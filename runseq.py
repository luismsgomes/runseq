"""Simple job manager to run jobs sequentially"""

import argparse
import os
import sqlite3
import subprocess
import sys
import time

from datetime import datetime


DB_PATH = os.environ.get("RUNSEQ_DB", "runseq.sqlite3")


def db_connect():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS jobs("
        "id INTEGER PRIMARY KEY, "
        "priority INTEGER, "
        "submitted VARCHAR(64), "
        "command VARCHAR(1024)"
        ")"
    )
    return con


def run_job(job_id, priority, submitted, command):
    started = datetime.now()
    print(
        "### starting job #########################",
        "##      job id: %d" % job_id,
        "##    priority: %d" % priority,
        "##     command: %s" % command,
        "##   submitted: %s" % submitted,
        "##     started: %s" % started,
        "##########################################",
        sep="\n",
        flush=True,
    )
    proc = subprocess.run(command, shell=True)
    finished = datetime.now()
    print(
        "### finished job #########################",
        "##      job id: %d" % job_id,
        "##    priority: %d" % priority,
        "##     command: %s" % command,
        "##   submitted: %s" % submitted,
        "##     started: %s" % started,
        "##    finished: %s" % finished,
        "## exit status: %d" % proc.returncode,
        "##########################################",
        sep="\n",
        end="\n\n",
        flush=True,
    )


def run_jobs():
    sql = "SELECT id, priority, submitted, command FROM jobs ORDER BY -priority LIMIT 1"
    with db_connect() as con:
        while True:
            for job_id, priority, submitted, command in con.execute(sql):
                remove_job(job_id)
                run_job(job_id, priority, submitted, command)
                break  # fetch next job
            else:
                time.sleep(10)  # queue was empty; wait before retrying


def add_job(priority, command):
    with db_connect() as con:
        con.execute(
            "INSERT INTO jobs (priority, submitted, command) VALUES (?, ?, ?)",
            (priority, datetime.now(), command),
        )


def remove_job(job_id):
    with db_connect() as con:
        con.execute("DELETE FROM jobs WHERE id=? LIMIT 1", (job_id,))


def list_jobs():
    sql = "SELECT id, priority, submitted, command FROM jobs ORDER BY -priority"
    with db_connect() as con:
        for job_id, priority, submitted, command in con.execute(sql):
            print(
                "id:",
                job_id,
                "priority:",
                priority,
                "submitted: ",
                submitted,
                "command:",
                command,
            )


def parse_commandline():
    parser = argparse.ArgumentParser(
        prog="runseq",
        description="runs jobs sequentially",
    )
    subparsers = parser.add_subparsers(
        dest="action", required=True, title="actions", description="valid actions"
    )
    subparsers.add_parser(
        "run", help="run jobs as they appear on queue; this command does not return"
    )
    parser_add = subparsers.add_parser("add", help="add a job to the queue")
    parser_add.add_argument(
        "priority",
        type=int,
        help="add a job to the queue (higher priority will be executed first)",
    )
    parser_add.add_argument("command", type=str, help="the command to be executed")
    parser_add.add_argument("args", type=str, nargs="*", help="command arguments")
    subparsers.add_parser("list", aliases=["ls"], help="list jobs in the queue")
    parser_rm = subparsers.add_parser(
        "remove", aliases=["rm"], help="remove a job from the queue"
    )
    parser_rm.add_argument("job_id", type=int, help="the id of the job to be removed")
    return parser.parse_args()


def main():
    args = parse_commandline()
    if args.action == "run":
        run_jobs()
    elif args.action == "add":
        command = " ".join([args.command] + args.args)
        add_job(priority=args.priority, command=command)
    elif args.action in ["list", "ls"]:
        list_jobs()
    elif args.action in ["remove", "rm"]:
        remove_job(args.job_id)
    else:
        print("invalid action:", args.action, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
