"""
GitHub API Helper
Utility functions for working with GitHub API
"""

import logging
from typing import List, Dict, Any, Optional
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue

logger = logging.getLogger(__name__)


class GitHubAPIHelper:
    """Helper class for GitHub API operations"""
    
    @staticmethod
    def get_repository(github_client: Github, repo_full_name: str) -> Repository:
        """
        Get repository object
        
        Args:
            github_client: Authenticated GitHub client
            repo_full_name: Full repository name (owner/repo)
            
        Returns:
            Repository object
        """
        try:
            return github_client.get_repo(repo_full_name)
        except Exception as e:
            logger.error(f'Error getting repository {repo_full_name}: {str(e)}')
            raise
    
    @staticmethod
    def get_issue(repo: Repository, issue_number: int) -> Issue:
        """
        Get issue object
        
        Args:
            repo: Repository object
            issue_number: Issue number
            
        Returns:
            Issue object
        """
        try:
            return repo.get_issue(issue_number)
        except Exception as e:
            logger.error(f'Error getting issue #{issue_number}: {str(e)}')
            raise
    
    @staticmethod
    def get_pull_request(repo: Repository, pr_number: int) -> PullRequest:
        """
        Get pull request object
        
        Args:
            repo: Repository object
            pr_number: Pull request number
            
        Returns:
            PullRequest object
        """
        try:
            return repo.get_pull(pr_number)
        except Exception as e:
            logger.error(f'Error getting PR #{pr_number}: {str(e)}')
            raise
    
    @staticmethod
    def create_pull_request(
        repo: Repository,
        title: str,
        body: str,
        head: str,
        base: str = 'main'
    ) -> PullRequest:
        """
        Create a pull request
        
        Args:
            repo: Repository object
            title: PR title
            body: PR description
            head: Source branch
            base: Target branch (default: main)
            
        Returns:
            Created PullRequest object
        """
        try:
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            logger.info(f'Created PR #{pr.number}: {title}')
            return pr
        except Exception as e:
            logger.error(f'Error creating pull request: {str(e)}')
            raise
    
    @staticmethod
    def add_comment_to_issue(issue: Issue, comment: str):
        """
        Add comment to issue
        
        Args:
            issue: Issue object
            comment: Comment text
        """
        try:
            issue.create_comment(comment)
            logger.info(f'Added comment to issue #{issue.number}')
        except Exception as e:
            logger.error(f'Error adding comment to issue: {str(e)}')
            raise
    
    @staticmethod
    def add_comment_to_pr(pr: PullRequest, comment: str):
        """
        Add comment to pull request
        
        Args:
            pr: PullRequest object
            comment: Comment text
        """
        try:
            pr.create_issue_comment(comment)
            logger.info(f'Added comment to PR #{pr.number}')
        except Exception as e:
            logger.error(f'Error adding comment to PR: {str(e)}')
            raise
    
    @staticmethod
    def create_review(
        pr: PullRequest,
        body: str,
        event: str = 'COMMENT',
        comments: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Create a review on pull request
        
        Args:
            pr: PullRequest object
            body: Review body
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: List of review comments
        """
        try:
            if comments:
                pr.create_review(
                    body=body,
                    event=event,
                    comments=comments
                )
            else:
                pr.create_review(
                    body=body,
                    event=event
                )
            logger.info(f'Created review on PR #{pr.number}: {event}')
        except Exception as e:
            logger.error(f'Error creating review: {str(e)}')
            raise
    
    @staticmethod
    def get_pr_files(pr: PullRequest) -> List[Any]:
        """
        Get files changed in pull request
        
        Args:
            pr: PullRequest object
            
        Returns:
            List of changed files
        """
        try:
            return list(pr.get_files())
        except Exception as e:
            logger.error(f'Error getting PR files: {str(e)}')
            raise
    
    @staticmethod
    def get_pr_diff(pr: PullRequest) -> str:
        """
        Get pull request diff
        
        Args:
            pr: PullRequest object
            
        Returns:
            Diff string
        """
        try:
            files = GitHubAPIHelper.get_pr_files(pr)
            diff_text = ""
            
            for file in files:
                diff_text += f"\n\n=== {file.filename} ===\n"
                diff_text += f"Status: {file.status}\n"
                diff_text += f"Additions: {file.additions}, Deletions: {file.deletions}\n"
                if file.patch:
                    diff_text += f"\n{file.patch}\n"
            
            return diff_text
        except Exception as e:
            logger.error(f'Error getting PR diff: {str(e)}')
            raise
    
    @staticmethod
    def get_branch_ref(repo: Repository, branch_name: str) -> str:
        """
        Get branch reference
        
        Args:
            repo: Repository object
            branch_name: Branch name
            
        Returns:
            Branch reference
        """
        try:
            return repo.get_branch(branch_name).commit.sha
        except Exception as e:
            logger.error(f'Error getting branch ref: {str(e)}')
            raise
    
    @staticmethod
    def create_branch(repo: Repository, branch_name: str, base_branch: str = 'main'):
        """
        Create a new branch
        
        Args:
            repo: Repository object
            branch_name: New branch name
            base_branch: Base branch to branch from
        """
        try:
            base_ref = GitHubAPIHelper.get_branch_ref(repo, base_branch)
            repo.create_git_ref(
                ref=f'refs/heads/{branch_name}',
                sha=base_ref
            )
            logger.info(f'Created branch: {branch_name}')
        except Exception as e:
            logger.error(f'Error creating branch: {str(e)}')
            raise
    
    @staticmethod
    def update_file(
        repo: Repository,
        path: str,
        message: str,
        content: str,
        branch: str,
        sha: Optional[str] = None
    ):
        """
        Update or create a file in repository
        
        Args:
            repo: Repository object
            path: File path
            message: Commit message
            content: File content
            branch: Branch name
            sha: File SHA (if updating existing file)
        """
        try:
            if sha:
                repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=sha,
                    branch=branch
                )
                logger.info(f'Updated file: {path}')
            else:
                repo.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=branch
                )
                logger.info(f'Created file: {path}')
        except Exception as e:
            logger.error(f'Error updating file {path}: {str(e)}')
            raise
