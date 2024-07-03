## Here we will bring it all together and host it in a REST API
import os
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI

app = Flask(__name__)

AZURE_OPENAI_ENDPOINT = os.environ['AZURE_OPENAI_ENDPOINT']
AZURE_OPENAI_API_KEY = os.environ['AZURE_OPENAI_API_KEY']
AZURE_OPENAI_API_VERSION = os.environ['AZURE_OPENAI_API_VERSION']
ONLINE_MODEL_ID = os.environ['ONLINE_MODEL_ID']

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_OPENAI_API_KEY
)

## Load in the function for websearching
## TODO Test quality of responses upon changing num_results

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
        print(f"Error in web search: {e}")
        return []
    

@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])
    
    user_message = next((msg['content'] for msg in messages if msg['role'] == 'user'), None)
    if not user_message:
        return jsonify({"error": "No user message found"}), 400

    search_results = web_search(user_message)
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

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Query: {user_message}\nRelevant information:\n{relevant_info}"}
    ]

    try:
        completion = client.chat.completions.create(
            model=ONLINE_MODEL_ID,
            messages=messages
        )
        return jsonify(completion.model_dump())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()