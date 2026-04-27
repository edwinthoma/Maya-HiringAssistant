#Main Stremalit application file
#It builds the UI and connects the conversation engine to the interface

import streamlit as st
from maya import initialize_session,get_maya_response

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

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        
#Starting the chat 
#if theres only system prompt in history trigger greeting automatically without user input
if len(st.session_state.messages)==1:
    with st.chat_message("assistant"):
        greeting= get_maya_response(
            "Begin the conversation with your greeting message"
        )
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
        
        

    with st.chat_message("assistant"):
        #loading indicator
        with st.spinner("Maya is typing..."):
            response=get_maya_response(user_input)
        st.markdown(response)
     
#CONVERSATION ENDED STATE
if st.session_state.conversation_ended:
    st.info(
        "This screening session has ended. "
        "Thank you for your time!"
    )

    # Restart button — clears all session state and reruns the app
    # st.rerun() tells Streamlit to immediately rerun the script from scratch
    if st.button("Start New Session"):
        # Clear every key from session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Rerun the app — initialize_session() will rebuild everything fresh
        st.rerun()