import streamlit as st
import os
import json
import requests
from openai import AzureOpenAI
import base64

# Global configuration
SERVICE_URL = "http://154.42.3.13:27515"  # Global variable for the service URL

# Azure OpenAI configuration
api_key = "D3G1kjhWBkqLQU1kdHL02H31JvlQBiLOWKmkmg2kUSG4Zc02pl0CJQQJ99BCACHYHv6XJ3w3AAAAACOGSkPK"
azure_endpoint = "https://rahul-m86gj0lw-eastus2.openai.azure.com/"
deployment_name = "gpt-4o-modelia-rag"
api_version = "2024-05-01-preview"

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version
)

# Define the functions that the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_app_health",
            "description": "Check if the application is running by calling its health check endpoint",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_url": {
                        "type": "string",
                        "description": "The base URL of the application to check (e.g., https://myapp.example.com)"
                    },
                    "endpoint": {
                        "type": "string",
                        "description": "The health check endpoint path (default: /health)",
                        "default": "/health"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds for the health check request (default: 5)",
                        "default": 5
                    }
                },
                "required": ["app_url"]
            }
        }
    }
]

# Function implementations
def get_weather(location, unit="celsius"):
    """Simulated weather data retrieval function"""
    # This is a mock function - in a real app, you'd call a weather API
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "forecast": ["sunny", "windy"],
        "humidity": 60
    }
    return json.dumps(weather_data)

def check_app_health(app_url=None, endpoint="/health", timeout=5):
    """Check if an application is running by calling its health check endpoint"""
    # Use the global service URL if none is provided
    if app_url is None:
        app_url = SERVICE_URL
        
    try:
        # Form the complete health check URL
        health_url = f"{app_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Make the request to the health check endpoint
        response = requests.get(health_url, timeout=timeout)
        
        # Check if the request was successful
        if response.status_code >= 200 and response.status_code < 300:
            status = "healthy"
            message = "Application is running correctly"
        else:
            status = "unhealthy"
            message = f"Application returned status code {response.status_code}"
            
        # Try to parse response content if it's JSON
        try:
            details = response.json()
        except:
            details = {"raw_response": response.text[:500]}  # Limit the response size
            
        result = {
            "status": status,
            "message": message,
            "url": health_url,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "status_code": response.status_code,
            "details": details
        }
    except requests.exceptions.Timeout:
        result = {
            "status": "unhealthy",
            "message": f"Health check timed out after {timeout} seconds",
            "url": health_url
        }
    except requests.exceptions.ConnectionError:
        result = {
            "status": "unhealthy",
            "message": "Could not connect to the application",
            "url": health_url
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": f"Error checking application health: {str(e)}",
            "url": app_url
        }
        
    return json.dumps(result)

def process_image(prompt, endpoint_url="", operation="custom"):
    """Process an image with text instructions and send to a specified endpoint"""
    # Get the current uploaded image from session state
    if 'current_uploaded_file' not in st.session_state or st.session_state.current_uploaded_file is None:
        return json.dumps({
            "success": False,
            "error": "No image is currently uploaded. Please upload an image first."
        })
    
    uploaded_file = st.session_state.current_uploaded_file
    
    # Use the global service URL if no endpoint is provided
    if not endpoint_url:
        endpoint_url = f"{SERVICE_URL}/process-image"
    
    try:
        # Prepare the image data
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        file_type = uploaded_file.type
        
        # Prepare multipart form data
        files = {
            'image': (file_name, file_bytes, file_type)
        }
        
        data = {
            'prompt': prompt,
            'operation': operation
        }
        
        # Send the request
        response = requests.post(
            endpoint_url,
            files=files,
            data=data,
            timeout=30  # Longer timeout for image processing
        )
        
        # Process the response
        if response.status_code >= 200 and response.status_code < 300:
            try:
                result = response.json()
                result["success"] = True
                return json.dumps(result)
            except:
                # If response is not JSON, it might be the processed image itself
                if 'image' in response.headers.get('Content-Type', ''):
                    # Store the processed image in session state
                    st.session_state.processed_image = response.content
                    return json.dumps({
                        "success": True,
                        "message": "Image processed successfully.",
                        "content_type": response.headers.get('Content-Type'),
                        "operation": operation,
                        "prompt": prompt
                    })
                else:
                    return json.dumps({
                        "success": True,
                        "message": "Image processed successfully, but response format is unexpected.",
                        "raw_response": response.text[:500]
                    })
        else:
            return json.dumps({
                "success": False,
                "error": f"Image processing failed with status code {response.status_code}",
                "message": response.text[:500]
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error processing image: {str(e)}"
        })

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
    
