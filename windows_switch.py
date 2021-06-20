#!/usr/bin/python3

import argparse
import subprocess
import sys

from collections import defaultdict

# Mapping between the textual window identifier returned by wmctrl and the application binary
window2app={"jetbrains-phpstorm.jetbrains-phpstorm": "/snap/bin/phpstorm",
            "slack.Slack": "/snap/bin/slack",
            "chromium.Chromium": "/snap/bin/chromium",
            "spotify.Spotify": "/snap/bin/spotify",
            "terminator.Terminator": "/usr/bin/terminator",
            "Navigator.Firefox": "/usr/lib/firefox/firefox",
            "Mail.Thunderbird": "/usr/bin/birdtray"
            }


def get_win_info():
    """ Return a dictionary of textual window identifier mapping to a list of numerical window id
    """
    info = defaultdict(list)
    wlist = subprocess.check_output(["wmctrl", "-l", "-x"]).decode("utf-8")
    for line in wlist.split("\n"):
        if not line: 
            continue
        id, _, text, _ = line.split(None, 3)
        # convert to int to make true hexadecimal comparison
        info[text].append(int(id, 0))
    return info

def get_active_win_id():
    """ Return the numerical if of the active window
    """
    active_info = subprocess.check_output(["xprop", "-root", "32x", " $0", "_NET_ACTIVE_WINDOW"]).decode("utf-8")
    _, active_id = active_info.split()
    return int(active_id, 0)


def get_win_ids(text, win_info):
    """ For a given textual window identifier, return the list of numerical window id
    """
    for win_text, win_ids in win_info.items():
        if text == win_text:
            return win_ids
    return []

def pick_win_id(ids):
    """ Choose the next window identifier to switch to
    """
    if not ids:
        return None
    active_id = get_active_win_id()
    if len(ids) > 1 and active_id in ids:
        active_id_idx = ids.index(active_id)
        if active_id_idx < len(ids) - 1:
            return ids[active_id_idx + 1]
        # else if it's the last one, then switch to the first one
    return ids[0]

def switch_to_win(id):
    if id:
        subprocess.run(["wmctrl", "-i", "-a", hex(id)])

parser = argparse.ArgumentParser("Switch the focus to the given application, or launch it if needed.")
parser.add_argument("windows", nargs="+", help="Window identifier as returned by 'wmctrl -l'. It should match exactly, case sensitive")
args = parser.parse_args()

info = get_win_info()
# Get all the window ids in the order of the windows arguments
ids = []
for window in args.windows:
    ids += get_win_ids(window, info)

# If some windows are found, pick one and switch the focus to it
if ids:
    picked_id = pick_win_id(ids)
    switch_to_win(picked_id)
    sys.exit(0) 

# If no window found, launch the app if defined
for window in args.windows:
    if window in window2app:
        app = window2app[window]
        subprocess.run([window2app[window]])
        sys.exit(0) 

