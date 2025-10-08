try:
    from flask import Flask, jsonify, request
    import json
    import os
    from datetime import datetime
except ImportError as e:
    # Fallback for missing imports
    def create_error_response():
        return f"Import Error: {str(e)}"

# Create Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    try:
        return jsonify({
            "status": "success",
            "message": "🚀 Enhanced Ultimate Squeeze Scanner v2.0 - WORKING!",
            "timestamp": datetime.now().isoformat(),
            "endpoints": [
                "/api/health",
                "/api/test"
            ]
        })
    except Exception as e:
        return f"Error in home route: {str(e)}", 500

@app.route('/api/health', methods=['GET'])
def health():
    try:
        return jsonify({
            "status": "healthy",
            "version": "2.0.0",
            "message": "Enhanced Ultimate Squeeze Scanner - Serverless Active",
            "timestamp": datetime.now().isoformat(),
            "python_version": "3.x",
            "deployment": "vercel_serverless"
        })
    except Exception as e:
        return f"Error in health route: {str(e)}", 500

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    try:
        method = request.method if request else "GET"
        return jsonify({
            "status": "test_success",
            "method": method,
            "message": "API endpoint is working correctly!",
            "ready_for_enhancement": True
        })
    except Exception as e:
        return f"Error in test route: {str(e)}", 500

# Catch-all route for debugging
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    try:
        return jsonify({
            "status": "catch_all",
            "path": path,
            "message": f"Path /{path} received",
            "available_endpoints": ["/", "/api/health", "/api/test"]
        })
    except Exception as e:
        return f"Error in catch-all: {str(e)}", 500

# Error handler
@app.errorhandler(500)
def handle_500(e):
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "error": str(e)
    }), 500

# For local testing
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
