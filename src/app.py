## Lets use this space as the file output which is going to be tested
## Fow now import os and dotenv and load the parameters through there
## Will delete this for the final version

import os
import sys

from src.exception import CustomException
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.components.onlinellm import generate_chat_completion
from src.config import Config


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
limiter = Limiter(key_func=get_remote_address, app=app)

@app.route('/chat/completions', methods=['POST'])
@limiter.limit("10 per minute")
def chat_completions():
    data = request.json
    model = data.get('model')
    messages = data.get('messages', [])

    if model != Config.ONLINE_MODEL_ID:
        return jsonify({"error": "Invalid model ID"}), 400

    try:
        response = generate_chat_completion(messages)
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error in chat_completions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chat with AI</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                #chat-form { display: flex; margin-bottom: 20px; }
                #user-input { flex-grow: 1; padding: 10px; font-size: 16px; }
                button { padding: 10px 20px; font-size: 16px; }
                #response { border: 1px solid #ddd; padding: 20px; min-height: 100px; }
            </style>
        </head>
        <body>
            <h1>Chat with AI</h1>
            <form id="chat-form">
                <input type="text" id="user-input" placeholder="Enter your message">
                <button type="submit">Send</button>
            </form>
            <div id="response"></div>
            <script>
                document.getElementById('chat-form').onsubmit = function(e) {
                    e.preventDefault();
                    const userInput = document.getElementById('user-input');
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerText = 'Thinking...';
                    
                    fetch('/chat/completions', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            model: 'pt_rekoncile_online',
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


# try:
#   completion = client.chat.completions.create(
#       model="pt_rekoncile", ## TODO Update this with the final version once created
#       messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "What is the top news about Gen AI today? "}
#       ]
#   )

#   print(completion.choices[0].message)
# except Exception as e:
#   raise CustomException(e,sys)