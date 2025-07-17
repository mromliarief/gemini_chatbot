import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hai! Saya adalah chatbot Gemini. Ada yang bisa saya bantu?"
        }
    ]

# Set up Streamlit UI
st.title("💬 Chatbot dengan Gemini")
st.caption("Aplikasi chatbot berbasis LLM Gemini oleh Google AI")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
    # Validate input
    if not prompt.strip():
        st.warning("Silakan masukkan pertanyaan yang valid")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Stream the response
            response = model.generate_content(
                {"role": "user", "parts": [{"text": prompt}]},
                stream=True
            )

            for chunk in response:
                # Handle different response formats
                chunk_text = ""
                if hasattr(chunk, 'text'):
                    chunk_text = chunk.text
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text'):
                            chunk_text += part.text

                if chunk_text:
                    full_response += chunk_text
                    message_placeholder.markdown(full_response + "▌")

            if not full_response.strip():
                raise ValueError("Empty response from model")

            message_placeholder.markdown(full_response)

            # Add to history only if we got valid response
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except Exception as e:
            error_msg = f"Maaf, terjadi error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg})
