# MCP-Repo2LLM
## Overview
mcp-repo2llm is a MCP server  that transforms code repositories into LLM-friendly formats.
A powerful tool that transforms code repositories into LLM-friendly formats, bridging the gap between traditional code bases and modern AI language models.

## Motivation

As AI and Large Language Models (LLMs) become increasingly important in software development, there's a growing need to effectively communicate our codebases to these models. Traditional code repositories aren't optimized for LLM processing, which can lead to suboptimal results when using AI tools for code analysis and generation.

## Problem Solved

This project addresses several critical challenges:
- Difficulty in processing large codebases with LLMs
- Loss of context and structure when feeding code to AI models
- Inefficient handling of repository metadata and documentation
- Inconsistent formatting across different programming languages

## Key Features

- **Smart Repository Scanning**: Intelligently processes entire codebases while maintaining structural integrity
- **Context Preservation**: Maintains important contextual information and relationships between code files
- **Multi-language Support**: Handles various programming languages with language-specific optimizations
- **Metadata Enhancement**: Enriches code with relevant metadata for better LLM understanding
- **Efficient Processing**: Optimized for handling large repositories with minimal resource usage

## Installation

To install mcp-repo2llm by uv:
```
"mcp-repo2llm-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "/mcp-repo2llm",
        "mcp",
        "run",
        "/mcp-repo2llm/mcp-repo2llm-server.py"
      ],
      "env":{
          "GITHUB_TOKEN":"your-github-token",
          "GITLAB_TOKEN":"your-gitlab-token"
      }
    }
```
GITHUB_TOKEN: your github token
GITLAB_TOKEN: your gitlab token
## Tools
### get_gitlab_repo
- Process and return the code from a GitLab repository branch as text
- Input:
    - repo_url (string): the repository URL from gitlab
    - branch (string): The branch name,default is master
- Returns(string): The project all information and struction from the repository as text
### get_github_repo
- Process and return the code from a Github repository branch as text
- Input:
    - repo_url (string): the repository URL from github
    - branch (string): The branch name,default is master
- Returns(string): The project all information and struction from the repository as text
### get_local_repo
- Process and return the code from a GitLab repository branch as text
- Input:
    - repo_url (string): the repository  path 
- Returns(string): The project all information and struction from the repository as text