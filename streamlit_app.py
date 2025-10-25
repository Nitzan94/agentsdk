# ABOUTME: Streamlit web UI for Personal Assistant
# ABOUTME: Simple chat interface with session management

import streamlit as st
import asyncio
from agent.client import AssistantClient
import nest_asyncio
import os

# Add claude CLI to PATH (needed for Claude Agent SDK)
npm_bin = r"C:\Users\nitza\AppData\Roaming\npm"
if npm_bin not in os.environ["PATH"]:
    os.environ["PATH"] = npm_bin + os.pathsep + os.environ["PATH"]

# Allow nested event loops (needed for Streamlit)
nest_asyncio.apply()

st.set_page_config(page_title="Personal Assistant", page_icon="🤖", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "client" not in st.session_state:
    st.session_state.client = None

def initialize_client():
    """Initialize AssistantClient synchronously"""
    if st.session_state.client is None:
        async def _init():
            client = AssistantClient(session_id=st.session_state.session_id, resume=False)
            await client.initialize()
            st.session_state.session_id = client.session_id
            st.session_state.client = client
            return client

        return asyncio.run(_init())
    return st.session_state.client

# Sidebar
with st.sidebar:
    st.title("Personal Assistant")

    if st.session_state.session_id:
        st.success(f"Session: {st.session_state.session_id[:8]}...")

    if st.button("New Session"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.client = None
        st.rerun()

# Main chat area
st.title("🤖 Personal Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            client = initialize_client()

            async def get_response():
                response_text = ""
                async for response in client.send_message(prompt):
                    if hasattr(response, 'type'):
                        if response.type == 'text' or (hasattr(response, 'content') and isinstance(response.content, str)):
                            content = response.content if isinstance(response.content, str) else ""
                            response_text += content
                        elif hasattr(response, 'content') and isinstance(response.content, list):
                            for block in response.content:
                                if hasattr(block, 'text'):
                                    response_text += block.text
                return response_text

            full_response = asyncio.run(get_response())
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
