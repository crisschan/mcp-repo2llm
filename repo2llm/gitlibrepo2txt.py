import os
import gitlab
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv

class GitlabRepo2Txt:
    def __init__(self):
        # _=load_dotenv(find_dotenv())
        load_dotenv()
        self.GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
        if not self.GITLAB_TOKEN:
            raise ValueError("Please set 'GITLAB_TOKEN' environment variable or in the script.")
        self.gitlab = gitlab.Gitlab('https://gitlab.com', private_token=self.GITLAB_TOKEN)
        
    def _get_readme_content(self, repo, branch='master'):
        """
        Retrieve the content of the README file.
        """
        readme_variants = ['README.md', 'readme.md', 'ReadMe.md']
        
        for readme_name in readme_variants:
            try:
                readme = repo.files.get(file_path=readme_name, ref=branch)
                return readme.decode().decode('utf-8')
            except:
                continue
        
        return "README not found."

    def _traverse_repo_iteratively(self, repo):
        """
        Traverse the repository iteratively to avoid recursion limits for large repositories.
        """
        # Get default branch
        default_branch = repo.default_branch
        structure = ""
        dirs_to_visit = [("", repo.repository_tree(ref=repo.default_branch, all=True))]
        dirs_visited = set()

        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in tqdm(contents, desc=f"Processing {path}", leave=False):
                if content['type'] == "tree":
                    if content['path'] not in dirs_visited:
                        structure += f"{path}/{content['name']}/\n"
                        dirs_to_visit.append((f"{path}/{content['name']}", repo.repository_tree(path=content['path'], all=True)))
                else:
                    structure += f"{path}/{content['name']}\n"
        return structure

    def _get_file_contents_iteratively(self, repo, branch='master'):
        # Get default branch
        # default_branch = repo.default_branch
        file_contents = ""
        dirs_to_visit = [("", repo.repository_tree(ref=branch, all=True))]
        dirs_visited = set()
        binary_extensions = [
            # Compiled executables and libraries
            '.exe', '.dll', '.so', '.a', '.lib', '.dylib', '.o', '.obj',
            # Compressed archives
            '.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.bz2', '.gz', '.xz', '.z', '.lz', '.lzma', '.lzo', '.rz', '.sz', '.dz',
            # Application-specific files
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
            # Media files (less common)
            '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.wav', '.flac', '.ogg', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.m4a', '.aac',
            # Virtual machine and container images
            '.iso', '.vmdk', '.qcow2', '.vdi', '.vhd', '.vhdx', '.ova', '.ovf',
            # Database files
            '.db', '.sqlite', '.mdb', '.accdb', '.frm', '.ibd', '.dbf',
            # Java-related files
            '.jar', '.class', '.war', '.ear', '.jpi',
            # Python bytecode and packages
            '.pyc', '.pyo', '.pyd', '.egg', '.whl',
            # Other potentially important extensions
            '.deb', '.rpm', '.apk', '.msi', '.dmg', '.pkg', '.bin', '.dat', '.data',
            '.dump', '.img', '.toast', '.vcd', '.crx', '.xpi', '.lockb', 'package-lock.json', '.svg' ,
            '.eot', '.otf', '.ttf', '.woff', '.woff2',
            '.ico', '.icns', '.cur',
            '.cab', '.dmp', '.msp', '.msm',
            '.keystore', '.jks', '.truststore', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.csr',
            '.key', '.pub', '.sig', '.pgp', '.gpg',
            '.nupkg', '.snupkg', '.appx', '.msix', '.msp', '.msu',
            '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
            '.ko', '.sys', '.elf',
            '.swf', '.fla', '.swc',
            '.rlib', '.pdb', '.idb', '.pdb', '.dbg',
            '.sdf', '.bak', '.tmp', '.temp', '.log', '.tlog', '.ilk',
            '.bpl', '.dcu', '.dcp', '.dcpil', '.drc',
            '.aps', '.res', '.rsrc', '.rc', '.resx',
            '.prefs', '.properties', '.ini', '.cfg', '.config', '.conf',
            '.DS_Store', '.localized', '.svn', '.git', '.gitignore', '.gitkeep',
        ]

        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in tqdm(contents, desc=f"Downloading {path}", leave=False):
                if content['type'] == "tree":
                    if content['path'] not in dirs_visited:
                        dirs_to_visit.append((f"{path}/{content['name']}", repo.repository_tree(path=content['path'], all=True)))
                else:
                    # Check if the file extension suggests it's a binary file
                    if any(content['name'].endswith(ext) for ext in binary_extensions):
                        file_contents += f"File: {path}/{content['name']}\nContent: Skipped binary file\n\n"
                    else:
                        file_contents += f"File: {path}/{content['name']}\n"
                        try:
                            file = repo.files.get(file_path=content['path'], ref=branch)
                            decoded_content = file.decode().decode('utf-8')
                            file_contents += f"Content:\n{decoded_content}\n\n"
                        except UnicodeDecodeError:
                            file_contents += "Content: Skipped due to unsupported encoding\n\n"
        return file_contents

    def process_repo(self, repo_url, branch='master'):
        """
        处理GitLab仓库并返回处理后的内容
        
        Args:
            repo_url (str): GitLab仓库URL
            branch (str, optional): 分支名称. 默认为 'master'
            
        Returns:
            tuple: (repo_name, content_string) - 仓库名和处理后的内容字符串
        """
        repo_name = repo_url.split('/')[-1]
        repo = self.gitlab.projects.get(repo_url.replace('https://gitlab.com/', ''))

        # print(f"Getting README for {repo_name}")
        readme_content = self._get_readme_content(repo, branch)

        # print(f"\nGetting repository structure for {repo_name}")
        repo_structure = f"Repository structure: {repo_name}\n"
        repo_structure += self._traverse_repo_iteratively(repo)

        # print(f"\nGetting file contents for {repo_name}")
        file_contents = self._get_file_contents_iteratively(repo, branch)

        instructions = "Use the following files and contents for analysis:\n\n"
        
        # 组合所有内容
        content = (
            instructions +
            f"README:\n{readme_content}\n\n" +
            repo_structure +
            '\n\n' +
            file_contents
        )
        
        return repo_name, content

    def save_repo_contents(self, repo_url, branch='master'):
        """
        处理GitLab仓库并保存到文件
        
        Args:
            repo_url (str): GitLab仓库URL
            branch (str, optional): 分支名称. 默认为 'master'
            
        Returns:
            str: 输出文件的路径
        """
        try:
            repo_name, content = self.process_repo(repo_url, branch)
            output_filename = f'{repo_name}_contents.txt'
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # print(f"Repository contents have been saved to '{output_filename}'.")
            return output_filename
            
        except Exception as e:
            raise Exception(f"Error processing repository: {str(e)}")

# if __name__ == '__main__':
#     repo_url = input("Please enter GitLab repository URL: ")
#     branch = input("Please enter branch name (default is master): ") or "master"
    
#     try:
#         repo_processor = GitlabRepo2Txt()
#         output_file = repo_processor.save_repo_contents(repo_url, branch)
#     except ValueError as ve:
#         # print(f"Error: {ve}")
#     except Exception as e:
#         # print(f"An error occurred: {e}")
#         # print("Please check the repository URL and try again.")
    """
    # 作为模块导入使用
    from repo2llm.gitlibrepo2txt import GitlabRepo2Txt

    # 创建实例
    repo_processor = GitlabRepo2Txt()

    # 方式1：直接保存到文件
    output_file = repo_processor.save_repo_contents(
        repo_url="https://gitlab.com/username/repo",
        branch="master"  # 可选参数
    )

    # 方式2：获取处理后的内容
    repo_name, content = repo_processor.process_repo(
        repo_url="https://gitlab.com/username/repo",
        branch="master"  # 可选参数
    )
    """