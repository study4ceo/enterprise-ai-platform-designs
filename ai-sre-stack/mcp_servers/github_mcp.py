"""GitHub MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
from github import Github, GithubException
import logging

logger = logging.getLogger(__name__)


class GitHubMCP(BaseMCPServer):
    """GitHub MCP server for repository, PR, and issue management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize GitHub MCP server."""
        super().__init__("GitHub", MCPCategory.CICD, config)
        self.github = None
        self.repo = None
        self.org_name = config.get('org')
        self.repo_name = config.get('repo')
        
    async def _connect(self):
        """Connect to GitHub API."""
        try:
            self.github = Github(self.config.get('token'))
            if self.org_name and self.repo_name:
                self.repo = self.github.get_repo(f"{self.org_name}/{self.repo_name}")
            logger.info(f"Connected to GitHub: {self.org_name}/{self.repo_name}")
        except Exception as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current GitHub repository state.
        
        Returns:
            Current PRs, issues, and repository health
        """
        try:
            if not self.repo:
                return {"error": "No repository configured", "status": "unhealthy"}
            
            # Get open pull requests
            prs = self.repo.get_pulls(state='open')
            pr_list = []
            for pr in prs:
                pr_list.append({
                    "number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "created_at": str(pr.created_at),
                    "mergeable": pr.mergeable,
                    "draft": pr.draft,
                    "url": pr.html_url
                })
            
            # Get open issues
            issues = self.repo.get_issues(state='open')
            issue_list = []
            for issue in issues:
                if not issue.pull_request:  # Filter out PRs
                    issue_list.append({
                        "number": issue.number,
                        "title": issue.title,
                        "author": issue.user.login,
                        "created_at": str(issue.created_at),
                        "labels": [label.name for label in issue.labels],
                        "url": issue.html_url
                    })
            
            # Get recent commits
            commits = self.repo.get_commits()[:5]
            commit_list = []
            for commit in commits:
                commit_list.append({
                    "sha": commit.sha[:7],
                    "message": commit.commit.message.split('\n')[0],
                    "author": commit.commit.author.name,
                    "date": str(commit.commit.author.date)
                })
            
            # Get workflow runs (GitHub Actions)
            workflows = self.repo.get_workflows()
            workflow_status = []
            for workflow in workflows:
                runs = workflow.get_runs()[:1]  # Latest run
                if runs.totalCount > 0:
                    latest_run = runs[0]
                    workflow_status.append({
                        "name": workflow.name,
                        "status": latest_run.status,
                        "conclusion": latest_run.conclusion,
                        "created_at": str(latest_run.created_at)
                    })
            
            return {
                "status": "healthy",
                "pull_requests": pr_list[:10],
                "pr_count": len(pr_list),
                "issues": issue_list[:10],
                "issue_count": len(issue_list),
                "recent_commits": commit_list,
                "workflows": workflow_status
            }
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "create_issue":
                return await self._create_issue(params)
            elif action == "comment_pr":
                return await self._comment_on_pr(params)
            elif action == "merge_pr":
                return await self._merge_pr(params)
            elif action == "create_pr":
                return await self._create_pr(params)
            elif action == "get_file":
                return await self._get_file(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue."""
        title = params.get('title')
        body = params.get('body', '')
        labels = params.get('labels', [])
        
        issue = self.repo.create_issue(title=title, body=body, labels=labels)
        return {"success": True, "issue_number": issue.number, "url": issue.html_url}
    
    async def _comment_on_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Comment on a pull request."""
        pr_number = params.get('pr_number')
        comment = params.get('comment')
        
        pr = self.repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        return {"success": True, "message": f"Comment added to PR #{pr_number}"}
    
    async def _merge_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge a pull request."""
        pr_number = params.get('pr_number')
        commit_message = params.get('commit_message', '')
        
        pr = self.repo.get_pull(pr_number)
        merge_result = pr.merge(commit_message=commit_message)
        
        return {"success": merge_result.merged, "message": f"PR #{pr_number} merged"}
    
    async def _create_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new pull request."""
        title = params.get('title')
        body = params.get('body', '')
        head = params.get('head')
        base = params.get('base', 'main')
        
        pr = self.repo.create_pull(title=title, body=body, head=head, base=base)
        return {"success": True, "pr_number": pr.number, "url": pr.html_url}
    
    async def _get_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file contents from repository."""
        file_path = params.get('path')
        ref = params.get('ref', 'main')
        
        file_content = self.repo.get_contents(file_path, ref=ref)
        return {"success": True, "content": file_content.decoded_content.decode()}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform GitHub-specific health check."""
        try:
            user = self.github.get_user()
            return {"user": user.login, "message": "GitHub API accessible"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available GitHub capabilities."""
        return [
            "create_issue",
            "comment_pr",
            "merge_pr",
            "create_pr",
            "get_file",
            "list_prs",
            "list_issues",
            "get_workflows"
        ]
