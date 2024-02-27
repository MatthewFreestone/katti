## Conventions:
All kattis solutions are named by their problem id on kattis and are enclosed in a directory by that name. If they have sample inputs
or expected outputs those will be included in the directory.

# Installation of Katti Automation 

To install the Katti command line tool, simply install using pip.

I recommend using a virtual environment to install katti, so you don't have to worry about conflicting dependencies.

```bash
$ python -m pip install katti
```

## Additional Setup

**1. Login to Kattis and download or copy and paste your personal .kattisrc file from:**
```
https://open.kattis.com/download/kattisrc
```
**2. Move your .kattisrc to your home directory:**
```
$ mv .kattisrc $HOME
```

**3. add password to .kattisrc:**
In the .kattisrc file, add your password to the below line that says "token:". It should look like this:
```
[user]
username: <username>
token: <token>
password: <password>
```
# Usage
The tool can be run using a terminal or command prompt. If you are using a virtual environment, make sure to activate it before running the tool.

## Commands

**katti get <problem_id>**  
Download the problem description, sample inputs and sample outputs from Kattis and create a directory for the problem. It will do this in the directory that you run the command from.
```bash
$ katti get carrots
``` 

**katti description <problem_id>**  
Open the problem description for the given problem_id in your default browser.  
```bash
$ katti description carrots
```

**katti run**  
Run test cases on the problem in the current directory. This will run all the test cases in the directory, and will tell you if you passed or failed each one.  
```bash
$ katti run
```

**katti submit**  
Submit the problem in the current directory to Kattis. This will submit the problem, and give you a link to watch the submission status.
```bash
$ katti submit
```

**katti add <problem_id>**  
Add a problem to your "todo" list, which is stored with your katti install. Running this command will allow `katti random` to select this problem.  
```bash
$ katti add carrots
```

**katti update**
Update the list of problems from Kattis. This will update the list of problems that `katti random` can select from. This will also update the rating of each problem in "todo" list. (this function is slow, and may take about a minute to run) 
```bash
$ katti update
```

**katti random <difficulty>**
Select a random problem from your "unsolved" list. If you specify a difficulty, it will only select problems that have the same difficulty, rounded down.  
```bash
$ katti random 2.0
```

**katti selected <difficulty>**
Select a random problem from our high quality list. If you specify a difficulty, it will only select problems that have the same difficulty, rounded down.  
```bash
$ katti selected 2.0
```

