"""
Git Helper Utilities
Helper functions for Git operations
"""

import os
import logging
from typing import List, Optional
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)


class GitHelper:
    """Helper class for Git operations"""
    
    def __init__(self, repo_path: str = '.'):
        """
        Initialize Git helper
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self.repo = None
        
        try:
            self.repo = Repo(repo_path)
            logger.info(f'Git repository loaded: {repo_path}')
        except Exception as e:
            logger.warning(f'Not a git repository: {str(e)}')
    
    def clone_repository(self, clone_url: str, destination: str) -> bool:
        """
        Clone a repository
        
        Args:
            clone_url: Repository URL
            destination: Destination path
            
        Returns:
            True if successful
        """
        try:
            self.repo = Repo.clone_from(clone_url, destination)
            self.repo_path = destination
            logger.info(f'Cloned repository to {destination}')
            return True
        except GitCommandError as e:
            logger.error(f'Failed to clone repository: {str(e)}')
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """
        Get current branch name
        
        Returns:
            Branch name or None
        """
        if not self.repo:
            return None
        
        try:
            return self.repo.active_branch.name
        except Exception as e:
            logger.error(f'Error getting current branch: {str(e)}')
            return None
    
    def create_branch(self, branch_name: str, base_branch: str = 'main') -> bool:
        """
        Create a new branch
        
        Args:
            branch_name: New branch name
            base_branch: Base branch to branch from
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            # Checkout base branch
            self.repo.git.checkout(base_branch)
            
            # Create and checkout new branch
            self.repo.git.checkout('-b', branch_name)
            logger.info(f'Created branch: {branch_name}')
            return True
        
        except GitCommandError as e:
            logger.error(f'Failed to create branch: {str(e)}')
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout a branch
        
        Args:
            branch_name: Branch name to checkout
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            self.repo.git.checkout(branch_name)
            logger.info(f'Checked out branch: {branch_name}')
            return True
        except GitCommandError as e:
            logger.error(f'Failed to checkout branch: {str(e)}')
            return False
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Commit changes
        
        Args:
            message: Commit message
            files: List of files to commit (None for all)
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            # Add files
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add('-A')
            
            # Commit
            self.repo.index.commit(message)
            logger.info(f'Committed changes: {message}')
            return True
        
        except GitCommandError as e:
            logger.error(f'Failed to commit: {str(e)}')
            return False
    
    def push_changes(self, branch_name: Optional[str] = None) -> bool:
        """
        Push changes to remote
        
        Args:
            branch_name: Branch to push (current branch if None)
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            if branch_name:
                self.repo.git.push('origin', branch_name)
            else:
                self.repo.git.push()
            
            logger.info('Pushed changes to remote')
            return True
        
        except GitCommandError as e:
            logger.error(f'Failed to push: {str(e)}')
            return False
    
    def get_diff(self, base: str = 'HEAD', compare: Optional[str] = None) -> str:
        """
        Get diff between commits
        
        Args:
            base: Base commit/branch
            compare: Compare commit/branch (working directory if None)
            
        Returns:
            Diff string
        """
        if not self.repo:
            return ''
        
        try:
            if compare:
                return self.repo.git.diff(base, compare)
            else:
                return self.repo.git.diff(base)
        except GitCommandError as e:
            logger.error(f'Failed to get diff: {str(e)}')
            return ''
    
    def get_changed_files(self) -> List[str]:
        """
        Get list of changed files
        
        Returns:
            List of changed file paths
        """
        if not self.repo:
            return []
        
        try:
            # Get both staged and unstaged changes
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            changed_files.extend([item.a_path for item in self.repo.index.diff('HEAD')])
            
            # Get untracked files
            untracked = self.repo.untracked_files
            changed_files.extend(untracked)
            
            return list(set(changed_files))
        
        except Exception as e:
            logger.error(f'Failed to get changed files: {str(e)}')
            return []
    
    def is_clean(self) -> bool:
        """
        Check if working directory is clean
        
        Returns:
            True if no changes
        """
        if not self.repo:
            return True
        
        return not self.repo.is_dirty() and not self.repo.untracked_files
    
    def pull_changes(self, branch_name: Optional[str] = None) -> bool:
        """
        Pull changes from remote
        
        Args:
            branch_name: Branch to pull (current branch if None)
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            if branch_name:
                self.repo.git.pull('origin', branch_name)
            else:
                self.repo.git.pull()
            
            logger.info('Pulled changes from remote')
            return True
        
        except GitCommandError as e:
            logger.error(f'Failed to pull: {str(e)}')
            return False
