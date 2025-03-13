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
    },

    {
        "type": "function",
        "function": {
            "name": "generate",
            "description": "process an image for dress my garment tool by sending a http request to the url /api/v1/generate/generate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_url": {
                        "type": "string",
                        "description": "The base URL of the application to check (e.g., https://myapp.example.com)"
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