import google.generativeai as genai
import streamlit as st
import os

def get_api_key():
    """
    Retrieves the GOOGLE_API_KEY from Streamlit secrets or the environment.
    """
    try:
        # First, try to get it from Streamlit secrets (for cloud deployment)
        api_key = st.secrets["GOOGLE_API_KEY"]
        return api_key
    except KeyError:
        try:
            # If not found in secrets, try the environment (for local)
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Please set the GOOGLE_API_KEY environment variable or Streamlit secret."
                )
            return api_key
        except Exception as e:
            st.error(f"Error retrieving API Key: {e}") # use st.error
            return None  # Important: Return None in case of error

# Configuration
api_key = get_api_key()
if api_key: # Only configure if api_key was successfully retrieved
    genai.configure(api_key=api_key)
else:
    st.stop() # Stop if no API key is available


def get_gemini_response(prompt):
    """
    Generates a response from the Gemini API based on the given prompt.

    Args:
        prompt: The prompt message to send to the Gemini API.

    Returns:
        The response text from the Gemini API, or None on error.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def create_prompt(user_message):
    """
    Creates a prompt with Chain of Thought reasoning for BillCut.
    """
    prompt = f"""
    You are a chatbot named Sophie, a customer service representative for BillCut. 
    BillCut is a fintech company that helps users manage their debt. Your goal is to provide concise and accurate information.

    Here are some details about BillCut's services.  Use this information *exactly* as provided:

    -   **Refinancing:** BillCut helps refinance debt by paying off existing credit card or personal loans and converting them into Equated Monthly Installments (EMIs).
    -   **Debt Settlement:** BillCut assists users facing recovery calls by helping to reduce their outstanding loan or credit card dues by up to 50%.  This is *not* a loan service.
    -   **Fees:** BillCut does not charge any fees, except for debt settlement, which has a ₹19 fee for a session with a financial advisor.
    -   **Interest Rates:** Interest rates for refinancing vary from 12% to 19%.
    -   **Loan Consolidation:** BillCut can consolidate multiple loans into a single loan. Users make payments directly to the Non-Banking Financial Company (NBFC).
    -    **Loan Payment:** BillCut partners with NBFCs. The NBFCs pay off the user's loan amount.
    -   **Fund Disbursement:** NBFCs transfer funds directly to the user's bank account, except for balance transfers, which are handled via demand draft.

    -   **Credit Score Impact:** Refinancing does not negatively affect credit scores. Debt settlement *will* negatively affect credit scores.
    -   **Work Email:** BillCut asks for work emails only to verify employment. BillCut will not send any emails to the work email address.
    -   **Demand Draft:** A demand draft is a prepaid bank slip that guarantees payment. It is safer than a check and cannot bounce.
    -   **NBFCs:** Non-Banking Financial Companies (NBFCs) provide loans and other financial products but are not banks.
    -   **NBFC Full Form:** The full form of NBFC is Non-Banking Financial Company.
    -   **Credit Card Bill Payment:** BillCut pays the user's credit card bill by transferring funds to their account through its lending partners. The amount is converted into a low-interest EMI. The user must provide proof of payment for their credit card.

        When answering a user question, follow these guidelines:

        -   Be brief and professional.
        -   Only use the information provided above. Do not make up any details.
        -   If the user asks a question that cannot be answered from the provided information, respond with: "I'm sorry, I cannot answer that question with the information I have."
        -   Do not include any introductory phrases like "According to the provided information". Just answer the question.

        Here is an example of how to think step by step.

        User: What is BillCut?
        
        Let's think step by step. BillCut is a fintech company. BillCut helps users manage their debt through lending partners and offers debt settlement services.

        Here is the user's question: '{user_message}'
        """
    return prompt

def main():
    """
    Main function to run the Streamlit chatbot application.
    """
    st.title("BillCut Chatbot")
    st.write("Welcome to BillCut! Ask me anything about our services.")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you today?"}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Your question"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from Gemini
        full_prompt = create_prompt(prompt)  # Pass the user input
        response = get_gemini_response(prompt)

        # Handle response
        if response:
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            error_message = "I'm sorry, I encountered an error processing your request."
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            with st.chat_message("assistant"):
                st.markdown(error_message)
        st.rerun()

if __name__ == "__main__":
    main()