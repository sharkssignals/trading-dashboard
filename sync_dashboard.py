#!/usr/bin/env python3
"""
Export closed trades from bot's trades.json to trading-dashboard/trades_public.json
Then push to GitHub.
Run via cron every 5 minutes.
"""
import json
import subprocess
import os

BOT_TRADES = "/root/sharks-signal-bot-v3/data/trades.json"
DASHBOARD_DIR = "/root/trading-dashboard"
PUBLIC_FILE = os.path.join(DASHBOARD_DIR, "trades_public.json")

def export():
    # Load bot trades
    try:
        with open(BOT_TRADES) as f:
            all_trades = json.load(f)
    except:
        print("No trades file found")
        return

    # Filter only closed trades
    closed = {}
    for k, v in all_trades.items():
        if v.get("status") in ("CLOSED", "SL", "TP1", "TP2", "TP3") and v.get("closed_at"):
            # Remove raw_signal to keep file small
            clean = {key: val for key, val in v.items() if key != "raw_signal"}
            closed[k] = clean

    # Write to dashboard
    with open(PUBLIC_FILE, "w") as f:
        json.dump(closed, f, indent=2)

    # Git push
    os.chdir(DASHBOARD_DIR)
    subprocess.run(["git", "add", "trades_public.json"], capture_output=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode != 0:  # there are changes
        subprocess.run(["git", "commit", "-m", "Update trades"], capture_output=True)
        subprocess.run(["git", "push"], capture_output=True)
        print(f"Pushed {len(closed)} closed trades")
    else:
        print("No changes")

if __name__ == "__main__":
    export()
