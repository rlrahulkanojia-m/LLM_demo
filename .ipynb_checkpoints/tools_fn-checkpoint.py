import json
import requests
import streamlit as st

from environment import SERVICE_URL

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

def check_app_health(app_url=SERVICE_URL, endpoint="/health", timeout=5):
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

def process_image(prompt, operation="generate"):
    """Process an image with text instructions and send to a specified endpoint"""
    # Get the current uploaded image from session state
    if 'current_uploaded_file' not in st.session_state or st.session_state.current_uploaded_file is None:
        return json.dumps({
            "success": False,
            "error": "No image is currently uploaded. Please upload an image first."
        })
    
    uploaded_file = st.session_state.current_uploaded_file
    
    # Use the global service URL if no endpoint is provided
    endpoint_url = f"{SERVICE_URL}/api/v1/generate/generate"
    
    try:
        # Prepare the image data
        file_bytes = uploaded_file.getvalue()
        # file_name = uploaded_file.name
        # file_type = uploaded_file.type
        data = {
            "mode":operation,
            "api_recipe_json_string":"{}",
            "image_base64": {{file_bytes}}
        }
        
        # Send the request
        response = requests.post(
            endpoint_url,
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

def function_call_evaluator(function_name, function_args ):
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
    elif function_name == "process_image":
        function_response = process_image(
            prompt=function_args.get("prompt"),
            endpoint_url=function_args.get("endpoint_url", ""),
            operation=function_args.get("operation", "custom")
        )
    else:
        function_response = json.dumps({"error": f"Unknown function: {function_name}"})

    return function_response