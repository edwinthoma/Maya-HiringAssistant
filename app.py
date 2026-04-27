#Main Stremalit application file
#It builds the UI and connects the conversation engine to the interface

import streamlit as st
from maya import (
    initialize_session,
    get_opening_greeting,
    get_maya_response,
    update_candidate_info,
    check_info_complete,
    start_interview,
    handle_answer_and_next
)
# --- PAGE CONFIGURATION ---
# Sets the browser tab title and page layout
st.set_page_config(
    page_title="Maya | TalentScout Hiring Assistant",
    layout="centered"
)

# HEADER 
st.title("Maya")
st.caption("TalentScout Hiring Assistant — Powered by AI")
st.divider()

# INITIALIZE SESSION STATE
# This sets up all session variables on first load
initialize_session()

#Dispaly Conversation History 
#Loop through all messages in history and render them as chat bubbles 
#We skip the first messafge (index 0) as its the system prompt
# We also skip any messages with role "system" injected mid-conversation

for message in st.session_state.messages[1:]:
    if message["role"]=="system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        
#Starting the chat 
#if theres only system prompt in history trigger greeting automatically without user input
if len(st.session_state.messages)==1:
    with st.chat_message("assistant"):
        greeting= get_opening_greeting()
        st.markdown(greeting)
        
#User Input 
#st.chat renders the text box at the bottom of the screen 
user_input=st.chat_input(
    placeholder="Type your message here...",
    disabled=st.session_state.conversation_ended
)

#Handle user input
if user_input:
    #Display user messege immediately
    with st.chat_message("user"):
        st.markdown(user_input)
        
    #Route to correct handler based on current phase
    #Phase: Gathering info    
    if st.session_state.phase=="gathering":
        
        with st.chat_message("assistant"):
            #loading indicator
            with st.spinner("Maya is typing..."):
                response=get_maya_response(user_input)
            st.markdown(response)
            
        #Extracting info in bg after every gather message    
        with st.spinner(""):
            update_candidate_info()
           
        # Check if all 7 fields are now complete
        if check_info_complete() and not st.session_state.questions_generated:
            st.session_state.phase = "questioning"
            st.rerun()
                
    # Phase: questioning — save answer, move to next question
    elif st.session_state.phase == "questioning":

        if not st.session_state.questions_generated:
            with st.chat_message("assistant"):
                with st.spinner("Maya is preparing your interview..."):
                    interview_start = start_interview()
                st.markdown(interview_start)

        else:
            # Questions already generated — candidate is answering them
            with st.chat_message("assistant"):
                with st.spinner("Maya is typing..."):
                    response = handle_answer_and_next(user_input)
                st.markdown(response)

    # Phase: ended — conversation is over
    #This wont execute but its here as safety net
    else:
        pass           
#CONVERSATION ENDED STATE
if st.session_state.conversation_ended:

    # Restart button — clears all session state and reruns the app
    # st.rerun() tells Streamlit to immediately rerun the script from scratch
    if st.button("Start New Session"):
        # Clear every key from session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Rerun the app — initialize_session() will rebuild everything fresh
        st.rerun()
        