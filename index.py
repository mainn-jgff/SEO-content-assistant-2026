import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
sys.path.insert(0, os.path.dirname(__file__))
import agent

load_dotenv()

app = Flask(__name__)
CORS(app)

WEBHOOK_URL = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")

@app.route('/api/state1', methods=['POST'])
def start_session():
    data = request.json
    try:
        matrix = agent.generate_keyword_matrix(data)
        return jsonify({'data': matrix, 'state': 2})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/state2', methods=['POST'])
def select_keywords():
    data = request.json
    try:
        outline = agent.generate_outline(data)
        return jsonify({'data': outline, 'state': 3})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/state3', methods=['POST'])
def approve_outline():
    data = request.json
    try:
        content = agent.generate_content(data)
        return jsonify({'data': content, 'state': 4})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/state4', methods=['POST'])
def qa_content():
    data = request.json
    try:
        qa_result = agent.qa_content(data)
        return jsonify({'data': qa_result, 'state': 5})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/state5', methods=['POST'])
def submit_feedback():
    data = request.json
    
    # Gửi qua Webhook
    if WEBHOOK_URL:
        from datetime import datetime
        end_time = datetime.now().isoformat()
        
        payload = {
            "start_time": data.get('start_time', ''),
            "end_time": end_time,
            "topic": data.get('topic', ''),
            "goal": data.get('goal', ''),
            "audience": data.get('audience', ''),
            "voice": data.get('voice', ''),
            "suggested_keywords": data.get('suggested_keywords', ''),
            "selected_keywords": data.get('selected_keywords', ''),
            "final_content": data.get('final_content', ''),
            "user_feedback": data.get('user_feedback', '')
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print("Webhook error:", str(e))
            
    return jsonify({'success': True, 'state': 6})
