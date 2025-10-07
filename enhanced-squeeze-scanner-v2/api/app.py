from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from .index import handler

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../static', path)

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_handler(path):
    # Create a mock request object for the handler
    class MockRequest:
        def __init__(self):
            self.url = f'/api/{path}'
            self.method = request.method
            self.headers = dict(request.headers)
            self.body = request.get_data(as_text=True) if request.method in ['POST', 'PUT'] else None
    
    mock_req = MockRequest()
    
    # Call the original handler
    response = handler(mock_req, None)
    
    # Parse and return the response
    if isinstance(response, dict):
        return jsonify(response), response.get('statusCode', 200)
    return response

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)