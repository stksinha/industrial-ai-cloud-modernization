"""
Test suite for DC Modernization AI Gateway
"""
import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app, DCMetricsSchema, CapacityPlanSchema, PowerOptimizationSchema


class TestDCModernizationApp(unittest.TestCase):
    """Test cases for DC Modernization endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'DC-AI-Modernization-Gateway')

    def test_analyze_dc_metrics_missing_server_id(self):
        """Test DC metrics endpoint rejects missing server_id"""
        response = self.client.post(
            '/analyze-dc-metrics',
            data=json.dumps({'metrics': 'CPU 85%'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_dc_metrics_missing_metrics(self):
        """Test DC metrics endpoint rejects missing metrics"""
        response = self.client.post(
            '/analyze-dc-metrics',
            data=json.dumps({'server_id': 'DC1-SRV-01'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @patch('src.app.model.generate_content')
    def test_analyze_dc_metrics_success(self, mock_generate):
        """Test successful DC metrics analysis"""
        mock_response = MagicMock()
        mock_response.text = "Infrastructure analysis..."
        mock_generate.return_value = mock_response

        response = self.client.post(
            '/analyze-dc-metrics',
            data=json.dumps({
                'server_id': 'DC1-RACK-05-SRV-12',
                'metrics': 'CPU 85%, Memory 72%',
                'region': 'us-east-1',
                'environment': 'production'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['server_id'], 'DC1-RACK-05-SRV-12')

    def test_capacity_planning_missing_dc_zone(self):
        """Test capacity planning rejects missing dc_zone"""
        response = self.client.post(
            '/capacity-planning',
            data=json.dumps({'current_utilization': 'CPU 78%'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @patch('src.app.model.generate_content')
    def test_capacity_planning_success(self, mock_generate):
        """Test successful capacity planning"""
        mock_response = MagicMock()
        mock_response.text = "Capacity forecast..."
        mock_generate.return_value = mock_response

        response = self.client.post(
            '/capacity-planning',
            data=json.dumps({
                'dc_zone': 'DC1-Zone-A',
                'current_utilization': 'CPU 78%, Memory 82%, Storage 65%',
                'growth_trend': '12% quarterly growth'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_power_optimization_missing_device_id(self):
        """Test power optimization rejects missing device_id"""
        response = self.client.post(
            '/power-optimization',
            data=json.dumps({'power_data': '3.2kW'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @patch('src.app.model.generate_content')
    def test_power_optimization_success(self, mock_generate):
        """Test successful power optimization"""
        mock_response = MagicMock()
        mock_response.text = "Power optimization..."
        mock_generate.return_value = mock_response

        response = self.client.post(
            '/power-optimization',
            data=json.dumps({
                'device_id': 'PDU-RACK-12',
                'power_data': 'Current draw 3.2kW, Peak 3.8kW',
                'efficiency_goal': 'reduce_pue'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

    def test_404_not_found(self):
        """Test 404 error handler"""
        response = self.client.get('/non-existent-endpoint')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error_code'], 'NOT_FOUND')

    def test_dc_metrics_schema_validation(self):
        """Test DCMetricsSchema validation"""
        schema = DCMetricsSchema()
        valid_data = {
            'server_id': 'DC1-SRV-01',
            'metrics': 'CPU 85%'
        }
        result = schema.load(valid_data)
        self.assertEqual(result['server_id'], 'DC1-SRV-01')


if __name__ == '__main__':
    unittest.main()
