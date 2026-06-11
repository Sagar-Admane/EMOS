from github import Github
from app.utils.text_extension import TEXT_EXTENSIONS

class GithubService:
    def __init__(self, token: str):
        self.client = Github(token)

    def get_repository(self, repo_name: str):
        return self.client.get_repo(repo_name)
    
    def get_commits(self, repo_name: str):
        repo = self.client.get_repo(repo_name)
        return repo.get_commits()
    
    def get_pull_requests(self, repo_name: str):
        repo = self.client.get_repo(repo_name)
        return repo.get_pulls(state="all")
    
    def get_branches(self, repo_name: str):
        repo = self.client.get_repo(repo_name)
        return repo.get_branches()
    
    def get_contributors(self, repo_name: str):
        repo = self.client.get_repo(repo_name)
        return repo.get_contributors()
    
    def get_repository_tree(self, repo_name:str):
        repo = self.client.get_repo(repo_name)
        tree = repo.get_git_tree(repo.default_branch, recursive=True)
        return tree.tree
    
    def get_commit(self, repo_name: str, sha: str):
        repo = self.client.get_repo(repo_name)
        return repo.get_commit(sha)
    
    def get_file_content(self, repo_name: str, path: str):
        repo = self.client.get_repo(repo_name)

        if(path not in TEXT_EXTENSIONS):
            return None
        content = repo.get_contents(path)

        return content.decoded_content.decode("utf-8")
    
    def get_pr_reviews(self, repo_id: int, pull_number: int):
        repo = self.client.get_repo(repo_id)
        prs = repo.get_pull(pull_number)
        return prs.get_reviews()