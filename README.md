sublime-gitignorer
==================

Sublime plugin that excludes from your Sublime project any files ignored by git.

Created as a solution to http://stackoverflow.com/questions/18482976/tell-sublime-text-to-ignore-everything-in-gitignore

Usage instructions:

* Install the plugin by copying and pasting `gitignore_plugin.py` into your Packages folder. See http://stackoverflow.com/a/15652795/1709587 for manual package installation instructions. Installation via Sublime Package Control is not yet supported.
* `sublime-gitignorer` will regularly check all your open folders for files that are ignored by Git and update your `"file_exclude_patterns"` and `"folder_exclude_patterns"` settings in Sublime to match the list of files and folders ignored by Git.
* After you create a new Git-ignored file or update your `.gitignore` files, the files should be hidden from your project within 5 seconds.
* Since the `"file_exclude_patterns"` and `"folder_exclude_patterns"` settings are now being managed programatically, if you want to *manually* set file or folder exclusion patterns in sublime, you can use the `"extra_file_exclude_patterns"` and `"extra_folder_exclude_patterns"` settings. Any file paths you list in here will automatically be included in your `"file_exclude_patterns"` and `"folder_exclude_patterns"` in addition to Git-ignored paths.
* If you already have `"file_exclude_patterns"` or `"folder_exclude_patterns"` set, there is no need to back them up prior to installing this plugin; they will be automatically migrated to the `"extra_file_exclude_patterns"` and `"extra_folder_exclude_patterns"` settings on first launch.

Currently tested on Ubuntu in Sublime Text 2 and Sublime Text 3. I haven't tested on Mac yet but it should work there too. Windows is not currently supported.
