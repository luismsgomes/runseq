"""Simple job manager to run jobs sequentially"""

import argparse
import os
import sqlite3
import subprocess
import sys
import time


DB_PATH = os.environ.get("RUNSEQ_DB", "runseqv0.2.sqlite3")


def db_connect():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS jobs("
        "job_id INTEGER PRIMARY KEY, "
        "status TEXT "
        "CHECK(status IN ('running','queued','finished')) "
        "NOT NULL DEFAULT 'queued', "
        "priority INTEGER, "
        "submitted TEXT NOT NULL, "
        "started TEXT DEFAULT NULL, "
        "finished TEXT DEFAULT NULL, "
        "returncode INTEGER DEFAULT NULL,"
        "command TEXT NOT NULL"
        ")"
    )
    return con


def run_job(job_id):
    with db_connect() as con:
        sql = (
            "UPDATE jobs "
            "SET status = 'running', started = datetime('now') "
            "WHERE job_id = ? LIMIT 1"
        )
        con.execute(sql, (job_id,))
        sql = (
            "SELECT priority, submitted, started, command "
            "FROM jobs "
            "WHERE job_id = ? LIMIT 1"
        )
        priority, submitted, started, command = con.execute(sql, (job_id,)).fetchone()
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
    with db_connect() as con:
        sql = (
            "UPDATE jobs "
            "SET status = 'finished', finished = datetime('now'), returncode = ? "
            "WHERE job_id = ? LIMIT 1"
        )
        con.execute(sql, (proc.returncode, job_id))
        sql = "SELECT finished FROM jobs WHERE job_id = ? LIMIT 1"
        finished = con.execute(sql, (job_id,)).fetchone()[0]
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
    sql = (
        "SELECT job_id "
        "FROM jobs "
        "WHERE status = 'queued' "
        "ORDER BY -priority, submitted LIMIT 1"
    )
    with db_connect() as con:
        while True:
            for (job_id,) in con.execute(sql):
                run_job(job_id)
                break  # rerun SQL to fetch next job
            else:
                time.sleep(10)  # queue was empty; wait before retrying


def add_job(priority, command):
    sql = (
        "INSERT INTO jobs (priority, submitted, command) "
        "VALUES (?, datetime('now'), ?)"
    )

    with db_connect() as con:
        con.execute(sql, (priority, command))


def remove_job(job_id):
    with db_connect() as con:
        con.execute("DELETE FROM jobs WHERE job_id=? LIMIT 1", (job_id,))


def clear_finished_jobs():
    with db_connect() as con:
        con.execute("DELETE FROM jobs WHERE status = 'finished'")


def list_jobs():
    columns = [
        "job_id",
        "status",
        "priority",
        "submitted",
        "started",
        "finished",
        "returncode",
        "command",
    ]
    sql = (
        "SELECT " + ", ".join(columns) + " FROM jobs "
        "ORDER BY CASE "
        "WHEN status = 'finished' THEN 0 "
        "WHEN status = 'running' THEN 1 "
        "WHEN status = 'queued' THEN 2 "
        "END, -priority, submitted"
    )
    with db_connect() as con:
        for line in con.execute(sql):
            line = ["n/a" if value is None else value for value in line]
            print(
                *["%s: %s" % key_value for key_value in zip(columns, line)], sep=" | "
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
    parser_clear = subparsers.add_parser(  # noqa: F841
        "clear", aliases=["cl"], help="remove all finished jobs from the queue"
    )
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
    elif args.action in ["clear", "cl"]:
        clear_finished_jobs()
    else:
        print("invalid action:", args.action, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
