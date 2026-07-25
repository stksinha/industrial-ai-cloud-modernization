# src/app.py - Data Center Modernization AI Analysis Engine
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
    log.info("GenAI model initialized successfully for DC Modernization.")
except Exception as e:
    log.error(f"Failed to initialize GenAI model: {str(e)}")
    raise

# Define input validation schemas
class DCMetricsSchema(Schema):
    """Schema for validating data center infrastructure metrics."""
    server_id = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    metrics = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    region = fields.String(required=False, allow_none=True)
    environment = fields.String(required=False, allow_none=True, missing="production")


class CapacityPlanSchema(Schema):
    """Schema for capacity planning analysis."""
    dc_zone = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    current_utilization = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    growth_trend = fields.String(required=False, allow_none=True)


class PowerOptimizationSchema(Schema):
    """Schema for power consumption optimization analysis."""
    device_id = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    power_data = fields.String(required=True, validate=lambda x: len(x.strip()) > 0)
    efficiency_goal = fields.String(required=False, allow_none=True, missing="reduce_pue")


@app.route('/analyze-dc-metrics', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_dc_metrics():
    """
    Endpoint to analyze data center infrastructure metrics using GenAI.
    
    Expected JSON:
    {
        "server_id": "DC1-RACK-05-SRV-12",
        "metrics": "CPU 85%, Memory 72%, Disk I/O High, Network utilization 60%",
        "region": "us-east-1",
        "environment": "production"
    }
    
    Returns:
    {
        "status": "success" or "error",
        "analysis": "AI-generated infrastructure health analysis",
        "recommendations": "Optimization recommendations",
        "handled_by": "DC-AI-Modernization-Gateway"
    }
    """
    schema = DCMetricsSchema()
    try:
        data = schema.load(request.json or {})
    except ValidationError as e:
        log.warning(f"Validation error in /analyze-dc-metrics: {e.messages}")
        return jsonify({
            "status": "error",
            "message": "Invalid input. 'server_id' and 'metrics' are required.",
            "details": e.messages
        }), 400
    except Exception as e:
        log.error(f"Unexpected error during validation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

    server_id = data.get("server_id", "Unknown")
    metrics = data.get("metrics", "")
    region = data.get("region", "Unknown")
    environment = data.get("environment", "production")

    # Structured Prompting for Data Center Infrastructure Analysis
    prompt = f"""
    You are an expert Data Center Infrastructure Analyst specializing in modernization and optimization.
    
    Analyze the following infrastructure metrics from Server {server_id} in region {region} ({environment} environment):
    
    METRICS DATA: {metrics}
    
    Please provide:
    1. Infrastructure Health Assessment - Current status and potential bottlenecks
    2. Modernization Recommendations - Actions to improve efficiency and reliability
    3. Risk Level - Critical/High/Medium/Low with justification
    4. Immediate Actions - SOP steps if intervention is required
    5. Long-term Strategy - Capacity planning and upgrades needed
    """

    try:
        log.info(f"Processing DC metrics for server: {server_id} in {region}")
        response = model.generate_content(prompt)
        
        log.info(f"Successfully analyzed DC metrics for server: {server_id}")
        return jsonify({
            "status": "success",
            "analysis": response.text,
            "server_id": server_id,
            "region": region,
            "handled_by": "DC-AI-Modernization-Gateway"
        }), 200
        
    except genai.types.BlockedPromptException as e:
        log.warning(f"Prompt blocked for server {server_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "The provided metrics data was flagged as unsafe.",
            "error_code": "BLOCKED_PROMPT"
        }), 400
        
    except genai.types.StopCandidateException as e:
        log.warning(f"Generation stopped for server {server_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Analysis could not be completed.",
            "error_code": "GENERATION_STOPPED"
        }), 500
        
    except Exception as e:
        log.exception(f"Error generating content for server {server_id}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error",
            "error_code": "INTERNAL_ERROR"
        }), 500


