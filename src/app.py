# src/app.py
import os
import logging
from functools import wraps
import google.generativeai as genai
from flask import Flask, request, jsonify, abort
from marshmallow import Schema, fields, ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize logging
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# 1. Securely load the API Key (Validated via K8s Secrets)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    log.error("System Error: GOOGLE_API_KEY not found in environment.")
    raise ValueError("System Error: GOOGLE_API_KEY not found in environment.")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    log.info("GenAI model initialized successfully.")
except Exception as e:
    log.error(f"Failed to initialize GenAI model: {str(e)}")
    raise

# Define input validation schema
class TelemetrySchema(Schema):
    """Schema for validating telemetry data input."""
    sensor_id = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    logs = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)


@app.route('/analyze-telemetry', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_telemetry():
    """
    Endpoint to process industrial sensor data using GenAI.
    
    Expected JSON:
    {
        "sensor_id": "PUMP-01",
        "logs": "Pressure high, Temp 95C"
    }
    
    Returns:
    {
        "status": "success" or "error",
        "analysis": "AI-generated analysis",
        "handled_by": "Honeywell-AI-Cloud-Gateway"
    }
    """
    # Validate input
    schema = TelemetrySchema()
    try:
        data = schema.load(request.json or {})
    except ValidationError as e:
        log.warning(f"Validation error in /analyze-telemetry: {e.messages}")
        return jsonify({
            "status": "error",
            "message": "Invalid input. Both 'sensor_id' and 'logs' are required.",
            "details": e.messages
        }), 400
    except Exception as e:
        log.error(f"Unexpected error during validation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

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
        log.info(f"Processing telemetry for sensor: {sensor_id}")
        response = model.generate_content(prompt)
        
        log.info(f"Successfully analyzed telemetry for sensor: {sensor_id}")
        return jsonify({
            "status": "success",
            "analysis": response.text,
            "handled_by": "Honeywell-AI-Cloud-Gateway"
        }), 200
        
    except genai.types.BlockedPromptException as e:
        log.warning(f"Prompt blocked for sensor {sensor_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "The provided telemetry data was flagged as unsafe.",
            "error_code": "BLOCKED_PROMPT"
        }), 400
        
    except genai.types.StopCandidateException as e:
        log.warning(f"Generation stopped for sensor {sensor_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Analysis could not be completed.",
            "error_code": "GENERATION_STOPPED"
        }), 500
        
    except Exception as e:
        log.exception(f"Error generating content for sensor {sensor_id}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error",
            "error_code": "INTERNAL_ERROR"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness probes."""
    return jsonify({"status": "healthy", "service": "Honeywell-AI-Cloud-Gateway"}), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors."""
    log.warning(f"Rate limit exceeded: {e.description}")
    return jsonify({
        "status": "error",
        "message": "Rate limit exceeded. Please try again later.",
        "error_code": "RATE_LIMIT_EXCEEDED"
    }), 429


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found.",
        "error_code": "NOT_FOUND"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    log.error(f"Internal server error: {str(e)}")
    return jsonify({
        "status": "error",
        "message": "Internal Server Error",
        "error_code": "INTERNAL_ERROR"
    }), 500


if __name__ == '__main__':
    # Run on port 5000 as defined in your K8s Deployment
    # Set debug=False in production environments
    app.run(host='0.0.0.0', port=5000, debug=False)