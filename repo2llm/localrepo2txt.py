import os
from tqdm import tqdm

class LocalRepo2Txt:
    def __init__(self):
        self.binary_extensions = [
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
        self.ignore_dirs = {'.git', '__pycache__', '.svn', '.hg', '.DS_Store', '.venv'}
    
    def _traverse_local_repo_iteratively(self, repo_path):
        """
        Traverse the local repository iteratively.
        """
        structure = ""
        dirs_to_visit = [repo_path]
        dirs_visited = set()

        while dirs_to_visit:
            current_path = dirs_to_visit.pop()
            dirs_visited.add(current_path)
            for entry in tqdm(os.scandir(current_path), desc=f"Processing {current_path}", leave=False):
                if entry.is_dir():
                    if entry.name in self.ignore_dirs:
                        continue
                    if entry.path not in dirs_visited:
                        structure += f"{entry.path}/\n"
                        dirs_to_visit.append(entry.path)
                else:
                    structure += f"{entry.path}\n"
        return structure
    
    def _get_local_file_contents_iteratively(self, repo_path):
        # Ensure repo_path ends with '/'
        if not repo_path.endswith('/'):
            repo_path = repo_path + '/'
        file_contents = ""
        dirs_to_visit = [repo_path]
        dirs_visited = set()
    
        while dirs_to_visit:
            current_path = dirs_to_visit.pop()
            dirs_visited.add(current_path)
            for entry in tqdm(os.scandir(current_path), desc=f"Downloading {current_path}", leave=False):
                if entry.is_dir():
                    if entry.name in self.ignore_dirs:
                        continue
                    if entry.path not in dirs_visited:
                        dirs_to_visit.append(entry.path)
                else:
                    if any(entry.name.endswith(ext) for ext in self.binary_extensions):
                        file_contents += f"File: {entry.path}\nContent: Skipped binary file\n\n"
                    else:
                        file_contents += f"File: {entry.path}\n"
                        try:
                            with open(entry.path, 'r', encoding='utf-8') as file:
                                file_contents += f"Content:\n{file.read()}\n\n"
                        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
                            file_contents += "Content: Skipped due to decoding error or file not found\n\n"
        return file_contents
    
    def process_repo(self, repo_path):
        """
        处理本地仓库并返回处理后的内容
        
        Args:
            repo_path (str): 本地仓库路径
            
        Returns:
            tuple: (repo_name, content_string) - 仓库名和处理后的内容字符串
        """
        repo_name = os.path.basename(repo_path)
    
        # print(f"Fetching repository structure for: {repo_name}")
        repo_structure = f"Repository Structure: {repo_name}\n"
        repo_structure += self._traverse_local_repo_iteratively(repo_path)
    
        repo_structure = repo_structure.replace(repo_path, '.')
    
        # print(f"\nFetching file contents for: {repo_name}")
        file_contents = self._get_local_file_contents_iteratively(repo_path)
    
        instructions = "Use the files and contents provided below to complete this analysis:\n\n"
        
        # 组合所有内容
        content = (
            instructions +
            repo_structure +
            '\n\n' +
            file_contents
        )
        
        return repo_name, content
    
    def save_repo_contents(self, repo_path):
        """
        处理本地仓库并保存到文件
        
        Args:
            repo_path (str): 本地仓库路径
            
        Returns:
            str: 输出文件的路径
        """
        try:
            repo_name, content = self.process_repo(repo_path)
            output_filename = f'{repo_name}_contents.txt'
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # print(f"Repository contents saved to '{output_filename}'.")
            return output_filename
            
        except Exception as e:
            raise Exception(f"Error processing repository: {str(e)}")

# if __name__ == '__main__':
#     repo_path = input("Please enter the local repository path: ")
#     try:
#         repo_processor = LocalRepo2Txt()
#         output_file = repo_processor.save_repo_contents(repo_path)
#     except Exception as e:
#         # print(f"An error occurred: {e}")
#         # print("Please check the repository path and try again.")

"""
# 作为模块导入使用
from repo2llm.localrepo2txt import LocalRepo2Txt

# 创建实例
repo_processor = LocalRepo2Txt()

# 方式1：直接保存到文件
output_file = repo_processor.save_repo_contents(
    repo_path="/path/to/local/repo"
)

# 方式2：获取处理后的内容
repo_name, content = repo_processor.process_repo(
    repo_path="/path/to/local/repo"
)
"""