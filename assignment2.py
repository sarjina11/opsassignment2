#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Student Name"
Semester: "Enter Winter/Summer/Fall Year"

The python code in this file is original work written by
"Student Name". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: A memory usage visualizer that shows system and program memory usage
using bar charts and human-readable formats as specified by command-line options.
'''

import argparse
import os

def parse_command_args() -> object:
    """
    Set up command-line arguments for the memory visualizer program.
    """
    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )
    parser.add_argument(
        "-H", "--human-readable",
        action="store_true",
        help="Prints sizes in human readable format"
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )
    parser.add_argument(
        "program",
        type=str,
        nargs="?",
        help="if a program is specified, show memory use of all associated processes. Show only total use if not."
    )
    return parser.parse_args()

def percent_to_graph(percent: float, length: int = 20) -> str:
    """
    Converts a percentage (0.0 to 1.0) into a bar graph of specified length.
    """
    filled = int(percent * length)
    empty = length - filled
    return f"[{'#' * filled}{' ' * empty}] {int(percent * 100)}%"

def get_sys_mem() -> int:
    """
    Returns total system memory in kB.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return 0

def get_avail_mem() -> int:
    """
    Returns total available memory in kB.
    """
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    return 0

def pids_of_prog(app_name: str) -> list:
    """
    Returns a list of process IDs for a given application name using the `pidof` command.
    """
    try:
        result = os.popen(f"pidof {app_name}").read().strip()
        return result.split() if result else []
    except Exception:
        return []

def rss_mem_of_pid(proc_id: str) -> int:
    """
    Returns the Resident Set Size (RSS) memory used by a process (in kB).
    """
    try:
        rss_total = 0
        with open(f"/proc/{proc_id}/smaps") as f:
            for line in f:
                if line.startswith("Rss:"):
                    rss_total += int(line.split()[1])
        return rss_total
    except FileNotFoundError:
        return 0

def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """
    Converts kibibytes to human-readable format (e.g., MiB, GiB).
    """
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suffix_index = 0
    value = kibibytes
    while value >= 1024 and suffix_index < len(suffixes) - 1:
        value /= 1024
        suffix_index += 1
    return f"{value:.{decimal_places}f} {suffixes[suffix_index]}"

if __name__ == "__main__":
    args = parse_command_args()

    if not args.program:
        # No program specified, show total memory usage
        total_mem = get_sys_mem()
        avail_mem = get_avail_mem()
        used_mem = total_mem - avail_mem
        percent_used = used_mem / total_mem
        graph = percent_to_graph(percent_used, args.length)

        if args.human_readable:
            total_mem = bytes_to_human_r(total_mem)
            used_mem = bytes_to_human_r(used_mem)
            print(f"Memory {graph} {used_mem}/{total_mem}")
        else:
            print(f"Memory {graph} {used_mem}/{total_mem} kB")
    else:
        # Program specified, show memory usage for its processes
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"No processes found for program: {args.program}")
        else:
            total_rss = 0
            for pid in pids:
                rss = rss_mem_of_pid(pid)
                total_rss += rss
                percent_used = rss / get_sys_mem()
                graph = percent_to_graph(percent_used, args.length)

                if args.human_readable:
                    rss = bytes_to_human_r(rss)
                    print(f"{pid:<10} {graph} {rss}")
                else:
                    print(f"{pid:<10} {graph} {rss} kB")
            percent_used = total_rss / get_sys_mem()
            graph = percent_to_graph(percent_used, args.length)
            if args.human_readable:
                total_rss = bytes_to_human_r(total_rss)
                print(f"{args.program:<10} {graph} {total_rss}")
            else:
                print(f"{args.program:<10} {graph} {total_rss} kB")
