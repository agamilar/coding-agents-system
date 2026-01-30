"""
Main Flask application for Coding Agents GitHub App
Handles webhooks and orchestrates Code and Review agents
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from github_app.webhook import WebhookHandler
from github_app.auth import GitHubAppAuth
from utils.tunnel import setup_ngrok_tunnel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('GITHUB_WEBHOOK_SECRET')

# Initialize GitHub App authentication
github_auth = GitHubAppAuth(
    app_id=os.getenv('GITHUB_APP_ID'),
    private_key_path=os.getenv('GITHUB_APP_PRIVATE_KEY_PATH')
)

# Initialize webhook handler
webhook_handler = WebhookHandler(github_auth)


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'status': 'running',
        'app': 'Coding Agents System',
        'version': '1.0.0'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'github_app_configured': bool(os.getenv('GITHUB_APP_ID')),
        'llm_configured': bool(
            os.getenv('OPENAI_API_KEY') or 
            os.getenv('YANDEX_API_KEY') or 
            os.getenv('ANTHROPIC_API_KEY')
        )
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle GitHub webhook events
    
    Supported events:
    - issues: opened, edited, reopened
    - pull_request: opened, synchronize, reopened
    - pull_request_review: submitted
    """
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not webhook_handler.verify_signature(request.data, signature):
            logger.warning('Invalid webhook signature')
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        logger.info(f'Received webhook event: {event_type}')
        
        # Handle different event types
        if event_type == 'issues':
            return webhook_handler.handle_issue_event(payload)
        
        elif event_type == 'pull_request':
            return webhook_handler.handle_pull_request_event(payload)
        
        elif event_type == 'pull_request_review':
            return webhook_handler.handle_review_event(payload)
        
        elif event_type == 'ping':
            logger.info('Received ping event')
            return jsonify({'message': 'pong'})
        
        else:
            logger.info(f'Unhandled event type: {event_type}')
            return jsonify({'message': 'Event type not handled'}), 200
    
    except Exception as e:
        logger.error(f'Error handling webhook: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/setup', methods=['GET'])
def setup_info():
    """Provide setup information for the GitHub App"""
    ngrok_url = os.getenv('NGROK_URL', '')
    base_url = ngrok_url if ngrok_url else 'http://your-domain.com'
    
    return jsonify({
        'webhook_url': f'{base_url}/webhook',
        'app_id': os.getenv('GITHUB_APP_ID'),
        'instructions': {
            '1': 'Create a GitHub App in your organization settings',
            '2': f'Set webhook URL to: {base_url}/webhook',
            '3': 'Set webhook secret and add to .env file',
            '4': 'Download private key and place in ./keys/ directory',
            '5': 'Install the app on your repositories',
            '6': 'Create an issue to test!'
        },
        'required_permissions': {
            'Contents': 'Read & Write',
            'Issues': 'Read & Write',
            'Pull requests': 'Read & Write',
            'Workflows': 'Read & Write',
            'Metadata': 'Read-only'
        },
        'subscribe_to_events': [
            'Issues',
            'Pull request',
            'Pull request review'
        ]
    })


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f'Internal error: {str(e)}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Main entry point"""
    # Setup ngrok tunnel if enabled
    if os.getenv('USE_NGROK', 'false').lower() == 'true':
        ngrok_url = setup_ngrok_tunnel(
            port=int(os.getenv('FLASK_PORT', 3000)),
            auth_token=os.getenv('NGROK_AUTH_TOKEN'),
            subdomain=os.getenv('NGROK_SUBDOMAIN')
        )
        if ngrok_url:
            logger.info(f'Ngrok tunnel active at: {ngrok_url}')
            os.environ['NGROK_URL'] = ngrok_url
    
    # Run Flask app
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 3000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f'Starting Coding Agents System on {host}:{port}')
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
