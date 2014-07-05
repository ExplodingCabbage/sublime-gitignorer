import sublime
import subprocess
import os
import os.path
import threading
from time import sleep

# Used for output suppression when calling subprocess functions; see
# http://stackoverflow.com/questions/10251391/suppressing-output-in-python-subprocess-call
devnull = open(os.devnull, 'w')

def start(): # Gets invoked at the bottom of this file.
    """
    Regularly (every 5s) updates the file_exclude_patterns setting from a
    background thread.
    """
    def run():
        while True:
            update_file_exclude_patterns()
            sleep(5)
            
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

def update_file_exclude_patterns():
    """
    Updates the "file_exclude_patterns" preference to include all .gitignored
    files.
    
    Also includes any additional files or folders listed in the
    "extra_file_exclude_patterns" and "extra_folder_exclude_patterns" settings.
    """
    s = sublime.load_settings("Preferences.sublime-settings")
    file_exclude_patterns = s.get('extra_file_exclude_patterns', [])
    folder_exclude_patterns = s.get('extra_folder_exclude_patterns', [])
    for path in all_ignored_paths():
        if os.path.isdir(path):
            folder_exclude_patterns.append(path.rstrip('/'))
        else:
            file_exclude_patterns.append(path)
    
    # Only make changes if anything has actually changed, to avoid spamming the
    # sublime console
    new_files = set(file_exclude_patterns)
    old_files = set(s.get('file_exclude_patterns', []))
    new_folders = set(folder_exclude_patterns)
    old_folders = set(s.get('folder_exclude_patterns', []))
    
    
    if new_files != old_files or new_folders != old_folders:        
        s.set('file_exclude_patterns', file_exclude_patterns)
        s.set('folder_exclude_patterns', folder_exclude_patterns)
        sublime.save_settings("Preferences.sublime-settings")

def all_ignored_paths():
    """
    Returns a list of all .gitignored files or folders contained in repos
    contained within or containing any folders open in any open windows.
    """
    
    open_folders = set()
    for window in sublime.windows():
        open_folders.update(window.folders())
    
    all_ignored_paths = set()
    for folder in open_folders:
        ignored_paths = folder_ignored_paths(folder)
        all_ignored_paths.update(ignored_paths)
        
    return list(all_ignored_paths)

def folder_ignored_paths(folder):
    """
    Returns a list (without duplicates, in the case of weird repo-nesting) of
    all files/folders within the given folder that are git ignored.
    
    The folder itself need not be the top level of a git repo, nor even within 
    a git repo.
    """
    
    all_ignored_paths = set()
    
    # First find all repos CONTAINED in this folder:
    repos = set(find_git_repos(folder))
    
    # Then, additionally, if this folder is itself contained within a repo,
    # find the .git folder of the repo containing it:
    if is_in_git_repo(folder):
        repos.add(parent_repo_path(folder))
    
    # Now we find all the ignored paths in any of the above repos
    for git_repo in repos:
        ignored_paths = repo_ignored_paths(git_repo)
        all_ignored_paths.update(ignored_paths)
            
    return list(all_ignored_paths)

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
    Takes the path to a folder contained within a git repo, and returns the
    parent repo.
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

def repo_ignored_paths(git_repo):
    """
    Takes the path of a git repo and lists all ignored files/folders in the
    repo.
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
    
start()