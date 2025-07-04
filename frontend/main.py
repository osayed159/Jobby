import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from backend.cv_assistant import CVAssistant
from agent.agent import Agent

st.set_page_config(page_title="Jobby - AI Job Hunting Assistant", page_icon="💼", layout="centered")

st.title("Jobby")
st.markdown("""
Welcome to **Jobby**! 🚀

Your AI-powered assistant for job hunting, CV creation, and motivational letters.

---
""")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a feature:", ("Home", "CV Generator", "Job Search", "Motivational Letter (coming soon)"))

if page == "CV Generator":
    st.header("CV Generator")
    st.write("Let Gemini guide you step by step to create your CV.")

    st.subheader("Choose a CV Template")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folder = os.path.join(project_root, 'cv_templates')
    template_path = os.path.join(project_root, "cv_templates", "cv_template_structure.json")
    cv_assistant = CVAssistant(template_folder, template_path)

    if not os.path.exists(template_folder):
        st.error(f"Template folder not found: {template_folder}")
        st.stop()
    
    image_files, template_labels = cv_assistant.get_template_images()
    st.session_state.setdefault('selected_template', 0)

    cols = st.columns(3)
    for idx, (img, label) in enumerate(zip(image_files, template_labels)):
        col = cols[idx % 3]
        with col:
            border_color = "#4CAF50" if idx == st.session_state.selected_template else "#ccc"
            st.markdown(f"<div style='border: 3px solid {border_color}; border-radius: 10px; padding: 4px;'>", unsafe_allow_html=True)
            st.image(os.path.join(template_folder, img), caption=label, use_container_width=True)
            if st.button(label, key=f"select_{idx}"):
                st.session_state.selected_template = idx
            st.markdown("</div>", unsafe_allow_html=True)

    st.write(f"**Selected Template:** {template_labels[st.session_state.selected_template]}")

    # Initialize session state variables
    st.session_state.setdefault('cv_assistant_started', False)
    st.session_state.setdefault('cv_conversation', [])
    st.session_state.setdefault('last_gemini_response', None)
    st.session_state.setdefault('expecting_user_input', False)

    initial_prompt = cv_assistant.get_initial_prompt(st.session_state.selected_template)

    def get_conversation_prompt():
        prompt = initial_prompt + "\n\n"
        for turn in st.session_state.cv_conversation:
            if turn["role"] == "gemini":
                prompt += f"Gemini: {turn['content']}\n"
            else:
                prompt += f"User: {turn['content']}\n"
        return prompt

    if st.button("Start CV Assistant") or st.session_state.cv_assistant_started:
        st.session_state.cv_assistant_started = True
        
        if not st.session_state.cv_conversation:
            gemini_response = cv_assistant.get_gemini_response(initial_prompt)
            st.session_state.cv_conversation.append({"role": "gemini", "content": gemini_response})
            st.session_state.last_gemini_response = gemini_response
            st.session_state.expecting_user_input = True
        else:
            gemini_response = st.session_state.last_gemini_response
        
        st.markdown(f"**Jobby:** {gemini_response}")

        def process_user_answer():
            user_answer = st.session_state["user_answer"]
            if user_answer and st.session_state.expecting_user_input:
                st.session_state.cv_conversation.append({"role": "user", "content": user_answer})
                conversation_prompt = get_conversation_prompt()
                gemini_response = cv_assistant.get_gemini_response(conversation_prompt)
                
                # Clean up any fake user responses from the LLM
                gemini_response = cv_assistant.validate_gemini_response(gemini_response)
                st.session_state.cv_conversation.append({"role": "gemini", "content": gemini_response})
                st.session_state.last_gemini_response = gemini_response
                st.session_state["user_answer"] = ""
                st.session_state.expecting_user_input = True
                
                result_json = cv_assistant.parse_cv_json(gemini_response, st.session_state.selected_template)
                if result_json:
                    st.success("CV JSON with selected template:")
                    st.json(result_json)
                    st.session_state.expecting_user_input = False

        st.text_input("Your answer", key="user_answer")
        st.button("Send Answer", on_click=process_user_answer)

elif page == "Job Search":
    st.header("Job Search")
    
    # Create a form
    with st.form(key="job_form"):
        job_title = st.text_input("Enter Job Title")
        user_pref = st.text_area("Write your job preference for filtering")
        submit = st.form_submit_button(label="Submit")
        

    if submit:
        # Xing job scraping
        if user_pref:
            agent = Agent()
            agent.specifyWebsite("xing")
            xing_url = "https://www.xing.com/jobs/search?keywords=Werkstudent&location=Bonn&id=121067bff07394a5d92ce255fa4ee3a5&cityId=2946447.b8acbb&radius=100&careerLevel=1.795d28*2.24d1f6&sort=date&discipline=1011.6cf3f7*1007.b61d22*1022.ed6b40"
            xing_results = agent.xingFilteredJobs(xing_url, user_pref)
            st.write("Xing Jobs Matching Preference:")
            for r in xing_results:
                st.markdown(f"- [{r['url']}]({r['url']}) — {r['reason']}")
        
        agent = Agent()
        agent.specifyWebsite("linkedIn")
        agent.driver.insertJobTitle(job_title)
        agent.driver.getJobsPage()
        urls = agent.driver.getCompanyURLs()
        jobInfo = agent.driver.getJobInfo(urls)
        print(jobInfo)

else:
    st.info("Select an option from the sidebar to get started.")
