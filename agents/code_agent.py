"""
Code Agent
Analyzes issues and generates code changes
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from github import Github

from github_app.api import GitHubAPIHelper
from utils.llm import LLMClient
from agents.prompts import (
    CODE_AGENT_SYSTEM_PROMPT,
    format_code_agent_prompt,
    format_review_feedback_prompt
)

logger = logging.getLogger(__name__)


class CodeAgent:
    """Agent for generating code based on issues"""
    
    def __init__(self, github_client: Github):
        """
        Initialize Code Agent
        
        Args:
            github_client: Authenticated GitHub client
        """
        self.github_client = github_client
        self.llm_client = LLMClient()
        self.api_helper = GitHubAPIHelper()
    
    def process_issue(
        self,
        repo_full_name: str,
        issue_number: int,
        issue_title: str,
        issue_body: str
    ) -> Dict[str, Any]:
        """
        Process an issue and create a pull request with code changes
        
        Args:
            repo_full_name: Full repository name
            issue_number: Issue number
            issue_title: Issue title
            issue_body: Issue description
            
        Returns:
            Dict with success status and PR details
        """
        try:
            logger.info(f'Processing issue #{issue_number}: {issue_title}')
            
            # Get repository
            repo = self.api_helper.get_repository(self.github_client, repo_full_name)
            
            # Get repository context
            default_branch = repo.default_branch
            existing_files = self._get_existing_files(repo)
            
            # Generate code changes using LLM
            logger.info('Generating code changes...')
            changes = self._generate_code_changes(
                issue_title=issue_title,
                issue_body=issue_body,
                repo_name=repo_full_name,
                default_branch=default_branch,
                existing_files=existing_files
            )
            
            if not changes:
                return {
                    'success': False,
                    'error': 'Failed to generate code changes'
                }
            
            # Create branch for changes
            branch_name = f'issue-{issue_number}-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            logger.info(f'Creating branch: {branch_name}')
            self.api_helper.create_branch(repo, branch_name, default_branch)
            
            # Apply changes to repository
            logger.info('Applying code changes...')
            self._apply_changes(repo, changes, branch_name)
            
            # Create pull request
            pr_title = f'Fix: {issue_title}'
            pr_body = self._create_pr_body(issue_number, changes)
            
            logger.info('Creating pull request...')
            pr = self.api_helper.create_pull_request(
                repo=repo,
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=default_branch
            )
            
            # Add comment to issue
            issue = self.api_helper.get_issue(repo, issue_number)
            self.api_helper.add_comment_to_issue(
                issue,
                f'🤖 I\'ve created a pull request to address this issue: #{pr.number}\n\n'
                f'The changes will be reviewed automatically.'
            )
            
            return {
                'success': True,
                'pr_number': pr.number,
                'pr_url': pr.html_url,
                'branch': branch_name
            }
        
        except Exception as e:
            logger.error(f'Error processing issue: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_review_feedback(
        self,
        repo_full_name: str,
        pr_number: int,
        issue_number: int,
        review_body: str
    ) -> Dict[str, Any]:
        """
        Process review feedback and update PR with fixes
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
            issue_number: Related issue number
            review_body: Review feedback
            
        Returns:
            Dict with success status
        """
        try:
            logger.info(f'Processing review feedback for PR #{pr_number}')
            
            # Get repository and PR
            repo = self.api_helper.get_repository(self.github_client, repo_full_name)
            pr = self.api_helper.get_pull_request(repo, pr_number)
            issue = self.api_helper.get_issue(repo, issue_number)
            
            # Get current code state
            pr_diff = self.api_helper.get_pr_diff(pr)
            
            # Generate fixes using LLM
            logger.info('Generating fixes based on review...')
            changes = self._generate_fixes_from_review(
                issue_description=f'{issue.title}\n\n{issue.body}',
                previous_changes=pr_diff,
                review_feedback=review_body,
                current_code=pr_diff
            )
            
            if not changes:
                return {
                    'success': False,
                    'error': 'Failed to generate fixes'
                }
            
            # Apply fixes to PR branch
            logger.info('Applying fixes...')
            self._apply_changes(repo, changes, pr.head.ref)
            
            # Add comment to PR
            self.api_helper.add_comment_to_pr(
                pr,
                f'🤖 I\'ve updated the code based on the review feedback.\n\n'
                f'Changes applied:\n{changes.get("commit_message", "Code improvements")}'
            )
            
            return {
                'success': True,
                'updated_pr': pr_number
            }
        
        except Exception as e:
            logger.error(f'Error processing review feedback: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_code_changes(
        self,
        issue_title: str,
        issue_body: str,
        repo_name: str,
        default_branch: str,
        existing_files: List[str]
    ) -> Dict[str, Any]:
        """Generate code changes using LLM"""
        try:
            # Format prompt
            user_prompt = format_code_agent_prompt(
                issue_title=issue_title,
                issue_body=issue_body,
                repo_name=repo_name,
                default_branch=default_branch,
                existing_files=existing_files
            )
            
            # Get response from LLM
            response = self.llm_client.generate(
                system_prompt=CODE_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=float(os.getenv('CODE_AGENT_TEMPERATURE', 0.3))
            )
            
            # Parse JSON response
            changes = self._parse_llm_response(response)
            return changes
        
        except Exception as e:
            logger.error(f'Error generating code changes: {str(e)}')
            return None
    
    def _generate_fixes_from_review(
        self,
        issue_description: str,
        previous_changes: str,
        review_feedback: str,
        current_code: str
    ) -> Dict[str, Any]:
        """Generate fixes based on review feedback"""
        try:
            # Format prompt
            user_prompt = format_review_feedback_prompt(
                issue_description=issue_description,
                previous_changes=previous_changes,
                review_feedback=review_feedback,
                current_code=current_code
            )
            
            # Get response from LLM
            response = self.llm_client.generate(
                system_prompt=CODE_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=float(os.getenv('CODE_AGENT_TEMPERATURE', 0.3))
            )
            
            # Parse JSON response
            changes = self._parse_llm_response(response)
            return changes
        
        except Exception as e:
            logger.error(f'Error generating fixes: {str(e)}')
            return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Extract JSON from markdown code blocks if present
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                response = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                response = response[start:end].strip()
            
            # Parse JSON
            data = json.loads(response)
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse LLM response as JSON: {str(e)}')
            logger.debug(f'Response: {response}')
            return None
    
    def _apply_changes(self, repo, changes: Dict[str, Any], branch: str):
        """Apply code changes to repository"""
        try:
            commit_message = changes.get('commit_message', 'Update code')
            
            # Apply main files
            for file_info in changes.get('files', []):
                path = file_info['path']
                content = file_info['content']
                action = file_info.get('action', 'create')
                
                # Get file SHA if updating
                sha = None
                if action == 'update':
                    try:
                        existing_file = repo.get_contents(path, ref=branch)
                        sha = existing_file.sha
                    except:
                        pass  # File doesn't exist, will create
                
                # Update or create file
                self.api_helper.update_file(
                    repo=repo,
                    path=path,
                    message=f'{commit_message} - {path}',
                    content=content,
                    branch=branch,
                    sha=sha
                )
            
            # Apply test files
            for test_info in changes.get('tests', []):
                path = test_info['path']
                content = test_info['content']
                action = test_info.get('action', 'create')
                
                # Get file SHA if updating
                sha = None
                if action == 'update':
                    try:
                        existing_file = repo.get_contents(path, ref=branch)
                        sha = existing_file.sha
                    except:
                        pass
                
                # Update or create test file
                self.api_helper.update_file(
                    repo=repo,
                    path=path,
                    message=f'{commit_message} - {path}',
                    content=content,
                    branch=branch,
                    sha=sha
                )
            
            logger.info(f'Applied {len(changes.get("files", []))} files and {len(changes.get("tests", []))} test files')
        
        except Exception as e:
            logger.error(f'Error applying changes: {str(e)}')
            raise
    
    def _get_existing_files(self, repo) -> List[str]:
        """Get list of existing files in repository"""
        try:
            contents = repo.get_contents('')
            files = []
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == 'dir':
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    files.append(file_content.path)
            
            return files
        except Exception as e:
            logger.error(f'Error getting existing files: {str(e)}')
            return []
    
    def _create_pr_body(self, issue_number: int, changes: Dict[str, Any]) -> str:
        """Create pull request body"""
        pr_description = changes.get('pr_description', '')
        analysis = changes.get('analysis', '')
        
        body = f"""## Description
{pr_description}

## Analysis
{analysis}

## Changes
- Modified {len(changes.get('files', []))} file(s)
- Added/Updated {len(changes.get('tests', []))} test file(s)

## Related Issue
Closes #{issue_number}

---
🤖 This PR was automatically generated by Code Agent
"""
        return body
