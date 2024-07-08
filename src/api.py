import os
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
import logging
from flask_cors import CORS
from functools import lru_cache
import time
import datetime
from threading import Lock
import json


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Azure OpenAI settings
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_DEPLOYMENT_NAME = "pt_rekoncile"

# Serper API settings
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME, SERPER_API_KEY]):
    logger.error("Missing required environment variables")
    raise ValueError("Missing required environment variables")

try:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize AzureOpenAI client: {str(e)}")
    raise

def serper_search(query, num_results=5):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": num_results
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        logger.info(f"Sending search request to Serper API for query: {query}")
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        search_results = response.json()
        
        results = []
        if 'organic' in search_results:
            for result in search_results['organic'][:num_results]:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                results.append(f"{title}\nSnippet: {snippet}\nURL: {link}\n")
        
        logger.info(f"Serper API returned {len(results)} results for query: {query}")
        
        if not results:
            logger.warning(f"No results found for query: {query}")
            results.append("No relevant search results found. The AI will rely on its existing knowledge to answer the query.")
        
        return results

    except requests.exceptions.RequestException as e:
        logger.error(f"Serper API request failed: {str(e)}")
        return ["Search functionality is currently unavailable. The AI will rely on its existing knowledge to answer the query."]
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Serper API response: {str(e)}")
        return ["Error processing search results. The AI will rely on its existing knowledge to answer the query."]
    except Exception as e:
        logger.error(f"Unexpected error in Serper search: {str(e)}")
        return ["An unexpected error occurred during the search. The AI will rely on its existing knowledge to answer the query."]

def web_search(query, num_results=5):
    try:
        results = serper_search(query, num_results)
        if not results:
            logger.warning("Serper search returned no results")
            results = ["No search results available. Please rely on the AI's general knowledge."]
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        results = ["Search functionality is currently unavailable. Please rely on the AI's general knowledge."]
    return results

@app.route('/openai/deployments/<model_name>/chat/completions', methods=['POST'])
def chat_completions(model_name):
    app.logger.info(f"Received request for model: {model_name}")
    app.logger.info(f"Request data: {request.json}")
    try:
        data = request.json
        messages = data.get('messages', [])
        
        user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), None)
        if not user_message:
            logger.warning("No user message found in the request")
            return jsonify({"error": "No user message found"}), 400

        use_web_search = model_name.endswith('_online')
        actual_model_name = model_name.rsplit('_online', 1)[0] if use_web_search else model_name

        if use_web_search:
            app.logger.info(f"Performing web search for query: {user_message}")
            search_results = web_search(user_message)
            app.logger.info(f"Web search results: {search_results}")
            relevant_info = "\n".join(search_results)

            system_message = (
                "You are an advanced AI assistant with access to real-time web search capabilities. "
                "Your role is to provide accurate, up-to-date, and comprehensive answers to user queries "
                "based on the search results provided and your extensive knowledge base. "
                "Always prioritize information from the search results, but feel free to supplement "
                "with your general knowledge when appropriate. Provide well-structured, informative responses "
                "that directly address the user's question. If the search results don't provide enough information "
                "or seem irrelevant, state this clearly and offer the best answer you can based on your knowledge."
            )

            augmented_messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Query: {user_message}\nRelevant information from web search:\n{relevant_info}\n\nPlease answer the query based on this up-to-date information."}
            ]
        else:
            augmented_messages = messages

        completion = client.chat.completions.create(
            model=actual_model_name,
            messages=augmented_messages
        )
        
        # Format the response to match OpenAI API
        response = {
            "id": completion.id,
            "object": "chat.completion",
            "created": completion.created,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": completion.choices[0].message.content
                    },
                    "finish_reason": completion.choices[0].finish_reason
                }
            ],
            "usage": completion.usage.model_dump() if completion.usage else None
        }
        
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error in chat_completions: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working"}), 200

if __name__ == '__main__':
    app.run(debug=True)