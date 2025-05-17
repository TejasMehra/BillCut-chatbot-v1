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
    Creates a highly structured prompt for the Gemini API, tailored for BillCut, with detailed information.
    """
    prompt = f"""
    You are Sophie, a helpful and informative chatbot for BillCut. BillCut is a fintech company that helps users manage their debt.

    Here is detailed information about BillCut's services. Use this information to answer user questions thoroughly.

    BillCut helps refinance your debt through its lending partners. For example, BillCut can pay off your credit card or personal loan and convert it into EMIs.
    BillCut also offers debt settlement, where we help reduce your outstanding loans or credit card dues by up to 50% if you're facing recovery calls. Note: This is not a loan service.
    BillCut doesn't charge any fees, except for debt settlement, which has a ₹19 fee for a session with a financial advisor.
    The interest rates charged can vary from 12% to 19%.
    With the help of BillCut, you can convert multiple loans to a single loan and pay the NBFC directly.
    BillCut works in partnership with NBFCs. With the help of NBFCs, BillCut will pay off your loan amount.
    The NBFC transfers funds directly to your bank account, except for balance transfers, which are done via demand draft.
    The foreclosure charge is approximately 3 percent of the remaining amount.
    Refinancing does not negatively affect your credit score. However, debt settlement will affect your credit score negatively.
    BillCut asks for your work email only to verify your employment. BillCut won't send any emails to it.
    A demand draft is a prepaid bank slip that guarantees payment, is safer than a cheque, and can't bounce.
    NBFCs give loans and financial products, but they're not banks.
    The full form of NBFC is Non-Banking Financial Company.
    BillCut pays your credit card bill by transferring funds to your account through its lending partners. The amount is converted into a low-interest EMI. You must show proof of payment for your credit card.

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
        full_prompt = create_prompt(prompt)
        response = get_gemini_response(full_prompt)

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        st.rerun()

if __name__ == "__main__":
    main()
