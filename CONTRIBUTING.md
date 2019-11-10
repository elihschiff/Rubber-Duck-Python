If you're new to the team, first you'll want to fork the repository. Once you've
created your own copy of the repository, you can edit the code locally on your 
own device, and then merge your code with the main source code. 


**Forking the repo**

Forking the repo creates a copy of the repository from the main account to your
own account. Creating a copy of the source code allows you to commit to edit and
commit to your own project, and then request approval for the code to be added 
to the main repository. 
Go to the project you want to fork through the “Project” drop down menu at the 
top of the website. Then click the “Fork” button. You’ll then be brought to 
a screen that says “Fork project”, where you’ll choose where you want to 
fork. Select the namespace you want to create your fork in.  If the namespace 
you chose to fork the project to has another project with the same path name, 
you will be presented with a warning that the forking could not be completed. 
You can now make edits to this copy of your repository. When you want to push 
the code you’ve created back to the main source, you can create a merge request 
from your fork back to the main source. 



**Committing and pushing your edits**

Use the following commands:

`git checkout master `

`git fetch` 

`git pull` 

`git checkout -b NEW_BRANCH_NAME `

`git add <file-name> `

`git commit -m "COMMENT FOR YOUR COMMIT" `

`git push` 



1. Pushing (and tracking) a local branch to a remote Git repository.

   To create a new branch, type `git checkout -b <branch_name>`. When you create
   a new branch, it will include all commits from the parent branch. The parent 
   branch is the branch you're on when you create the new branch. 

   Edit your files, and when you feel you're ready to share what you've written,
   add and commit your files to the branch you've created. To add a file to your
   project, use the command `git add <filename>`. Finally, push your branch to 
   the remote repository using `git push -u origin <branch_name>`. Use `git push` 
   to push commits made on your local branch to a remote repository.  The `push` 
   command takes two arguments: a remote name, for example, `origin`, and a branch 
   name, like , `master`. For example, `git push <REMOTENAME> <BRANCHNAME> `. 
   `git fetch` will "fetch" or download from either a single named repository or
   URL, or from several repositories at once if <group> is passed in. 

   `git push origin master` is usually run to push your local changes to your 
   online repository.

   

2. Committing changes

   The simplest way to commit is type `git commit`. Note that any files that you 
   have created or modified that you haven’t run `git add` on since you edited 
   them won’t be committed. To check which branch you’re currently connected to,
   use the `git status` command.  `git status` will inform you which branch 
   you’re working on. If you want to see the changes you’ve staged that will go 
   into your next commit, use `git diff -- staged`.

   

3. Creating a merge request

   When you’ve made edits to your code that you want sent back to the main 
   project, you can create a merge request. Click “Merge request” on the 
   left side bar, then click “new merge request.” Select your forked 
   project’s main branch as the source branch and the original project’s main 
   branch as the target branch, and create a merge request. Once you submit your 
   merge request, your changes will be added to the main repository and the 
   branch. Your changes will be added to the repository and the target branch.
   Once you've submitted a merge request, switch back to the master branch using
   `git checkout master`.

   

**Other** 

<u>Fun with branches</u>

Checking branch status: `git status` tells you which branch you’re in and informs 
you that it has not diverged from the same branch on the server. If none of your 
tracked files are modified, your terminal should output `Your branch is up-to-date 
with…` when you run the command. The default branch is always `master`. 



Renaming branches: To rename a branch, use the same `git push` command, but you 
would add one more argument: the name of the new branch. For example: 
`git push <remote_name> <local_branch_name>:<remote_branch_name>`. This pushes 
the `local_branch_name` to your `remote_name` but it is renamed to 
`remote_branch_name`.




Deleting a remote branch or tag: Use following syntax:
    `git push  <remote_name> :<branch_name>`. 
Note that there is a space before the colon. The process is similar to renaming 
a branch. However, here, you're telling Git to push *nothing* into `branch_name` 
on `remote_name`. Because of this, `git push` deletes the branch on the remote 
repository.

<u>Using Python Black</u>

Black is a Python code formatter. Installing Black is simple! Just type 
`pip install black` in your terminal.

Black must be run against a Python file, like so: black file.py
When Black is done running, it will output the following:

​       `reformatted long_func.py`

​      `All done! ✨ 🍰 ✨ 1 file reformatted.`

This indicates that the file has been reformatted following the pip3 standard. 
Also, If you don’t want Black to change your file, but you still want to know 
if Black thinks a file should be changed, you can use one of the following command 
flags: `--check`, which checks if the file should be reformatted, but doesn’t 
actually modify the file or `--diff` – which writes out a diff of what Black 
would do to the file, but also doesn’t modify the file.