import os
import json
import requests
from openai import AzureOpenAI


from backend.environment import *
from backend.tools_fn import *
from backend.tools_definations import tools

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version
)


def process_user_input(user_input, conversation_history):
    """Process a single user input in the context of the conversation history"""
    # Add the new user message to the conversation history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Call the model with the conversation history and available functions
    response = client.chat.completions.create(
        model=deployment_name,
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"  # Let the model decide when to call the function
    )
    
    # Get the response message
    response_message = response.choices[0].message
    conversation_history.append(response_message)  # Add the response to the conversation
    
    # Check if the model wants to call a function
    if response_message.tool_calls:
        # Process all function calls
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            function_response = function_call_evaluator(
                function_name,
                function_args
            )
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
        conversation_history.append(final_message)
        
        return final_message.content
    else:
        # If no function call is requested, return the model's response directly
        return response_message.content

def run_conversational_interface():
    """Run an interactive conversation with the model"""
    # Initialize the conversation with a system message
    conversation_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    print("Welcome to the conversational AI. Type 'exit' to end the conversation.")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAssistant: Goodbye! Have a great day!")
            break
        
        try:
            # Process the user input and get the response
            assistant_response = process_user_input(user_input, conversation_history)
            
            # Display the assistant's response
            print(f"\nAssistant: {assistant_response}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            # Keep the conversation going despite errors
            conversation_history.append({"role": "assistant", "content": f"I encountered an error: {str(e)}"})

# Run the conversation
if __name__ == "__main__":
    try:
        run_conversational_interface()
    except KeyboardInterrupt:
        print("\n\nConversation ended by user.")
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {e}")