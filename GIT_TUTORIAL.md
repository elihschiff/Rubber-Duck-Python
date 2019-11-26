**Forking the repo**

​	To get started, first you'll want to fork the main repository. Forking the repo creates a copy of the repository from the main account. This local repository is like a buffer between your contributions and the central repository. When your contributions are ready to be added to the main project, you can make a merge request and then request approval for the code to be added to the main repository. Go to the project you want to fork through the “Project” drop down menu at the top of the website. Then click the “Fork” button. You’ll then be brought to a screen that says “Fork project”. Select the namespace you want to create your fork in. If the namespace you chose to fork the project to has another project with the same pathname, you'll get a warning that the forking could not be completed. Once you've forked, you can make edits to this copy of your repository. When you want to push the code you’ve created back to the central repository, you can create a merge request from your fork back to the main source.


**Syncing your edits with Git**

Once you have a repository cloned or initialized, you can commit file version changes using `git add` and `git commit`. To create an initial commit of your current directory, use the following two commands:

`git add .`

`git commit`

The above will commit an unversioned file into your local repository. Now that you're set up, new files can be added by passing the path to `git add`.

`git add <file_name>` 
This adds the specified file from the working directory to the repository staging area. The staging area can be thought of like a buffer between the working directory and the project's history. This stage lets you group related changes into a single concentrated area before actually committing changes to the project history, allowing you to edit unrelated files and then go back and commit them in smaller pieces. It's important to make logical, periodic commits so that it's easy to track down bugs and revert changes. `git add` is the first in a series of commands that directs Git to save a snapshot of the current project state into commit history.

`git commit -m "comment-describing-commit"`
This command is used to commit a snapshot of the staging directory to the repository's commit history. Commits are like snapshots of a directory along the timeline of a Git project. This lets developers work in an isolated environment, deferring integration until they're at a convenient point to merge with other users. 

`git fetch`
Fetch downloads commits, files, and refs from a remote repo into your local repo. This command allows you to see what everyone else has been working on without actually merging these changes into your repository. Content that has been "fetched"will not affect your local development, so you can review other commits before you integrate them locally. The following command will actually download remote content to your local active branch.

`git pull <remote> <branch_name>` 
This updates the local version of a repository from a remote repo. Running `git pull` actually executes `git fetch` and `git merge` on your checked-out, local branch with the remote branch. Remote branches are like local branches, except they map to commits from someone else's repository. They can be thought of as "read-only" branches. The command `git pull origin master` fetches a copy of the master branch from the original repo, and merges it with the current, checked-out branch.

`git push <remote_name> <branch_name>` 
This command uploads local repository content to a remote repository. Pushing is how you transfer commits from your staging area to a remote repo. In contrast to `git fetch`, which imports commits to local branches, `git push` exports commits to remote branches. All changes to the local repository must be committed before you push to the remote repository. 
Run `git push --help` to learn about the different options you can pass with this command. 

`git checkout <branch_name>`
'git checkout' can be used to switch between branches, restore working files, or create a new branch that updates files in the working directory to match the version stored in that branch. To create and check out a new branch, run `git checkout -b <new_branch> `The -b option tells git to run `git branch <new_branch>` before running `git checkout <new_branch>`. To delete a local branch (which you should do once your merge request has been closed), run `git branch -d <branch_name>`.

`git status` 
Running the above commands tells you which branch you're currently in and informs you if it has diverged from the same branch on the server. If none of your tracked files are modified, your terminal should output `Your branch is up-to-date with…`.


</u> Summary </u>:

1. Pushing (and tracking) a local branch to a remote Git repository.

   First, you'll want to create a new branch using `git checkout -b <branch_name>`. 
   When you create a new branch, it will include all commits from the parent 
   branch.

   Edit your files, and when you're ready, add and commit your files to the branch you've created. To add a file to your project, use the command `git add <file_name>`. Finally, push your branch to the remote repository using `git push -u origin <branch_name>`. Use `git push` to push commits made on your local branch to a remote repository.  The `push` command takes two arguments: a remote name, for example, `origin`, and a branch name, like , `master`. `git push origin master` is usually run to push your local changes to your online repository. `git fetch` will download from the specified repository.
   
   
   
2. Committing changes

   The command`git commit` will update the changes that you've made. Note that any files that you have created or modified that you haven’t run `git add` on since you edited 
   them won’t be committed. To check which branch you’re currently connected to,
   run `git status`. Make sure you're committing to the correct branch. If you want to see the changes you’ve staged that will go into your next commit, tun `git diff -- staged`.
   
   
   
3. Creating a merge request

   When you’ve made edits to that you want sent back to the main project, you can create a merge request. Click “Merge request” on the left side bar, then click “new merge request.” Your forked 
   project’s main branch should be the source branch, and the original project’s main 
   branch should be the target branch. Once you submit your 
   merge request, your changes will be added to the main repository and the 
   branch. Once you've submitted a merge request, switch back to the master branch using
   `git checkout master`.
