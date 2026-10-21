#!/usr/bin/env python3
"""Manage the durable watcher event queue. Ack only events observed before sync began."""
import sqlite3,sys,time
from pathlib import Path
dbpath=Path.home()/".local/state/proton-bisync/local_events.sqlite3"
def main():
    if len(sys.argv)<2:raise SystemExit("Usage: snapshot|ack <epoch>|stats")
    if not dbpath.exists():
        if sys.argv[1]=="stats":print("0");return
        if sys.argv[1]=="snapshot":print(time.time());return
        return
    with sqlite3.connect(dbpath,timeout=15) as conn:
        if sys.argv[1]=="snapshot":
            print(time.time())
        elif sys.argv[1]=="ack":
            limit=float(sys.argv[2])
            conn.execute("DELETE FROM pending WHERE changed_at<=?",(limit,))
        elif sys.argv[1]=="clear-full-scan":
            conn.execute("DELETE FROM control WHERE key='needs_full_scan'")
        elif sys.argv[1]=="stats":
            print(conn.execute("SELECT COUNT(*) FROM pending").fetchone()[0])
        else:raise SystemExit(64)
if __name__=="__main__":main()
