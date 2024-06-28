# TODO use flask 

import os
import sys
import uuid
import time
# from dotenv import load_dotenv
from openai import AzureOpenAI
from src.exception import CustomException
from src.utils import web_search
from src.config import Config


# load_dotenv() 

# Set up client API
client = AzureOpenAI(azure_endpoint=os.getenv("AZURE_ENDPOINT"),
                     api_version="2024-02-01",
                     api_key=os.getenv("OPENAI_API_KEY"))


def generate_chat_completion(messages):
    user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), None)
    if not user_message:
        raise ValueError("No user message found")

    search_results = web_search(user_message)
    
    # Filter out advertisements and extract relevant information
    relevant_results = [result for result in search_results if not result['title'].endswith('Ad')]
    
    if relevant_results:
        relevant_info = relevant_results[0]['snippet']
    else:
        relevant_info = "No relevant information found."

    system_message = (
        "You are a helpful assistant with access to information about Central Park in New York. "
        "Use the provided search results to answer the user's query about main attractions in Central Park. "
        "If the information is not directly related to the main attractions, provide a general response about Central Park "
        "and suggest that the user check official websites or guides for more specific information."
    )

    try:
        completion = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Query: {user_message}\nRelevant information: {relevant_info}"}
            ]
        )
        gpt4_response = completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error in GPT-4 API call: {str(e)}")

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": Config.ONLINE_MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": gpt4_response
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }