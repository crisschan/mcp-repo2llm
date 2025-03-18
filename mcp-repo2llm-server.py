import asyncio
from mcp.server.fastmcp import FastMCP
from repo2llm import GitlabRepo2Txt, GithubRepo2Txt, LocalRepo2Txt
# import logging
# logging.basicConfig(
#     filename='repo2llm.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

MCP_SERVER_NAME="mcp-repo2llm-server"
mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
async def get_gitlab_repo(repo_url: str, branch: str = "master")->str:
    """
    Process and return the code from a GitLab repository branch as text
    """
    try:
        repo_processor = GitlabRepo2Txt()
        repo_name, content = repo_processor.process_repo(
        repo_url=repo_url,
        branch=branch  # optional parameter
        )
        # logger.info(f"Processed GitLab repository: {repo_name}")
        # logger.info(f"Processed GitLab content: {content}")
        return content
    except Exception as e:
        # print(f"Error processing GitLab repository: {e}")
        return None

@mcp.tool()
async def get_github_repo(repo_url: str, branch: str = "master")->str:
    """
    Process and return the code from a GitHub repository branch as text
    """
    try:
        # Create an event loop
        loop = asyncio.get_event_loop()
        # Wrap synchronous operation in async operation with 300 seconds (5 minutes) timeout
        repo_processor = GithubRepo2Txt()
        repo_name, content = await asyncio.wait_for(
            loop.run_in_executor(None, repo_processor.process_repo, repo_url, branch),
            timeout=3000
        )
        # logger.info(f"Processed GitLab repository: {repo_name}")

        return content
    except asyncio.TimeoutError:
        return "Processing timeout, please check repository size or network connection"
    except Exception as e:
        # logger.error(f"Error processing GitLab repository: {e}")
        return f"Processing failed: {str(e)}"

@mcp.tool()
async def get_local_repo(repo_path: str)->str:
    """
    Process and return the code from a local repository as text
    """
    try:
        # Create an event loop
        loop = asyncio.get_event_loop()
        # Wrap synchronous operation in async operation with 300 seconds (5 minutes) timeout
        repo_processor = LocalRepo2Txt()
        repo_name, content = await asyncio.wait_for(
            loop.run_in_executor(None, repo_processor.process_repo, repo_path),
            timeout=300
        )
        return content
    except asyncio.TimeoutError:
        return "Processing timeout, please check repository size or file count"
    except Exception as e:
        return f"Processing failed: {str(e)}"
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')