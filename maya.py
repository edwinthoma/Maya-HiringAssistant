#This File contains the core conversation engine for Maya
from openai import OpenAI
from prompts import SYSTEM_PROMPT
import streamlit as st
import os 
from dotenv import load_dotenv

load_dotenv()

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def initialize_session():
    #We start with the system prompt so maya knows her role
    if "messages" not in st.session_state:
        st.session_state.messages=[
            {"role":"system","content":SYSTEM_PROMPT} 
        ]
    #Structured Storage for candidate info w extract during conversation
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info={
            "name":None,
            "email":None,
            "phone_number":None,
            "experience":None,
            "position":None,
            "location":None,
            "tech_stack":None
        }
    #tracks which phase the conversation is currently in (greeting,gathering,questioning,closing)
    if "phase" not in st.session_state:
        st.session_state.phase="greeting"
    
    #Flag to disable input once onversation has ended 
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended= False
        
def get_maya_response(user_input:str)->str:
    """Takes the user's message ,appends it to history
        sends the full history to LLM and return Maya's response.
        
        We send the full history everytime as openai 
        has no memory between calls.
        Only by sending the entire conversation history 
        Maya gets the context"""
        
    #Check for conversation ending keywords before calling the API
    exit_keywords=["exit","bye","quit"]
    if user_input.lower().strip() in exit_keywords:
        st.session_state.conversation_ended=True
        
    #Append the users message to the conversation history    
    st.session_state.messages.append({
        "role":"user",
        "content":user_input
    })
    
    #Send the entire conversation history to  OpenAI            
    response=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=0.5,
        max_tokens=500
    )
    
    #Extract Maya's reply from the response object
    maya_reply=response.choices[0].message.content
    
    #Append Maya's reply to history so future calls include it 
    st.session_state.messages.append({
        "role":"assistant",
        "content":maya_reply
    })
    
    return maya_reply