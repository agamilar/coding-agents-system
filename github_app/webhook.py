"""
Webhook Handler
Processes GitHub webhook events and triggers appropriate agents
"""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any
from flask import jsonify

from agents.code_agent import CodeAgent
from agents.review_agent import ReviewAgent

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Handles GitHub webhook events"""
    
    def __init__(self, github_auth):
        """
        Initialize webhook handler
        
        Args:
            github_auth: GitHubAppAuth instance
        """
        self.github_auth = github_auth
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', '').encode()
        self.max_iterations = int(os.getenv('MAX_ITERATIONS', 5))
    
    def verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify GitHub webhook signature
        
        Args:
            payload_body: Raw request body
            signature_header: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid
        """
        if not signature_header:
            return False
        
        hash_object = hmac.new(self.webhook_secret, msg=payload_body, digestmod=hashlib.sha256)
        expected_signature = 'sha256=' + hash_object.hexdigest()
        
        return hmac.compare_digest(expected_signature, signature_header)
    
    def handle_issue_event(self, payload: Dict[str, Any]):
        """
        Handle issue events (opened, edited, reopened)
        
        Args:
            payload: Webhook payload
            
        Returns:
            JSON response
        """
        action = payload.get('action')
        logger.info(f'Handling issue event: {action}')
        
        # Only process opened, edited, or reopened issues
        if action not in ['opened', 'edited', 'reopened']:
            return jsonify({'message': f'Issue action {action} not processed'}), 200
        
        # Get installation ID
        installation_id = self.github_auth.get_installation_id_from_payload(payload)
        if not installation_id:
            logger.error('No installation ID in payload')
            return jsonify({'error': 'No installation ID'}), 400
        
        # Get issue details
        issue = payload.get('issue', {})
        issue_number = issue.get('number')
        issue_title = issue.get('title')
        issue_body = issue.get('body', '')
        
        # Get repository details
        repository = payload.get('repository', {})
        repo_full_name = repository.get('full_name')
        
        logger.info(f'Processing issue #{issue_number}: {issue_title}')
        logger.info(f'Repository: {repo_full_name}')
        
        try:
            # Get GitHub client
            github_client = self.github_auth.get_github_client(installation_id)
            
            # Initialize Code Agent
            code_agent = CodeAgent(github_client)
            
            # Process the issue
            result = code_agent.process_issue(
                repo_full_name=repo_full_name,
                issue_number=issue_number,
                issue_title=issue_title,
                issue_body=issue_body
            )
            
            if result.get('success'):
                logger.info(f'Successfully created PR: {result.get("pr_url")}')
                return jsonify({
                    'message': 'Issue processed successfully',
                    'pr_url': result.get('pr_url'),
                    'pr_number': result.get('pr_number')
                }), 200
            else:
                logger.error(f'Failed to process issue: {result.get("error")}')
                return jsonify({
                    'error': result.get('error')
                }), 500
        
        except Exception as e:
            logger.error(f'Error processing issue: {str(e)}', exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    def handle_pull_request_event(self, payload: Dict[str, Any]):
        """
        Handle pull request events (opened, synchronize, reopened)
        
        Args:
            payload: Webhook payload
            
        Returns:
            JSON response
        """
        action = payload.get('action')
        logger.info(f'Handling pull request event: {action}')
        
        # GitHub Actions workflow will handle the review
        # This webhook is just for logging and potential future enhancements
        
        pr = payload.get('pull_request', {})
        pr_number = pr.get('number')
        pr_title = pr.get('title')
        
        repository = payload.get('repository', {})
        repo_full_name = repository.get('full_name')
        
        logger.info(f'Pull request #{pr_number}: {pr_title}')
        logger.info(f'Repository: {repo_full_name}')
        logger.info('GitHub Actions workflow will handle the review')
        
        return jsonify({
            'message': 'Pull request event received',
            'note': 'Review will be handled by GitHub Actions'
        }), 200
    
    def handle_review_event(self, payload: Dict[str, Any]):
        """
        Handle pull request review events
        
        Args:
            payload: Webhook payload
            
        Returns:
            JSON response
        """
        action = payload.get('action')
        logger.info(f'Handling pull request review event: {action}')
        
        review = payload.get('review', {})
        review_state = review.get('state')
        review_body = review.get('body', '')
        
        pr = payload.get('pull_request', {})
        pr_number = pr.get('number')
        
        repository = payload.get('repository', {})
        repo_full_name = repository.get('full_name')
        
        logger.info(f'Review on PR #{pr_number}: {review_state}')
        
        # If review requests changes and it's from our Review Agent
        if review_state == 'changes_requested' and 'AI Review Agent' in review_body:
            installation_id = self.github_auth.get_installation_id_from_payload(payload)
            
            if not installation_id:
                logger.error('No installation ID in payload')
                return jsonify({'error': 'No installation ID'}), 400
            
            try:
                # Get GitHub client
                github_client = self.github_auth.get_github_client(installation_id)
                
                # Get the linked issue number from PR
                issue_number = self._extract_issue_number_from_pr(github_client, repo_full_name, pr_number)
                
                if issue_number:
                    # Initialize Code Agent
                    code_agent = CodeAgent(github_client)
                    
                    # Check iteration count to prevent infinite loops
                    iteration_count = self._get_iteration_count(github_client, repo_full_name, pr_number)
                    
                    if iteration_count >= self.max_iterations:
                        logger.warning(f'Max iterations ({self.max_iterations}) reached for PR #{pr_number}')
                        return jsonify({
                            'message': 'Max iterations reached',
                            'iterations': iteration_count
                        }), 200
                    
                    # Process the review feedback
                    result = code_agent.process_review_feedback(
                        repo_full_name=repo_full_name,
                        pr_number=pr_number,
                        issue_number=issue_number,
                        review_body=review_body
                    )
                    
                    if result.get('success'):
                        logger.info(f'Successfully updated PR #{pr_number}')
                        return jsonify({
                            'message': 'Review feedback processed',
                            'iteration': iteration_count + 1
                        }), 200
                    else:
                        logger.error(f'Failed to process review feedback: {result.get("error")}')
                        return jsonify({'error': result.get('error')}), 500
        
        return jsonify({'message': 'Review event processed'}), 200
    
    def _extract_issue_number_from_pr(self, github_client, repo_full_name: str, pr_number: int) -> int:
        """
        Extract issue number from PR body
        
        Args:
            github_client: Authenticated GitHub client
            repo_full_name: Full repository name
            pr_number: Pull request number
            
        Returns:
            Issue number or None
        """
        try:
            repo = github_client.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            
            # Look for "Closes #123" or "Fixes #123" pattern
            body = pr.body or ''
            
            import re
            patterns = [
                r'Closes #(\d+)',
                r'Fixes #(\d+)',
                r'Resolves #(\d+)',
                r'Issue: #(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body)
                if match:
                    return int(match.group(1))
            
            return None
        
        except Exception as e:
            logger.error(f'Error extracting issue number: {str(e)}')
            return None
    
    def _get_iteration_count(self, github_client, repo_full_name: str, pr_number: int) -> int:
        """
        Get iteration count for a PR
        
        Args:
            github_client: Authenticated GitHub client
            repo_full_name: Full repository name
            pr_number: Pull request number
            
        Returns:
            Number of iterations
        """
        try:
            repo = github_client.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            
            # Count commits as a proxy for iterations
            commits = pr.get_commits()
            return commits.totalCount
        
        except Exception as e:
            logger.error(f'Error getting iteration count: {str(e)}')
            return 0
