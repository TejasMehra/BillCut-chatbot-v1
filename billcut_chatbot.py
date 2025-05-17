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
            st.error(f"Error retrieving API Key: {e}")
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
        The response text from the Gemini API.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_message = f"I encountered an error while processing your request: {e}"
        st.error(error_message)
        return error_message

def create_prompt(user_message):
    """
    Creates a highly structured prompt for the Gemini API, tailored for BillCut, with detailed information and controlled output.
    """
    prompt = f"""
    You are a helpful and informative chatbot for BillCut. BillCut is a fintech company that helps users manage their debt. 

    Here is detailed information about BillCut's services. Use this information to answer user questions.  Be concise. If the user asks for more details, offer them.

    BillCut helps refinance debt through its lending partners by paying off credit card or personal loans and converting them into EMIs.
    BillCut also offers debt settlement, helping to reduce outstanding loan or credit card dues by up to 50% for users facing recovery calls. This is not a loan service.
    BillCut doesn't charge fees, except for debt settlement, which has a ₹19 fee for a session with a financial advisor.
    Interest rates for refinancing vary from 12% to 19%.
    BillCut can convert multiple loans to a single loan, with users paying the NBFC directly.
    BillCut works in partnership with NBFCs to pay off loan amounts.
    NBFCs transfer funds directly to user bank accounts, except for balance transfers, which are handled via demand draft.
    The foreclosure charge is approximately 3% of the remaining amount.
    Refinancing does not negatively affect credit scores, but debt settlement will.
    BillCut asks for work emails only to verify employment and will not send emails to them.
    A demand draft is a prepaid bank slip that guarantees payment, safer than a cheque and cannot bounce.
    NBFCs provide loans and financial products but are not banks.
    The full form of NBFC is Non-Banking Financial Company.
    BillCut pays credit card bills by transferring funds to user accounts through lending partners, converting the amount to a low-interest EMI. Users must show proof of payment.

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
        st.session_state.messages = []

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
        full_prompt = create_prompt(prompt)
        response = get_gemini_response(full_prompt)

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        st.rerun()

if __name__ == "__main__":
    main()
