"""
Tests for Review Agent
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from agents.review_agent import ReviewAgent


class TestReviewAgent:
    """Test suite for Review Agent"""
    
    @pytest.fixture
    def mock_github_client(self):
        """Create mock GitHub client"""
        return Mock()
    
    @pytest.fixture
    def review_agent(self, mock_github_client):
        """Create Review Agent instance"""
        with patch('agents.review_agent.LLMClient'):
            agent = ReviewAgent(mock_github_client)
            return agent
    
    def test_init(self, review_agent):
        """Test Review Agent initialization"""
        assert review_agent is not None
        assert review_agent.github_client is not None
        assert review_agent.llm_client is not None
    
    def test_parse_llm_response_valid_json(self, review_agent):
        """Test parsing valid JSON response"""
        response = '''```json
{
    "overall_assessment": "APPROVE",
    "summary": "Good code",
    "correctness": {"score": 9, "issues": []},
    "code_quality": {"score": 8, "issues": []},
    "tests": {"score": 7, "issues": [], "coverage": "85%"},
    "ci_checks": {"passing": true, "failed_checks": []},
    "specific_comments": [],
    "required_changes": [],
    "optional_suggestions": [],
    "praise": ["Well structured"]
}
```'''
        
        result = review_agent._parse_llm_response(response)
        
        assert result is not None
        assert result['overall_assessment'] == 'APPROVE'
        assert result['correctness']['score'] == 9
    
    def test_format_review_body(self, review_agent):
        """Test review body formatting"""
        review_data = {
            'overall_assessment': 'APPROVE',
            'summary': 'Excellent code quality'
        }
        
        body = review_agent._format_review_body(review_data)
        
        assert 'APPROVE' in body
        assert 'Excellent code quality' in body
        assert '✅' in body
    
    def test_format_summary_comment(self, review_agent):
        """Test summary comment formatting"""
        review_data = {
            'correctness': {'score': 9, 'issues': []},
            'code_quality': {'score': 8, 'issues': ['Minor style issue']},
            'tests': {'score': 7, 'issues': [], 'coverage': '85%'},
            'ci_checks': {'passing': True, 'failed_checks': []},
            'required_changes': ['Fix typo'],
            'optional_suggestions': ['Consider using type hints'],
            'praise': ['Good error handling']
        }
        
        comment = review_agent._format_summary_comment(review_data)
        
        assert 'Scores' in comment
        assert '9/10' in comment
        assert 'Fix typo' in comment
        assert 'Good error handling' in comment
    
    def test_estimate_test_coverage_with_tests(self, review_agent):
        """Test coverage estimation with test files"""
        changed_files = ['src/main.py', 'tests/test_main.py']
        
        coverage = review_agent._estimate_test_coverage(changed_files)
        
        assert '1 test file(s) for 1 code file(s)' in coverage
    
    def test_estimate_test_coverage_no_tests(self, review_agent):
        """Test coverage estimation without test files"""
        changed_files = ['src/main.py', 'src/utils.py']
        
        coverage = review_agent._estimate_test_coverage(changed_files)
        
        assert 'no test files found' in coverage.lower()
    
    @patch('agents.review_agent.GitHubAPIHelper')
    def test_review_pull_request_success(self, mock_api_helper, review_agent):
        """Test successful PR review"""
        # Setup mocks
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.body = 'Closes #123'
        mock_pr.number = 1
        
        mock_api_helper.return_value.get_repository.return_value = mock_repo
        mock_api_helper.return_value.get_pull_request.return_value = mock_pr
        mock_api_helper.return_value.get_issue.return_value = Mock(
            title='Test Issue',
            body='Test body'
        )
        mock_api_helper.return_value.get_pr_diff.return_value = 'test diff'
        mock_api_helper.return_value.get_pr_files.return_value = [
            Mock(filename='test.py')
        ]
        
        review_agent.api_helper = mock_api_helper.return_value
        review_agent._get_ci_results = Mock(return_value='All checks passed')
        review_agent._estimate_test_coverage = Mock(return_value='Good coverage')
        review_agent._generate_review = Mock(return_value={
            'overall_assessment': 'APPROVE',
            'summary': 'Good work'
        })
        review_agent._post_review = Mock()
        review_agent._post_summary_comment = Mock()
        
        # Execute
        result = review_agent.review_pull_request(
            repo_full_name='test/repo',
            pr_number=1,
            issue_number=123
        )
        
        # Verify
        assert result['success'] is True
        assert result['assessment'] == 'APPROVE'