/* Custom CSS to match the provided image design */
.stTextInput > div > div > input {
    background-color: white !important;
    border-radius: 30px !important;
    padding: 10px 20px !important;
    border: 1px solid #e0e0e0 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    color: #333 !important;
}

/* Make text visible in input fields */
input, textarea {
    color: #333 !important;
}

/* Button styling to match image */
.stButton > button {
    border-radius: 30px !important;
    background-color: white !important;
    color: #555 !important;
    border: 1px solid #e0e0e0 !important;
    padding: 10px 20px !important;
    font-size: 0.9rem !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    margin: 5px !important;
}

/* Form buttons */
.stForm [data-testid="stForm"] {
    border-color: transparent !important;
}

button[kind="formSubmit"] {
    border-radius: 30px !important;
    background-color: #6c5ce7 !important;
    color: white !important;
    border: none !important;
    font-weight: bold !important;
}

/* Button hover state */
.stButton > button:hover {
    background-color: #f9f9f9 !important;
    border-color: #d0d0d0 !important;
}

/* File uploader styling */
.stFileUploader > div > button {
    border-radius: 30px !important;
    background-color: white !important;
    color: #555 !important;
    border: 1px solid #e0e0e0 !important;
}

/* Message container styling */
.chat-message {
    padding: 15px !important;
    border-radius: 15px !important;
    margin-bottom: 10px !important;
    display: flex !important;
    flex-direction: column !important;
    max-width: 80% !important;
}

/* User message styling */
.user-message {
    background-color: #e1f5fe !important;
    border-bottom-right-radius: 0 !important;
    align-self: flex-end !important;
    margin-left: auto !important;
}

/* Assistant message styling */
.assistant-message {
    background-color: #f5f5f5 !important;
    border-bottom-left-radius: 0 !important;
    align-self: flex-start !important;
    margin-right: auto !important;
}

/* Container for action buttons */
.action-buttons {
    display: flex !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}

/* Main content area */
.main-content {
    background-color: white !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    margin: 20px 0 !important;
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

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # App header with gradient text
    st.markdown('<div class="logo-title"><span class="gradient-text">modelia</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">How can I help you today?</div>', unsafe_allow_html=True)
    
    # Initialize conversation history in session state if it doesn't exist
    if 'conversation' not in st.session_state:
        st.session_state.conversation = [
            {"role": "system", "content": "You are a helpful assistant that can answer questions, check application health, and get weather information."}
        ]
    
    # Initialize show_image_upload flag in session state if it doesn't exist
    if 'show_image_upload' not in st.session_state:
        st.session_state.show_image_upload = False
        
    # Initialize current_uploaded_file in session state if it doesn't exist
    if 'current_uploaded_file' not in st.session_state:
        st.session_state.current_uploaded_file = None
    
    # Main content area
    with st.container():
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Toggle for image operations
        show_image_tools = st.checkbox("Show image tools", value=st.session_state.show_image_upload)
        
        # Update session state based on checkbox
        if show_image_tools != st.session_state.show_image_upload:
            st.session_state.show_image_upload = show_image_tools
            # Force a rerun to update UI
            st.rerun()
        
        # Only show image upload and related tools if enabled
        if st.session_state.show_image_upload:
            # File upload section
            st.markdown("Let's enhance your images", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("+ Attach", type=["jpg", "jpeg", "png"])
            
            # Store the uploaded file in session state
            if uploaded_file:
                st.session_state.current_uploaded_file = uploaded_file
                
                # Show the image preview
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                
            # Show processed image if available
            if 'processed_image' in st.session_state and st.session_state.processed_image is not None:
                st.image(st.session_state.processed_image, caption="Processed Image", use_column_width=True)
            
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
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
        user_input = st.text_input("Type your message...", key="user_input")
        submit_button = st.form_submit_button("Send")
    
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