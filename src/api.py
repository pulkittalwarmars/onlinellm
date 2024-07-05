import os
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
import logging
from flask_cors import CORS

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

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME]):
    logger.error("Missing required Azure OpenAI environment variables")
    raise ValueError("Missing required Azure OpenAI environment variables")

try:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize AzureOpenAI client: {str(e)}")
    raise

def web_search(query, num_results=5):
    url = "https://html.duckduckgo.com/html/"
    params = {'q': query, 'kl': 'us-en'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.select('.result__body')[:num_results]:
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            
            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True)
                results.append(f"{title}: {snippet}")
        
        return results
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return []

@app.route('/openai/deployments/<model_name>/chat/completions', methods=['POST'])
def chat_completions(model_name):
    app.logger.info(f"Received request for model: {model_name}")
    app.logger.info(f"Request data: {request.json}")
    app.logger.debug(f"Request data: {request.json}")
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
