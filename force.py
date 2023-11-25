import subprocess
import hashlib
import os
import time
from multiprocessing import Pool
import random
import os

def compute_git_hash(content):
    header = f'commit {len(content)}\0'.encode('utf-8')
    store = header + content
    return hashlib.sha1(store).hexdigest()

def generate_commit_content(tree, parent, author, committer, message):
    content = f"tree {tree}\n"
    content += f"parent {parent}\n" if parent else ""
    content += f"author {author}\n"
    content += f"committer {committer}\n"
    content += f"\n{message}\n"
    return content.encode('utf-8')

# Function adjusted for multiprocessing
def find_matching_commit(args):
    tree, parent, author_base, committer_base, message, target_end = args
    while True:
        # Randomize the timestamp by adding a delta in seconds for author and committer separately
        author_time_offset = random.randint(-500, 500)
        committer_time_offset = random.randint(-500, 500)
        author_timestamp = int(time.time()) + author_time_offset
        committer_timestamp = int(time.time()) + committer_time_offset

        # Construct the author and committer date strings in Git's format
        author_date_str = time.strftime("%s %z", time.localtime(author_timestamp))
        committer_date_str = time.strftime("%s %z", time.localtime(committer_timestamp))

        # Construct the author and committer strings with the new date strings
        author = f"{author_base} {author_date_str}"
        committer = f"{committer_base} {committer_date_str}"

        # Generate the commit content
        content = generate_commit_content(tree, parent, author, committer, message)
        commit_hash = compute_git_hash(content)

        if commit_hash.startswith(target_end):
            # Return the date strings for setting the environment variables
            return author_date_str, committer_date_str, commit_hash

# Generate arguments for multiprocessing
def generate_args(tree, parent, author, committer, message, target_end, processes):
    return [(tree, parent, author, committer, message, target_end) for _ in range(processes)]

def get_git_config_value(key):
    try:
        return subprocess.check_output(['git', 'config', key]).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return None

def get_last_commit_author():
    try:
        return subprocess.check_output(['git', 'log', '-1', '--pretty=format:%an <%ae>']).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return None
    
if __name__ == '__main__':
    # Get the target pattern and commit message from the user
    target_end = input("Enter the target hash ending (e.g., 'deadbeef'): ")
    message = input("Enter the full commit message: ")

    # These values must be obtained from your actual commit data
    tree = subprocess.check_output(['git', 'write-tree']).strip().decode('utf-8')
    parent = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
    
    # Get the base author and committer information without the timestamp
    author_name = get_git_config_value('user.name')
    author_email = get_git_config_value('user.email')
    author_base = f"{author_name} <{author_email}>"
    committer_base = author_base  # Usually the same as author

     # Number of processes to use
    processes = 20  # or any number you'd like to use

    # Create a pool of workers equal to the number of processes
    with Pool(processes=processes) as pool:
        ## Generate arguments for each process
        args = (tree, parent, author_base, committer_base, message, target_end)
        
        # This will block until a process finds a match
        author_date_str, committer_date_str, commit_hash = pool.apply(find_matching_commit, (args,))
        print(f"Author Date: {author_date_str}")
        print(f"Committer Date: {committer_date_str}")
        print(f"Matching commit hash: {commit_hash}")

        # Set the environment variables with the found timestamps
        os.environ['GIT_AUTHOR_DATE'] = author_date_str
        os.environ['GIT_COMMITTER_DATE'] = committer_date_str

    subprocess.run(['git', 'commit', '--no-gpg-sign', '-m', f"{message}"], check=True)

    # The commit with the desired hash pattern is now in your repository.
    # You can push this to a remote repository.