@app.route('/capacity-planning', methods=['POST'])
@limiter.limit("5 per minute")
def capacity_planning():
    """
    Endpoint for data center capacity planning analysis.
    
    Expected JSON:
    {
        "dc_zone": "DC1-Zone-A",
        "current_utilization": "CPU 78%, Memory 82%, Storage 65%",
        "growth_trend": "12% quarterly growth"
    }
    
    Returns:
    {
        "status": "success" or "error",
        "capacity_analysis": "Detailed capacity planning recommendations",
        "timeline": "Upgrade timeline recommendations"
    }
    """
    schema = CapacityPlanSchema()
    try:
        data = schema.load(request.json or {})
    except ValidationError as e:
        log.warning(f"Validation error in /capacity-planning: {e.messages}")
        return jsonify({
            "status": "error",
            "message": "Invalid input. 'dc_zone' and 'current_utilization' are required.",
            "details": e.messages
        }), 400
    except Exception as e:
        log.error(f"Unexpected error during validation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

    dc_zone = data.get("dc_zone", "Unknown")
    utilization = data.get("current_utilization", "")
    growth_trend = data.get("growth_trend", "Normal growth pattern")

    prompt = f"""
    You are a Data Center Capacity Planning Expert with expertise in infrastructure modernization.
    
    Analyze capacity requirements for Data Center Zone {dc_zone}:
    
    CURRENT UTILIZATION: {utilization}
    GROWTH TREND: {growth_trend}
    
    Provide:
    1. Current Capacity Assessment
    2. 12-Month Forecast
    3. Recommended Expansion Timeline
    4. Hardware/Infrastructure Upgrades Needed
    5. Cost-Benefit Analysis for Modernization
    """

    try:
        log.info(f"Processing capacity planning for zone: {dc_zone}")
        response = model.generate_content(prompt)
        
        log.info(f"Successfully generated capacity plan for zone: {dc_zone}")
        return jsonify({
            "status": "success",
            "capacity_analysis": response.text,
            "zone": dc_zone,
            "handled_by": "DC-AI-Modernization-Gateway"
        }), 200
        
    except Exception as e:
        log.exception(f"Error in capacity planning for zone {dc_zone}")
        return jsonify({
            "status": "error",
            "message": "Capacity planning analysis failed",
            "error_code": "PLANNING_ERROR"
        }), 500


@app.route('/power-optimization', methods=['POST'])
@limiter.limit("8 per minute")
def power_optimization():
    """
    Endpoint for power consumption analysis and optimization.
    
    Expected JSON:
    {
        "device_id": "PDU-RACK-12",
        "power_data": "Current draw 3.2kW, Peak 3.8kW, Idle baseline 0.8kW",
        "efficiency_goal": "reduce_pue"
    }
    
    Returns:
    {
        "status": "success" or "error",
        "optimization_analysis": "Power optimization recommendations",
        "estimated_savings": "Annual energy and cost savings"
    }
    """
    schema = PowerOptimizationSchema()
    try:
        data = schema.load(request.json or {})
    except ValidationError as e:
        log.warning(f"Validation error in /power-optimization: {e.messages}")
        return jsonify({
            "status": "error",
            "message": "Invalid input. 'device_id' and 'power_data' are required.",
            "details": e.messages
        }), 400
    except Exception as e:
        log.error(f"Unexpected error during validation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error"
        }), 500

    device_id = data.get("device_id", "Unknown")
    power_data = data.get("power_data", "")
    efficiency_goal = data.get("efficiency_goal", "reduce_pue")

    prompt = f"""
    You are a Data Center Power and Cooling Optimization Specialist.
    
    Analyze power consumption for Device {device_id} with efficiency goal: {efficiency_goal}
    
    POWER DATA: {power_data}
    
    Provide:
    1. Current Power Efficiency Assessment (PUE analysis if applicable)
    2. Immediate Optimization Opportunities
    3. Long-term Power Efficiency Improvements
    4. Estimated Annual Energy Savings (kWh and cost)
    5. ROI Timeline for Recommended Upgrades
    6. Cooling and Thermal Management Improvements
    """

    try:
        log.info(f"Processing power optimization for device: {device_id}")
        response = model.generate_content(prompt)
        
        log.info(f"Successfully analyzed power optimization for device: {device_id}")
        return jsonify({
            "status": "success",
            "optimization_analysis": response.text,
            "device_id": device_id,
            "efficiency_goal": efficiency_goal,
            "handled_by": "DC-AI-Modernization-Gateway"
        }), 200
        
    except Exception as e:
        log.exception(f"Error in power optimization for device {device_id}")
        return jsonify({
            "status": "error",
            "message": "Power optimization analysis failed",
            "error_code": "OPTIMIZATION_ERROR"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes liveness probes."""
    return jsonify({
        "status": "healthy",
        "service": "DC-AI-Modernization-Gateway",
        "endpoints": [
            "/analyze-dc-metrics",
            "/capacity-planning",
            "/power-optimization"
        ]
    }), 200


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
