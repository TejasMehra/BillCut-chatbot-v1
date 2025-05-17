import google.generativeai as genai
import streamlit as st
import os

def get_api_key():
    """
    Retrieves the GOOGLE_API_KEY, prioritizing Streamlit secrets for cloud deployment.
    """
    try:
        # 1. Try to get the API key from Streamlit secrets (for Streamlit Cloud)
        api_key = st.secrets["GOOGLE_API_KEY"]  
        return api_key  # Return the key if found in secrets
    except KeyError:
        # 2. If not found in Streamlit secrets, try the environment variable (for local)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("Please set the GOOGLE_API_KEY environment variable or Streamlit secret.")
            st.stop()  # Stop execution if the key is missing
        return api_key # Return the key if found in environment
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()
        return None

# Get and configure the API key
api_key = get_api_key()  # Call the function to get the key
if api_key:
    genai.configure(api_key=api_key)  # Configure Gemini if a key was found
else:
    st.stop() # Stop if no API key


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
    Creates a custom prompt for the Gemini API, tailored for BillCut, a debt refinancing startup.

    Args:
        user_message: The user's input message.

    Returns:
        A formatted prompt string to be used with the Gemini API.
    """
    prompt = f"""You are Sophie, a helpful and informative chatbot for BillCut. 
BillCut is a fintech company that helps users refinance their debt through its lending partners and offers debt settlement services. 

Here is some information about BillCut that you should use to answer the user's questions.  Be concise and professional.

* **Refinancing:** BillCut helps refinance debt by paying off credit card or personal loans and converting them into EMIs.
* **Debt Settlement:** BillCut helps reduce outstanding loan or credit card dues by up to 50% for users facing recovery calls. This is not a loan service.
* **Fees:** BillCut doesn't charge any fees, except for debt settlement, which has a ₹19 fee for a session with our financial advisor.
* **Interest Rates:** The interest rates charged can vary from 12% to 19%.
* **Loan Consolidation:** BillCut can help convert multiple loans into a single loan, and the user pays the NBFC directly.
* **Loan Payment:** BillCut works in partnership with NBFCs.  The NBFCs pay off the user's loan amount.
* **Fund Disbursement:** The NBFC transfers funds directly to your bank account, except for balance transfers, which are done via demand draft.
* **Foreclosure Charges:** The foreclosure charge is approximately 3% of the remaining amount.
* **Credit Score Impact:** Refinancing does not negatively affect credit scores. Debt settlement will affect credit scores negatively.
* **Work Email:** BillCut asks for work emails only to verify employment; it won't send any emails to the work email.
* **Demand Draft:** A demand draft is a prepaid bank slip that guarantees payment, is safer than a cheque, and can't bounce.
* **NBFCs:** Non-Banking Financial Companies (NBFCs) give loans and financial products but are not banks.
* **NBFC Full Form:** The full form of NBFC is Non-Banking Financial Company.
* **Credit Card Bill Payment:** BillCut pays your credit card bill by transferring funds to your account through its lending partners. The amount is converted into a low-interest EMI. The user must show proof of payment for your credit card.

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