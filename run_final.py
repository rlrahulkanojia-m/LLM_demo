import streamlit as st
import json
from openai import AzureOpenAI
import base64

from environment import *
from tools_fn import *
from tools_definations import tools
from utils import *

add_bg_image('background.jpg')


# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version
)

def process_user_input(user_input, conversation_history, uploaded_file=None):
    """Process a single user input in the context of the conversation history"""
    # Prepare the message content based on whether a file was uploaded
    message_content = user_input
    
    # If there's a file, create a message with both text and image
    if uploaded_file is not None:
        # Convert the file to base64
        file_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        # Create a message with both text and image
        message_content = [
            {"type": "text", "text": user_input},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/{uploaded_file.type.split('/')[1]};base64,{base64_image}"}
            }
        ]
    
    # Add the new user message to the conversation history
    if isinstance(message_content, list):
        conversation_history.append({"role": "user", "content": message_content})
    else:
        conversation_history.append({"role": "user", "content": message_content})
    
    # Call the model with the conversation history and available functions
    response = client.chat.completions.create(
        model=deployment_name,
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"  # Let the model decide when to call the function
    )
    
    # Get the response message
    response_message = response.choices[0].message
    
    # Extract the content attribute directly
    response_content = response_message.content
    
    # Check if the model wants to call a function
    if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
        # Add the assistant's message with tool_calls to the conversation history
        conversation_history.append({
            "role": "assistant",
            "content": response_content if response_content else "",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in response_message.tool_calls
            ]
        })
        
        # Process all function calls
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the function (using the function name to determine which function to call)
            if function_name == "get_weather":
                function_response = get_weather(
                    location=function_args.get("location"),
                    unit=function_args.get("unit", "celsius")
                )
            elif function_name == "check_app_health":
                function_response = check_app_health(
                    app_url=function_args.get("app_url"),
                    endpoint=function_args.get("endpoint", "/health"),
                    timeout=function_args.get("timeout", 5)
                )
            else:
                function_response = json.dumps({"error": f"Unknown function: {function_name}"})
            
            # Add the function response to the conversation history
            conversation_history.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
        
        # Call the model again with the function responses
        second_response = client.chat.completions.create(
            model=deployment_name,
            messages=conversation_history
        )
        
        # Add the final response to the conversation history
        final_message = second_response.choices[0].message
        # Extract the content attribute directly
        final_content = final_message.content
        conversation_history.append({"role": "assistant", "content": final_content if final_content else ""})
        
        return final_content if final_content else ""
    else:
        # If no function call is requested, add the assistant's response to conversation history
        conversation_history.append({"role": "assistant", "content": response_content if response_content else ""})
        # Return the model's response directly
        return response_content if response_content else ""

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # App header with gradient text
    st.markdown('<div class="logo-title"><span class="gradient-text">Modelia AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">How can I help you today?</div>', unsafe_allow_html=True)
    
    # Initialize conversation history in session state if it doesn't exist
    if 'conversation' not in st.session_state:
        st.session_state.conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Welcome to Modelia AI! I'm here to help with your fashion automation needs. How can I assist you today?"}
        ]
    
    # Initialize show_image_upload flag in session state if it doesn't exist
    if 'show_image_upload' not in st.session_state:
        st.session_state.show_image_upload = False
        
    # Initialize current_uploaded_file in session state if it doesn't exist
    if 'current_uploaded_file' not in st.session_state:
        st.session_state.current_uploaded_file = None
    
    # Main content area
    # with st.container():
        # st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        ## Toggle for image operations
        # show_image_tools = st.checkbox("Show image tools", value=st.session_state.show_image_upload)
        
        ## Update session state based on checkbox
        # if show_image_tools != st.session_state.show_image_upload:
        #     st.session_state.show_image_upload = show_image_tools
        #     # Force a rerun to update UI
        #     st.rerun()
        
        # # Only show image upload and related tools if enabled
        # if st.session_state.show_image_upload:
        #     # File upload section
        #     st.markdown("Let's enhance your images", unsafe_allow_html=True)
        #     uploaded_file = st.file_uploader("+ Attach", type=["jpg", "jpeg", "png"])
            
        #     # Store the uploaded file in session state
        #     if uploaded_file:
        #         st.session_state.current_uploaded_file = uploaded_file
                
        #         # Show the image preview
        #         st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                
        #     # Show processed image if available
        #     if 'processed_image' in st.session_state and st.session_state.processed_image is not None:
        #         st.image(st.session_state.processed_image, caption="Processed Image", use_column_width=True)
            
            # Action buttons (displayed but not functional for now)
            # st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
            # col1, col2, col3, col4, col5 = st.columns(5)
            
            # with col1:
            #     st.button("Modify to model", disabled=True)
            # with col2:
            #     st.button("Change person", disabled=True)
            # with col3:
            #     st.button("Change background", disabled=True)
            # with col4:
            #     st.button("Remove wrinkles", disabled=True)
            # with col5:
            #     st.button("Enhance", disabled=True)
                
            # st.markdown('</div>', unsafe_allow_html=True)
        
        # st.markdown('</div>', unsafe_allow_html=True)
    
    # Display conversation history
    for message in st.session_state.conversation:
        if message["role"] != "system":  # Don't display system messages
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    # Handle messages with text and image
                    for content_part in message["content"]:
                        if content_part["type"] == "text":
                            st.markdown(f'<div class="chat-message user-message">{content_part["text"]}</div>', unsafe_allow_html=True)
                        elif content_part["type"] == "image_url":
                            st.image(content_part["image_url"]["url"].split(",")[1], caption="Uploaded Image")
                else:
                    st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
            elif message["role"] == "assistant":
                st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # User input
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("", key="user_input")
        submit_button = st.form_submit_button("Send", use_container_width=True, icon=":material/send:")
    
    # Process user input when form is submitted
    if submit_button and user_input:
        try:
            # Get uploaded file from session state if available
            uploaded_file = None
            if st.session_state.show_image_upload and 'current_uploaded_file' in st.session_state:
                uploaded_file = st.session_state.current_uploaded_file
                
            # Process user input and get response
            assistant_response = process_user_input(user_input, st.session_state.conversation, uploaded_file)
            
            # Force a rerun to display the updated conversation
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Add error message to conversation
            st.session_state.conversation.append({"role": "assistant", "content": f"I encountered an error: {str(e)}"})

if __name__ == "__main__":
    main()
