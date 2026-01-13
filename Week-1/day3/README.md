#Day -3 Git & Recovery workflow
created an file naming log.js and app.log for couting error and a log file respectively
##Working with bisect 
### Commands 
`nano log.js` 
for working with js file
`git add log.js` 
for adding log.js
`git commit -m "message"`
for commiting staged files 

In total 8 commits were done:
```64d2aca (HEAD -> main) commented log
a93635a added log for processing message
0765d4d added todo
f75a0b9 added error count
2afbe4e bug added for non error count
f3607d6 added error counting function
4e2564b detecting error logs
fd98e03 created log.js
```
That can be seen by `git log --oneline`

Then tested the file with `node log.js`
which didnt give the expected output: `1`
actual output: `5`
so used `git bisect start`

which initiates with the recent head i.e `64d2aca`
which is a bad commit
so we flag it with the help of `git bisect bad`

which should give this output: `status: waiting for good commit(s), bad commit known`

after this will have to provide a good commit like: `git bisect good f3607d6`

which flags the left bad commits that are:
```f75a0b9 (HEAD) added error count
2afbe4e bug added for non error count
f3607d6 added error counting function
4e2564b detecting error logs
fd98e03 created log.js
```
now will check our script for the current head and then it should prompt the output, which wont be the expected one
hence we flag this `git bisect bad`

and the output is:
```Bisecting: 0 revisions left to test after this (roughly 0 steps)
[2afbe4eb2b9c23618f75d43800c31ad705ddf809] bug added for non error count
```

now will stop bisect using `git bisect reset`


### working with revert:

knowing the bad commit we can revert it with perserving the current history of working directory, through :
```git revert 2afbe4e```

after this one extra head will be added to our commit history that says `2304876 (HEAD -> main) Revert "bug added for non error count"`

which removes the only changes done at that specific commit and keeps rest things intact


### working with stash:
now will add one comment to the log.js for making it uncommited change:
```//TODO: error detection logic
//temporary comment <- this line in here
//console.log("processing log file")
const fs=require("fs")
function parseLine(line){return line.trim()}
function isError(line){return line.includes("ERROR")}
function countErrors(lines){
let c=0
for(const l of lines)if(isError(l))c++
return c
}
const logs=fs.readFileSync("app.log","utf8").split("\n")
console.log("Total Error Count:",countErrors(logs))
```
and will save it. 

now check current status, using `git status` shall say `modified: log.js` uncommited changes etc

and now will save it for working over previous working heads using `git stash` which will save the current changes in the .git/objects as a stack


after we are done with the task we can bring back uncommited changes through `git stash pop`

### resolving merge conflict 

we create a new branch naming feature using `git checkout -b feature`
then we edit our code, i.e:
```//TODO: error detection logic
//temporary comment
//console.log("processing log file")
const fs=require("fs")
function parseLine(line){return line.trim()}
function isError(line){return line.includes("ERROR")}
function countErrors(lines){
let c=0
for(const l of lines)if(isError(l))c++
return c
}
const logs=fs.readFileSync("app.log","utf8").split("\n")
console.log("Error Count:",countErrors(logs)) //<-- this line in here ```

add and commit changes, that are recently done and then `git checkout -b main`

and will modify the same line with different comments, which will eventually create conflict while merging.

merge branches using `git merge feature`
it will say ```CONFLICT (content): Merge conflict in log.js
Automatic merge failed; fix conflicts and then commit the result.```

now will have to review it manually and do changes, after that commit those changes and merge conflict will be resolved.
