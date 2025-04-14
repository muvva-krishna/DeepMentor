import streamlit as st
import os
import time
from codegen import AnimationGenerator
from manim_runner import run_manim
from retriever import handle_query

# Initialize both tools


# Set Streamlit page config
st.set_page_config(page_title="Study & Animate 🤖🎓", page_icon="🧠")
st.title("🧠DeepMentor")

# Session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat-like user input
user_input = st.chat_input("Ask a question or enter a math concept...")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Helper to wait for video file


# If user enters input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        studybot_response = handle_query(user_input, session_id="streamlit_session")
        st.markdown(studybot_response,unsafe_allow_html=True)

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": studybot_response})
    animation_generator = AnimationGenerator(api_key=os.environ.get("GROQ_API_KEY"))
    def wait_for_file(file_path, timeout=10):
        for _ in range(timeout * 10):
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return True
            time.sleep(0.1)
        return False

    # Proceed to animation generation only if StudyBot provided a valid response
    if studybot_response and "No valid answer" not in studybot_response:
        with st.chat_message("assistant"):
            with st.spinner("🎬 Generating animation plan and code..."):
                animation_plan, final_code = animation_generator.generate_final_manim_code(studybot_response)
            print(animation_plan)
            print(final_code)

        # Render video
        with st.chat_message("assistant"):
            with st.spinner("🎞️ Rendering Manim animation..."):
                video_path = run_manim(final_code)

            if video_path and wait_for_file(video_path):
                st.success("✅ Animation generated!")
                st.video(video_path)
            else:
                st.error("❌ Failed to render animation or video file not found.")



