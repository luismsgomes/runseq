# runseq

**Simple** job manager to run jobs sequentially in a Linux machine.

This simple command line tool was created to solve a problem similar to the ones described here:

- https://stackoverflow.com/questions/72365506/how-to-change-a-sequence-of-bash-commands-while-running
- https://stackoverflow.com/questions/70946428/what-is-the-simplest-queue-job-manager-for-linux

Specifically, I wanted a way to execute long processing jobs sequentially and be able to modify the queue of upcomming jobs while a job was running.

## usage

Using `--help` will show the tool usage:


    usage: runseq [-h] {run,add,list,ls,remove,rm,clear,cl} ...

    runs jobs sequentially

    options:
    -h, --help            show this help message and exit

    actions:
    valid actions

    {run,add,list,ls,remove,rm,clear,cl}
        run                 run jobs as they appear on queue; this command does not return
        add                 add a job to the queue
        list (ls)           list jobs in the queue
        remove (rm)         remove a job from the queue
        clear (cl)          remove all finished jobs from the queue


To use this tool, a *job runner* process must be started with the command `run`.

You may want to run the job runner in the background as follows:

    nohup runseq run > jobs.log 2>&1 &

Upon the first interaction with the job queue, runseq will create a sqlite database named `runseq.sqlite3` in the current directory.  If you want to save the database somewhere else, then set the desired path in the environment variable `RUNSEQ_DB` before running any runseq command.

To submit jobs to the queue, use the `add` command.  The first argument is the priority, which should be an integer; the remaining arguments form the command to be executed. Jobs will be executed in decreasing priority order. A shell will be spawn by the runner process and the command will be execute in the shell, which means that shell builtin commands are available as in the following example:

    runseq add 1 sleep 5 '&&' echo hello 

(note the quoted `&&` to avoid being interpreted by the shell where the `runseq add` command is being executed)

## authorhip and license

This program was created by Luís Gomes (https://research.variancia.com/) and is licensed under the GPLv3 license.


