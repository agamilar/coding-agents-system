"""
GitHub App Authentication
Handles JWT token generation and installation token retrieval
"""

import os
import time
import jwt
import logging
from typing import Optional
from github import Github, Auth

logger = logging.getLogger(__name__)


class GitHubAppAuth:
    """Manages GitHub App authentication"""
    
    def __init__(self, app_id: str, private_key_path: str):
        """
        Initialize GitHub App authentication
        
        Args:
            app_id: GitHub App ID
            private_key_path: Path to private key file
        """
        self.app_id = app_id
        self.private_key_path = private_key_path
        self._load_private_key()
    
    def _load_private_key(self):
        """Load private key from file"""
        try:
            with open(self.private_key_path, 'r') as key_file:
                self.private_key = key_file.read()
            logger.info('Private key loaded successfully')
        except FileNotFoundError:
            logger.error(f'Private key file not found: {self.private_key_path}')
            raise
        except Exception as e:
            logger.error(f'Error loading private key: {str(e)}')
            raise
    
    def generate_jwt(self) -> str:
        """
        Generate JWT token for GitHub App authentication
        
        Returns:
            JWT token string
        """
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Issued at time (60 seconds in the past)
            'exp': now + (10 * 60),  # Expiration time (10 minutes)
            'iss': self.app_id  # Issuer (GitHub App ID)
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        logger.debug('Generated JWT token')
        return token
    
    def get_installation_token(self, installation_id: str) -> str:
        """
        Get installation access token for a specific installation
        
        Args:
            installation_id: GitHub App installation ID
            
        Returns:
            Installation access token
        """
        try:
            # Create GitHub instance with JWT
            jwt_token = self.generate_jwt()
            auth = Auth.AppAuth(self.app_id, self.private_key)
            github_app = Github(auth=auth)
            
            # Get installation
            installation = github_app.get_app().get_installation(int(installation_id))
            
            # Get access token
            access_token = installation.get_access_token()
            logger.info(f'Retrieved installation token for installation {installation_id}')
            
            return access_token.token
        
        except Exception as e:
            logger.error(f'Error getting installation token: {str(e)}')
            raise
    
    def get_github_client(self, installation_id: str) -> Github:
        """
        Get authenticated GitHub client for an installation
        
        Args:
            installation_id: GitHub App installation ID
            
        Returns:
            Authenticated PyGithub client
        """
        token = self.get_installation_token(installation_id)
        auth = Auth.Token(token)
        return Github(auth=auth)
    
    def get_installation_id_from_payload(self, payload: dict) -> Optional[str]:
        """
        Extract installation ID from webhook payload
        
        Args:
            payload: Webhook payload
            
        Returns:
            Installation ID or None
        """
        installation = payload.get('installation')
        if installation:
            return str(installation.get('id'))
        return None
