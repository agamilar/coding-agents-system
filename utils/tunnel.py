"""
Tunnel Setup Utility
Sets up ngrok tunnel for local development
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_ngrok_tunnel(
    port: int = 3000,
    auth_token: Optional[str] = None,
    subdomain: Optional[str] = None
) -> Optional[str]:
    """
    Setup ngrok tunnel for local development
    
    Args:
        port: Local port to expose
        auth_token: Ngrok auth token
        subdomain: Custom subdomain (requires paid ngrok plan)
        
    Returns:
        Public URL or None if setup fails
    """
    try:
        from pyngrok import ngrok, conf
        
        # Set auth token if provided
        if auth_token:
            conf.get_default().auth_token = auth_token
            logger.info('Ngrok auth token configured')
        
        # Setup tunnel options
        options = {
            'bind_tls': True  # Use HTTPS
        }
        
        if subdomain:
            options['subdomain'] = subdomain
            logger.info(f'Using custom subdomain: {subdomain}')
        
        # Create tunnel
        logger.info(f'Creating ngrok tunnel for port {port}...')
        tunnel = ngrok.connect(port, **options)
        
        public_url = tunnel.public_url
        logger.info(f'Ngrok tunnel created successfully: {public_url}')
        logger.info(f'Ngrok dashboard: http://localhost:4040')
        
        return public_url
    
    except ImportError:
        logger.error('pyngrok not installed. Install with: pip install pyngrok')
        return None
    
    except Exception as e:
        logger.error(f'Failed to setup ngrok tunnel: {str(e)}')
        logger.info('Make sure you have ngrok installed and configured')
        logger.info('Get auth token from: https://dashboard.ngrok.com/get-started/your-authtoken')
        return None


def get_tunnel_info() -> dict:
    """
    Get information about active ngrok tunnels
    
    Returns:
        Dict with tunnel information
    """
    try:
        from pyngrok import ngrok
        
        tunnels = ngrok.get_tunnels()
        
        if not tunnels:
            return {'active': False, 'tunnels': []}
        
        tunnel_info = []
        for tunnel in tunnels:
            tunnel_info.append({
                'name': tunnel.name,
                'public_url': tunnel.public_url,
                'proto': tunnel.proto,
                'config': tunnel.config
            })
        
        return {
            'active': True,
            'count': len(tunnels),
            'tunnels': tunnel_info
        }
    
    except Exception as e:
        logger.error(f'Error getting tunnel info: {str(e)}')
        return {'active': False, 'error': str(e)}


def disconnect_tunnel():
    """Disconnect all ngrok tunnels"""
    try:
        from pyngrok import ngrok
        
        ngrok.disconnect()
        logger.info('Ngrok tunnels disconnected')
    
    except Exception as e:
        logger.error(f'Error disconnecting tunnels: {str(e)}')


if __name__ == '__main__':
    """Run tunnel setup standalone"""
    import sys
    
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv('FLASK_PORT', 3000))
    
    # Setup tunnel
    url = setup_ngrok_tunnel(
        port=port,
        auth_token=os.getenv('NGROK_AUTH_TOKEN'),
        subdomain=os.getenv('NGROK_SUBDOMAIN')
    )
    
    if url:
        print(f'\n✅ Ngrok tunnel active!')
        print(f'Public URL: {url}')
        print(f'Webhook URL: {url}/webhook')
        print(f'\nAdd this webhook URL to your GitHub App settings:')
        print(f'https://github.com/settings/apps/[your-app]/advanced')
        print(f'\nPress Ctrl+C to stop...\n')
        
        # Keep running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nDisconnecting tunnel...')
            disconnect_tunnel()
            print('Goodbye!')
    else:
        print('❌ Failed to setup ngrok tunnel')
        sys.exit(1)
