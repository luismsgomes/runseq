# runseq

**Simple** job manager to run jobs sequentially in a Linux machine.


## usage

General usage:


    runseq --help
    usage: runseq [-h] {run,add,list,ls,remove,rm} ...

    runs jobs sequentially

    options:
    -h, --help            show this help message and exit

    actions:
    valid actions

    {run,add,list,ls,remove,rm}
        run                 run jobs as they appear on queue; this command does not return
        add                 add a job to the queue
        list (ls)           list jobs in the queue
        remove (rm)         remove a job from the queue


You may want to run the job manager in the background as follows:

    nohup runseq run > jobs.log 2>&1 &

This will create a sqlite database named `runseq.sqlite3` in the current directory.  If you want to place the database somewhere else, then set the desired path in the environment variable `RUNSEQ_DB` before running any runseq command.

To submit jobs you use the `add` command.  The first argument is the priority (integer). Jobs will be executed in decreasing priority order. After the priority, all arguments are considered part of the command to be executed.  A shell will be spawn and the command will be execute in the shell, which means that shell builtin commands are available as in the following example:

    runseq add 1 sleep 5 '&&' echo hello 


# license

This software is licensed under the GPLv3 license.
