## Lets use this space as the file output which is going to be tested
## Fow now import os and dotenv and load the parameters through there
## Will delete this for the final version

import os

from flask_cors import CORS
from flask import Flask, request, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.components.onlinellm import generate_chat_completion
from src.config import Config


app = Flask(__name__)
CORS(app)
limiter = Limiter(key_func=get_remote_address, app=app)

@app.route('/chat/completions', methods=['POST'])
@limiter.limit("10 per minute")
def chat_completions():
    data = request.json
    messages = data.get('messages', [])

    try:
        response = generate_chat_completion(messages)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Research Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                #chat-form { display: flex; margin-bottom: 20px; }
                #user-input { flex-grow: 1; padding: 10px; font-size: 16px; }
                button { padding: 10px 20px; font-size: 16px; }
                #response { border: 1px solid #ddd; padding: 20px; min-height: 100px; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h1>AI Research Assistant</h1>
            <p>Ask any question and get up-to-date information from the web and AI analysis.</p>
            <form id="chat-form">
                <input type="text" id="user-input" placeholder="Enter your question">
                <button type="submit">Search and Analyze</button>
            </form>
            <div id="response"></div>
            <script>
                document.getElementById('chat-form').onsubmit = function(e) {
                    e.preventDefault();
                    const userInput = document.getElementById('user-input');
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerText = 'Searching and analyzing...';
                    
                    fetch('/chat/completions', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            messages: [
                                {role: 'user', content: userInput.value}
                            ]
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            responseDiv.innerText = 'Error: ' + data.error;
                        } else {
                            responseDiv.innerText = data.choices[0].message.content;
                        }
                    })
                    .catch(error => {
                        responseDiv.innerText = 'Error: ' + error.message;
                    });
                    
                    userInput.value = '';
                };
            </script>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))