# src/app.py
import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. Securely load the API Key (Validated via K8s Secrets)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("System Error: GOOGLE_API_KEY not found in environment.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

@app.route('/analyze-telemetry', methods=['POST'])
def analyze_telemetry():
    """
    Endpoint to process industrial sensor data using GenAI.
    Expected JSON: {"sensor_id": "PUMP-01", "logs": "Pressure high, Temp 95C"}
    """
    data = request.json
    sensor_id = data.get("sensor_id", "Unknown")
    logs = data.get("logs", "")

    # Structured Prompting for "Industrial Logic"
    prompt = f"""
    You are an expert Industrial Reliability Engineer.
    Analyze the following telemetry from Sensor {sensor_id}:
    
    LOG DATA: {logs}
    
    Please provide:
    1. A summary of the potential fault.
    2. Recommended immediate action (SOP).
    3. Estimated risk level (Low/Medium/High).
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({
            "status": "success",
            "analysis": response.text,
            "handled_by": "Honeywell-AI-Cloud-Gateway"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000 as defined in your K8s Deployment
    app.run(host='0.0.0.0', port=5000)
