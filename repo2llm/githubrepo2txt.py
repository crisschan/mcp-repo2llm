import os
from github import Github
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv

class GithubRepo2Txt:
    def __init__(self):
        # _=load_dotenv(find_dotenv())
        load_dotenv()
        # GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')    
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        if not self.GITHUB_TOKEN:
            raise ValueError("Please set 'GITHUB_TOKEN' env param")
        self.github = Github(self.GITHUB_TOKEN)
        
    def _get_readme_content(self, repo, branch='master'):
        """
        Retrieve the content of the README file.
        """
        readme_variants = ['README.md', 'readme.md', 'ReadMe.md']
        for readme in readme_variants:
            try:
                readme = repo.get_contents(readme,ref=branch)
                return readme.decoded_content.decode('utf-8')
            except:
                continue
        return "README not found."

    def _traverse_repo_iteratively(self, repo, branch='master'):
        """
        Traverse the repository iteratively to avoid recursion limits for large repositories.
        """
        structure = ""
        dirs_to_visit = [("", repo.get_contents("", ref=branch))]
        dirs_visited = set()

        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in tqdm(contents, desc=f"Processing {path}", leave=False):
                if content.type == "dir":
                    if content.path not in dirs_visited:
                        structure += f"{path}/{content.name}/\n"
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path, ref=branch)))
                else:
                    structure += f"{path}/{content.name}\n"
        return structure

    def _get_file_contents_iteratively(self, repo, branch='master'):
        file_contents = ""
        dirs_to_visit = [("", repo.get_contents("", ref=branch))]
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
                if content.type == "dir":
                    if content.path not in dirs_visited:
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path, ref=branch)))
                else:
                    # Check if the file extension suggests it's a binary file
                    if any(content.name.endswith(ext) for ext in binary_extensions):
                        file_contents += f"File: {path}/{content.name}\nContent: Skipped binary file\n\n"
                    else:
                        file_contents += f"File: {path}/{content.name}\n"
                        try:
                            if content.encoding is None or content.encoding == 'none':
                                file_contents += "Content: Skipped due to missing encoding\n\n"
                            else:
                                try:
                                    decoded_content = content.decoded_content.decode('utf-8')
                                    file_contents += f"Content:\n{decoded_content}\n\n"
                                except UnicodeDecodeError:
                                    try:
                                        decoded_content = content.decoded_content.decode('latin-1')
                                        file_contents += f"Content (Latin-1 Decoded):\n{decoded_content}\n\n"
                                    except UnicodeDecodeError:
                                        file_contents += "Content: Skipped due to unsupported encoding\n\n"
                        except (AttributeError, UnicodeDecodeError):
                            file_contents += "Content: Skipped due to decoding error or missing decoded_content\n\n"
        return file_contents

    def process_repo(self, repo_url, branch='master'):
        """
        处理GitHub仓库并返回处理后的内容
        
        Args:
            repo_url (str): GitHub仓库URL
            branch (str, optional): 分支名称. 默认为 'master'
            
        Returns:
            tuple: (repo_name, content_string) - 仓库名和处理后的内容字符串
        """
        repo_name = repo_url.split('/')[-1]
        repo = self.github.get_repo(repo_url.replace('https://github.com/', ''))

        # print(f"Getting {repo_name}'s README")
        readme_content = self._get_readme_content(repo, branch)

        # print(f"\nGetting {repo_name}'s repo structure")
        repo_structure = f"repo structure: {repo_name}\n"
        repo_structure += self._traverse_repo_iteratively(repo, branch)

        # print(f"\nGetting {repo_name}'s file")
        file_contents = self._get_file_contents_iteratively(repo, branch)

        instructions = "Please analyze using the following provided files and contents:\n\n"
        
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
        处理GitHub仓库并保存到文件
        
        Args:
            repo_url (str): GitHub仓库URL
            branch (str, optional): 分支名称. 默认为 'master'
            
        Returns:
            str: 输出文件的路径
        """
        try:
            repo_name, content = self.process_repo(repo_url, branch)
            output_filename = f'{repo_name}_contents.txt'
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # print(f"Repository contents saved to '{output_filename}'.")
            return output_filename
            
        except Exception as e:
            raise Exception(f"Error processing repository: {str(e)}")

# if __name__ == '__main__':

#     repo_url = input("please input GitHub repo URL: ")
#     branch = input("please input the branch(default: master): ") or "master"
    
#     try:
#         repo_processor = GithubRepo2Txt()
#         output_file = repo_processor.save_repo_contents(repo_url, branch)
#     except ValueError as ve:
#         print(f"Error: {ve}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         print("Please check the repository URL and try again.")
    """
    # 作为模块导入使用
    from repo2llm.githubrepo2txt import GithubRepo2Txt

    # 创建实例
    repo_processor = GithubRepo2Txt()

    # 方式1：直接保存到文件
    output_file = repo_processor.save_repo_contents(
        repo_url="https://github.com/username/repo",
        branch="master"  # 可选参数
    )

    # 方式2：获取处理后的内容
    repo_name, content = repo_processor.process_repo(
        repo_url="https://github.com/username/repo",
        branch="master"  # 可选参数
    )
"""
