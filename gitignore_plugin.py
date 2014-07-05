import subprocess
import os

# Used for output suppression when calling subprocess functions; see
# http://stackoverflow.com/questions/10251391/suppressing-output-in-python-subprocess-call
devnull = open(os.devnull, 'w')

def all_ignored_files(folder):
    """
    Returns a list (without duplicates, in the case of weird repo-nesting) of
    all files within the given folder that are git ignored.
    
    The folder itself need not be the top level of a git repo, nor even within 
    a git repo.
    """
    
    all_ignored_files = set()
    
    # First find all repos CONTAINED in this folder:
    repos = set(find_git_repos(folder))
    
    # Then, additionally, if this folder is itself contained within a repo,
    # find the .git folder of the repo containing it:
    if is_in_git_repo(folder):
        repos.add(parent_repo_path(folder))
    
    # Now we find all the ignored files in any of the above repos
    for git_repo in repos:
        ignored_files = list_ignored_files(git_repo)
        all_ignored_files.update(ignored_files)
            
    return list(all_ignored_files)

def is_in_git_repo(folder):
    """
    Returns true if the given folder is contained within a git repo
    """
    
    exit_code = subprocess.call(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=folder,
        stdout=devnull,
        stderr=devnull
    )
    
    return exit_code == 0

def parent_repo_path(folder):
    """
    Takes the path to a folder contained within a git repo, and returns the parent repo.
    """
    
    return subprocess.Popen(
        ['git', 'rev-parse', '--show-toplevel'],
        stdout=subprocess.PIPE,
        cwd=folder
    ).stdout.read().strip()

def find_git_repos(folder):
    """
    Returns a list of all git repos within the given ancestor folder.
    """
    
    # Command for finding git repos nicked from
    # http://sixarm.com/about/git-how-to-find-git-repository-directories.html
    command_output = subprocess.Popen(
        ['find', folder, '-type', 'd', '-name', '.git'],
        stdout=subprocess.PIPE
    ).stdout.read()
    
    if command_output.isspace() or command_output == '':
        return []
    
    dot_git_folders = command_output.strip().split('\n')
    
    return [path.replace('/.git', '') for path in dot_git_folders]

def list_ignored_files(git_repo):
    """
    Takes the path of a git repo and lists all ignored files in the repo.
    """
        
    # Trick for listing ignored files nicked from
    # http://stackoverflow.com/a/2196755/1709587
    command_output = subprocess.Popen(
        ['git', 'clean', '-ndX'],
        stdout=subprocess.PIPE,
        cwd=git_repo
    ).stdout.read()
    
    if command_output.isspace() or command_output == '':
        return []
       
    lines = command_output.strip().split('\n')
    # Each line in `lines` now looks something like:
    # "Would remove foo/bar/yourfile.txt"
    
    relative_paths = [line.replace('Would remove ', '', 1) for line in lines]
    absolute_paths = [git_repo + '/' + path for path in relative_paths]
    
    return absolute_paths