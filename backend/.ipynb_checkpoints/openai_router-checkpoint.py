import os
from pydoc import cli  
import openai
from openai import AzureOpenAI  

# Azure OpenAI configuration
api_key = "D3G1kjhWBkqLQU1kdHL02H31JvlQBiLOWKmkmg2kUSG4Zc02pl0CJQQJ99BCACHYHv6XJ3w3AAAAACOGSkPK"  # Store key in environment variable for security
azure_endpoint = "https://rahul-m86gj0lw-eastus2.openai.azure.com/"  # e.g., "https://your-resource-name.openai.azure.com/"
deployment_name = "gpt-4o-modelia-rag"  # The deployment name you chose for your model
api_version = "2024-05-01-preview"  # Use the latest API version that supports function calling

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version
)

print(vars(client))
response = client.chat.completions.create(
    model = "deployment_name".
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "Who were the founders of Microsoft?"}
    ]
)

#print(response)
print(response.model_dump_json(indent=2))
print(response.choices[0].message.content)