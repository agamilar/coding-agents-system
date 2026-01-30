"""
Review Agent
Performs automated code review on pull requests
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from github import Github

from github_app.api import GitHubAPIHelper
from utils.llm import LLMClient
from agents.prompts import (
    REVIEW_AGENT_SYSTEM_PROMPT,
    format_review_agent_prompt
)

logger = logging.getLogger(__name__)


class ReviewAgent:
    """Agent for reviewing code changes in pull requests"""
    
    def __init__(self, github_client: Github):
        """
        Initialize Review Agent
        
        Args:
            github_client: Authenticated GitHub client
        """
        self.github_client = github_client
        self.llm_client = LLMClient()
        self.api_helper = GitHubAPIHelper()
        self.min_test_coverage = int(os.getenv('MIN_TEST_COVERAGE', 80))
    
    def review_pull_request(
        self,
        repo_full_name: str,
        pr_number: int,
        issue_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Review a pull request
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
            issue_number: Related issue number (optional)
            
        Returns:
            Dict with review results
        """
        try:
            logger.info(f'Reviewing PR #{pr_number} in {repo_full_name}')
            
            # Get repository and PR
            repo = self.api_helper.get_repository(self.github_client, repo_full_name)
            pr = self.api_helper.get_pull_request(repo, pr_number)
            
            # Get issue description if available
            issue_description = ''
            if issue_number:
                try:
                    issue = self.api_helper.get_issue(repo, issue_number)
                    issue_description = f'{issue.title}\n\n{issue.body}'
                except:
                    issue_description = 'No issue description available'
            else:
                issue_description = pr.body or 'No description provided'
            
            # Get PR diff and files
            pr_diff = self.api_helper.get_pr_diff(pr)
            changed_files = [f.filename for f in self.api_helper.get_pr_files(pr)]
            
            # Get CI/CD results
            ci_results = self._get_ci_results(pr)
            
            # Get test coverage (if available)
            test_coverage = self._estimate_test_coverage(changed_files)
            
            # Perform review using LLM
            logger.info('Generating review...')
            review_data = self._generate_review(
                issue_description=issue_description,
                pr_diff=pr_diff,
                changed_files=changed_files,
                ci_results=ci_results,
                test_coverage=test_coverage
            )
            
            if not review_data:
                return {
                    'success': False,
                    'error': 'Failed to generate review'
                }
            
            # Post review to PR
            logger.info('Posting review...')
            self._post_review(pr, review_data)
            
            # Add summary comment
            self._post_summary_comment(pr, review_data)
            
            return {
                'success': True,
                'assessment': review_data.get('overall_assessment'),
                'pr_number': pr_number
            }
        
        except Exception as e:
            logger.error(f'Error reviewing PR: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_review(
        self,
        issue_description: str,
        pr_diff: str,
        changed_files: List[str],
        ci_results: str,
        test_coverage: str
    ) -> Optional[Dict[str, Any]]:
        """Generate review using LLM"""
        try:
            # Format prompt
            user_prompt = format_review_agent_prompt(
                issue_description=issue_description,
                pr_diff=pr_diff,
                changed_files=changed_files,
                ci_results=ci_results,
                test_coverage=test_coverage
            )
            
            # Get response from LLM
            response = self.llm_client.generate(
                system_prompt=REVIEW_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=float(os.getenv('REVIEW_AGENT_TEMPERATURE', 0.2))
            )
            
            # Parse JSON response
            review_data = self._parse_llm_response(response)
            return review_data
        
        except Exception as e:
            logger.error(f'Error generating review: {str(e)}')
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
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
    
    def _post_review(self, pr, review_data: Dict[str, Any]):
        """Post review to pull request"""
        try:
            # Prepare review body
            body = self._format_review_body(review_data)
            
            # Prepare inline comments
            comments = []
            for comment_data in review_data.get('specific_comments', []):
                # Note: GitHub API requires position (line in diff), not line number
                # For simplicity, we'll post these as general comments
                pass
            
            # Determine review event
            assessment = review_data.get('overall_assessment', 'COMMENT')
            event_map = {
                'APPROVE': 'APPROVE',
                'REQUEST_CHANGES': 'REQUEST_CHANGES',
                'COMMENT': 'COMMENT'
            }
            event = event_map.get(assessment, 'COMMENT')
            
            # Create review
            self.api_helper.create_review(
                pr=pr,
                body=body,
                event=event,
                comments=comments if comments else None
            )
            
            logger.info(f'Posted {event} review')
        
        except Exception as e:
            logger.error(f'Error posting review: {str(e)}')
            raise
    
    def _post_summary_comment(self, pr, review_data: Dict[str, Any]):
        """Post summary comment with detailed feedback"""
        try:
            comment = self._format_summary_comment(review_data)
            self.api_helper.add_comment_to_pr(pr, comment)
            logger.info('Posted summary comment')
        
        except Exception as e:
            logger.error(f'Error posting summary comment: {str(e)}')
    
    def _format_review_body(self, review_data: Dict[str, Any]) -> str:
        """Format review body"""
        summary = review_data.get('summary', 'Code review completed')
        assessment = review_data.get('overall_assessment', 'COMMENT')
        
        emoji_map = {
            'APPROVE': '✅',
            'REQUEST_CHANGES': '🔄',
            'COMMENT': '💬'
        }
        emoji = emoji_map.get(assessment, '💬')
        
        body = f"""## {emoji} AI Review Agent

**Overall Assessment:** {assessment}

### Summary
{summary}

---
🤖 Automated review by AI Review Agent
"""
        return body
    
    def _format_summary_comment(self, review_data: Dict[str, Any]) -> str:
        """Format detailed summary comment"""
        comment_parts = ['## 📊 Detailed Review Analysis\n']
        
        # Scores
        comment_parts.append('### Scores')
        correctness = review_data.get('correctness', {})
        code_quality = review_data.get('code_quality', {})
        tests = review_data.get('tests', {})
        
        comment_parts.append(f"- **Correctness:** {correctness.get('score', 'N/A')}/10")
        comment_parts.append(f"- **Code Quality:** {code_quality.get('score', 'N/A')}/10")
        comment_parts.append(f"- **Tests:** {tests.get('score', 'N/A')}/10")
        comment_parts.append('')
        
        # CI Checks
        ci_checks = review_data.get('ci_checks', {})
        passing = ci_checks.get('passing', False)
        comment_parts.append(f"### CI/CD Status: {'✅ Passing' if passing else '❌ Failing'}")
        
        if not passing:
            failed = ci_checks.get('failed_checks', [])
            if failed:
                comment_parts.append('\nFailed checks:')
                for check in failed:
                    comment_parts.append(f'- {check}')
        comment_parts.append('')
        
        # Required Changes
        required = review_data.get('required_changes', [])
        if required:
            comment_parts.append('### ⚠️ Required Changes')
            for change in required:
                comment_parts.append(f'- {change}')
            comment_parts.append('')
        
        # Issues by category
        if correctness.get('issues'):
            comment_parts.append('### Correctness Issues')
            for issue in correctness['issues']:
                comment_parts.append(f'- {issue}')
            comment_parts.append('')
        
        if code_quality.get('issues'):
            comment_parts.append('### Code Quality Issues')
            for issue in code_quality['issues']:
                comment_parts.append(f'- {issue}')
            comment_parts.append('')
        
        if tests.get('issues'):
            comment_parts.append('### Test Issues')
            for issue in tests['issues']:
                comment_parts.append(f'- {issue}')
            comment_parts.append('')
        
        # Optional Suggestions
        suggestions = review_data.get('optional_suggestions', [])
        if suggestions:
            comment_parts.append('### 💡 Optional Suggestions')
            for suggestion in suggestions:
                comment_parts.append(f'- {suggestion}')
            comment_parts.append('')
        
        # Praise
        praise = review_data.get('praise', [])
        if praise:
            comment_parts.append('### ⭐ Good Practices')
            for item in praise:
                comment_parts.append(f'- {item}')
            comment_parts.append('')
        
        # Specific Comments
        specific = review_data.get('specific_comments', [])
        if specific:
            comment_parts.append('### 📝 Specific Comments')
            for comment in specific:
                file = comment.get('file', 'unknown')
                line = comment.get('line', 'N/A')
                text = comment.get('comment', '')
                comment_parts.append(f'- **{file}:{line}** - {text}')
            comment_parts.append('')
        
        return '\n'.join(comment_parts)
    
    def _get_ci_results(self, pr) -> str:
        """Get CI/CD check results"""
        try:
            # Get the latest commit
            commits = list(pr.get_commits())
            if not commits:
                return 'No commits found'
            
            latest_commit = commits[-1]
            
            # Get check runs
            check_runs = latest_commit.get_check_runs()
            
            if check_runs.totalCount == 0:
                return 'No CI checks configured'
            
            results = []
            for check_run in check_runs:
                status = check_run.status
                conclusion = check_run.conclusion or 'in_progress'
                results.append(f'{check_run.name}: {status} ({conclusion})')
            
            return '\n'.join(results)
        
        except Exception as e:
            logger.error(f'Error getting CI results: {str(e)}')
            return 'Unable to fetch CI results'
    
    def _estimate_test_coverage(self, changed_files: List[str]) -> str:
        """Estimate test coverage based on changed files"""
        try:
            # Simple heuristic: check if there are test files
            test_files = [f for f in changed_files if 'test' in f.lower()]
            code_files = [f for f in changed_files if f.endswith('.py') and 'test' not in f.lower()]
            
            if not code_files:
                return 'No code files changed'
            
            if not test_files:
                return f'{len(code_files)} code file(s) changed, but no test files found'
            
            return f'{len(test_files)} test file(s) for {len(code_files)} code file(s)'
        
        except Exception as e:
            logger.error(f'Error estimating test coverage: {str(e)}')
            return 'Unable to estimate coverage'
