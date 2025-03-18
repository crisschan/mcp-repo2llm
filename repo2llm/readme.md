# RepoToTextForLLMs
> this repo is forked from  is forked from https://github.com/Doriandarko/RepoToTextForLLMs
Automates the analysis of GitHub, GitLab, and local repositories specifically tailored for usage with large context LLMs. These Python scripts efficiently fetch README files, repository structure, and non-binary file contents. Additionally, they provide structured outputs complete with pre-formatted prompts to guide further analysis of the repository's content.

## Features

- **README Retrieval:** Automatically extracts the content of README.md (with multiple case variants) to provide an initial insight into the repository.
- **Structured Repository Traversal:** Maps out the repository's structure through an iterative traversal method, ensuring thorough coverage without the limitations of recursion.
- **Selective Content Extraction:** Retrieves text contents from files, intelligently skipping over binary files to streamline the analysis process.
- **Multi-Platform Support:** Works with GitHub repositories, GitLab repositories, and local Git repositories.
- **Branch Support:** Allows specifying different branches for content retrieval.

## Prerequisites

To use **RepoToTextForLLMs**, you'll need:

- Python installed on your system
- Required Python packages:
  - `PyGithub` for GitHub repositories
  - `python-gitlab` for GitLab repositories
  - `tqdm` for progress bars
  - `python-dotenv` for environment variable management
- Access tokens (for remote repositories):
  - GitHub Personal Access Token configured as `GITHUB_TOKEN`
  - GitLab Personal Access Token configured as `GITLAB_TOKEN`

## Getting Started

1. Install the required packages:

```bash
pip install PyGithub python-gitlab tqdm python-dotenv
```

2. Set your GitHub Personal Access Token as an environment variable:

```python
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'YOUR TOKEN HERE')
```

## How to Use

1. Place the script in your desired directory.
2. Execute the script in your terminal:

```bash
python repototxt.py
```

3. Enter the GitHub repository URL when prompted. The script will process the repository and output its findings, including the README, structure, and file contents (excluding binary files), accompanied by analysis prompts.

## Contributing

Contributions to **RepoToTextForLLMs** are welcomed. Whether it's through submitting pull requests, reporting issues, or suggesting improvements, your input helps make this tool better for everyone.

## License

This project is licensed under the MIT License.
