# app.py - Render.com Version
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure API key from environment variable
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY environment variable not set!")
else:
    print("✅ API key loaded successfully")

genai.configure(api_key=API_KEY)

# Initialize the model
model = None
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini model initialized successfully")
except Exception as e:
    print(f"❌ Model initialization error: {e}")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Flutter-Python AI API is running on Render! 🚀',
        'status': 'healthy',
        'model_available': model is not None,
        'endpoints': {
            'health': '/health (GET)',
            'process_text': '/process_text (POST)'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_available': model is not None,
        'platform': 'Render.com',
        'message': 'All systems operational!'
    })

@app.route('/process_text', methods=['POST', 'OPTIONS'])
def process_text():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    # Check if model is available
    if not model:
        return jsonify({
            'error': 'AI model not available. Check server logs.',
            'success': False
        }), 503
    
    try:
        # Get and validate input
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Invalid request format. Expected: {"text": "your message"}',
                'success': False
            }), 400
        
        input_text = data['text']
        if not input_text or not input_text.strip():
            return jsonify({
                'error': 'Text input cannot be empty',
                'success': False
            }), 400
        
        # Log the request (first 100 chars only for privacy)
        print(f"🔄 Processing: {input_text[:100]}{'...' if len(input_text) > 100 else ''}")
        
        # Generate AI response
        response = model.generate_content(input_text)
        processed_text = response.text
        
        print(f"✅ Response generated ({len(processed_text)} characters)")
        
        return jsonify({
            'processed_text': processed_text,
            'success': True,
            'input_length': len(input_text),
            'output_length': len(processed_text)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Processing error: {error_msg}")
        return jsonify({
            'error': f'AI processing failed: {error_msg}',
            'success': False
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/health', '/process_text']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please check server logs'
    }), 500

# Get port from environment variable (Render provides this)
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    print(f"🚀 Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
