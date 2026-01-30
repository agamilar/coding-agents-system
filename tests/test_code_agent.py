"""
Tests for Code Agent
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from agents.code_agent import CodeAgent


class TestCodeAgent:
    """Test suite for Code Agent"""
    
    @pytest.fixture
    def mock_github_client(self):
        """Create mock GitHub client"""
        return Mock()
    
    @pytest.fixture
    def code_agent(self, mock_github_client):
        """Create Code Agent instance"""
        with patch('agents.code_agent.LLMClient'):
            agent = CodeAgent(mock_github_client)
            return agent
    
    def test_init(self, code_agent):
        """Test Code Agent initialization"""
        assert code_agent is not None
        assert code_agent.github_client is not None
        assert code_agent.llm_client is not None
    
    def test_parse_llm_response_valid_json(self, code_agent):
        """Test parsing valid JSON response"""
        response = '''```json
{
    "analysis": "Test analysis",
    "files": [{"path": "test.py", "content": "print('hello')", "action": "create"}],
    "tests": [],
    "commit_message": "Test commit"
}
```'''
        
        result = code_agent._parse_llm_response(response)
        
        assert result is not None
        assert result['analysis'] == 'Test analysis'
        assert len(result['files']) == 1
        assert result['files'][0]['path'] == 'test.py'
    
    def test_parse_llm_response_invalid_json(self, code_agent):
        """Test parsing invalid JSON response"""
        response = "This is not JSON"
        
        result = code_agent._parse_llm_response(response)
        
        assert result is None
    
    def test_create_pr_body(self, code_agent):
        """Test PR body creation"""
        issue_number = 123
        changes = {
            'pr_description': 'Test PR',
            'analysis': 'Test analysis',
            'files': [{'path': 'file1.py'}],
            'tests': [{'path': 'test_file1.py'}]
        }
        
        body = code_agent._create_pr_body(issue_number, changes)
        
        assert f'Closes #{issue_number}' in body
        assert 'Test PR' in body
        assert '1 file(s)' in body
        assert '1 test file(s)' in body
    
    @patch('agents.code_agent.GitHubAPIHelper')
    def test_process_issue_success(self, mock_api_helper, code_agent):
        """Test successful issue processing"""
        # Setup mocks
        mock_repo = Mock()
        mock_repo.default_branch = 'main'
        mock_api_helper.return_value.get_repository.return_value = mock_repo
        
        mock_pr = Mock()
        mock_pr.number = 1
        mock_pr.html_url = 'https://github.com/test/repo/pull/1'
        mock_api_helper.return_value.create_pull_request.return_value = mock_pr
        
        code_agent.api_helper = mock_api_helper.return_value
        code_agent._get_existing_files = Mock(return_value=[])
        code_agent._generate_code_changes = Mock(return_value={
            'analysis': 'Test',
            'files': [{'path': 'test.py', 'content': 'test', 'action': 'create'}],
            'tests': [],
            'commit_message': 'Test commit',
            'pr_description': 'Test PR'
        })
        code_agent._apply_changes = Mock()
        
        # Execute
        result = code_agent.process_issue(
            repo_full_name='test/repo',
            issue_number=1,
            issue_title='Test Issue',
            issue_body='Test body'
        )
        
        # Verify
        assert result['success'] is True
        assert result['pr_number'] == 1
        assert 'pr_url' in result
    
    def test_process_issue_no_changes_generated(self, code_agent):
        """Test issue processing when no changes generated"""
        code_agent._get_existing_files = Mock(return_value=[])
        code_agent._generate_code_changes = Mock(return_value=None)
        
        result = code_agent.process_issue(
            repo_full_name='test/repo',
            issue_number=1,
            issue_title='Test Issue',
            issue_body='Test body'
        )
        
        assert result['success'] is False
        assert 'error' in result
