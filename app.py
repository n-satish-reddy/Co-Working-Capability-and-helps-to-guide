import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from PIL import Image

# 1. Setup
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Co-Working", layout="wide")
st.title("Co-working And Helps To Guide")

# 2. Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []  # Start with an empty list

# 3. Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    option = st.radio("Input Method:", ("Text ", "Voice ", "Image "))
    if st.button(" Clear History"):
        st.session_state.messages = []
        st.rerun()

# 4. Display Existing Chat History (Before new inputs)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle New Inputs
user_query = None
if option == "Text ":
    user_query = st.chat_input("Ask a question...") # Modern chat input
elif option == "Voice ":
    user_query = st.audio_input("Record your question")
else:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), width=300)
        user_query = uploaded_file

# 6. Generate Response and Save to History
# Note: st.chat_input handles 'enter' automatically, others need a button
submit_button = st.button("Send Request") if option != "Text " else user_query

if submit_button:
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown("New Request Sent")

    with st.spinner('Gemini is thinking...'):
        try:
            content_parts = ["You are a Senior Developer. Reply helpfully."]
            
            # Format input based on type
            if option == "Image ":
                user_query.seek(0)
                content_parts.append(types.Part.from_bytes(data=user_query.read(), mime_type="image/jpeg"))
            elif option == "Voice ":
                content_parts.append(types.Part.from_bytes(data=user_query.read(), mime_type="audio/wav"))
            else:
                content_parts.append(user_query)

            # Get AI Response
            response = client.models.generate_content(model="gemini-2.5-flash", contents=content_parts)
            
            # SAVE TO HISTORY
            # We save both the user context (if text) and the AI response
            user_label = user_query if isinstance(user_query, str) else f"Sent a {option}"
            st.session_state.messages.append({"role": "user", "content": user_label})
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Refresh to show new messages in history
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")