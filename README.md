# AI-Powered Web Search Assistant

Welcome to the Online LLM project starter Pack. This tool uses the poor man's search engine to give you a summary of the question you want know about, this is done through an AI-powered web search assistant using Azure OpenAI and Flask. It combines real-time web search capabilities with advanced language models to provide up-to-date and comprehensive responses to user queries.

## Prerequisites

- Python 3.11+
- Azure OpenAI account and API key
- Flask
- Various Python libraries (see requirements.txt)

## Features

- Integration with Azure OpenAI for natural language processing
- Real-time web search functionality using DuckDuckGo
- Flexible API that can operate with or without web search capabilities
- Deployment on Azure Web Services for easy access and scalability


## Setup and Deployment

1. Clone the repository to your local machine or Azure development environment.

2. Ensure all required packages are listed in `requirements.txt`.

3. Set up the following environment variables in your Azure Web Service configuration:
   - AZURE_OPENAI_ENDPOINT
   - AZURE_OPENAI_API_KEY
   - AZURE_OPENAI_API_VERSION

4. Deploy the application to Azure Web Services using your preferred method (e.g., Azure CLI, Azure Portal, or GitHub Actions).

5. After deployment, the API will be accessible at your Azure Web Service URL.

## Usage

To interact with the AI assistant:

1. Use code provided below to create a test_api.py script to test the deployment:

Python
```
from openai import AzureOpenAI
import logging

logging.basicConfig(level=logging.DEBUG)

client = AzureOpenAI(
    azure_endpoint="https://pt-onlinellm2.azurewebsites.net",
    api_key="<API_KEY>",
    api_version="2024-02-01"
)

try:
    completion = client.chat.completions.create(
        model="pt_rekoncile_onlinellm",  # Add '_onlinellm' to trigger web search
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the cricket world cup in 2024?"}
        ]
    )
    print(f"Full response: {completion}")
    print(f"Content: {completion.choices[0].message.content}")
except Exception as e:
    logging.error(f"An error occurred: {str(e)}", exc_info=True)
```

2. Update the azure_endpoint in test_api.py with your Azure Web Service URL.

3. Run the script: test_api.py
