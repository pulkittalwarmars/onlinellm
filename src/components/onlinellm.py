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
    
    relevant_info = "\n".join([f"- {result['title']}: {result['snippet']}" for result in search_results])

    system_message = (
        "You are an advanced AI assistant with access to real-time web search capabilities. "
        "Your role is to provide accurate, up-to-date, and comprehensive answers to user queries "
        "based on the search results provided and your extensive knowledge base. "
        "Always prioritize information from the search results, but feel free to supplement "
        "with your general knowledge when appropriate. Provide well-structured, informative responses "
        "that directly address the user's question. If the search results don't provide enough information "
        "or seem irrelevant, state this clearly and offer the best answer you can based on your knowledge."
    )

    try:
        completion = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Query: {user_message}\nRelevant information:\n{relevant_info}"}
            ],
            temperature=0.7,
            max_tokens=800
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