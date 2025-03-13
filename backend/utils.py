import streamlit as st

# Custom CSS to match the provided image design
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main logo and title styling */
    .logo-title {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Gradient text for logo */
    .gradient-text {
        background: linear-gradient(90deg, #d16ba5, #86a8e7, #5ffbf1);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 4rem;
        font-weight: bold;
        font-family: 'Arial', sans-serif;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Chat input area styling */
    .stTextInput > div > div > input {
        background-color: white;
        border-radius: 30px;
        padding: 10px 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Button styling to match image */
    .stButton > button {
        border-radius: 30px;
        background-color: white;
        color: #555;
        border: 1px solid #e0e0e0;
        padding: 10px 20px;
        font-size: 0.9rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin: 5px;
    }
    
    /* Button hover state */
    .stButton > button:hover {
        background-color: #f9f9f9;
        border-color: #d0d0d0;
    }
    
    /* File uploader styling */
    .stFileUploader > div > button {
        border-radius: 30px;
        background-color: white;
        color: #555;
        border: 1px solid #e0e0e0;
    }
    
    /* Message container styling */
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        max-width: 80%;
    }
    
    /* User message styling */
    .user-message {
        background-color: #e1f5fe;
        border-bottom-right-radius: 0;
        align-self: flex-end;
        margin-left: auto;
    }
    
    /* Assistant message styling */
    .assistant-message {
        background-color: #f5f5f5;
        border-bottom-left-radius: 0;
        align-self: flex-start;
        margin-right: auto;
    }
    
    /* Container for action buttons */
    .action-buttons {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    /* Main content area */
    .main-content {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    /* Remove default Streamlit padding */
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Full width layout */
    .reportview-container {
        width: 100%;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
