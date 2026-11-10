# Plan Dashboard (stage 1 done)

Read-only dashboard for the current film's plan. Reads Films/EPxx/plan.json plus film.yaml, cost-log.csv, 00_admin/subscriptions.csv (the current file; _vN copies are ignored) and credit-balances.csv. Never writes to the project folders. Its only own file is a "last seen" copy of the plan in ~/Library/Application Support/PlanDashboard/.

## Files
- reader.py : reads everything, makes the warnings and the change list (python 3 standard library only, nothing to install)
- server.py : tiny local server that serves index.html and /api/data (this Mac only, unless you add --lan)
- index.html : the page (same look as the published dashboard, plus the times bar, warnings, what-changed panel and subscriptions)
- tests/ : 18 automated checks (`python3 -m unittest discover -s tests`) and two sample data snapshots used for screenshots

## Try it now (no install)
In Terminal: `cd "<Sarv Studio Code>/dashboard" && python3 server.py --open`
It opens in your browser. Press Refresh to re-read the files. Ctrl+C stops it.

## On your phone or iPad (optional, off by default)
In Terminal: `cd "<Sarv Studio Code>/dashboard" && python3 server.py --lan`
- It prints an address like `http://Your-Mac-Name.local:8765/`. Open that on a device on the same Wi-Fi.
- Warning: anyone on the same Wi-Fi can see the page while it runs (plan, costs, subscriptions). Use it on your home network only and press Ctrl+C when done.
- Other devices can only read. "Mark as seen" works only on the Mac itself (other devices get "Read-only from other devices").
- The first time, macOS may ask whether Python may accept incoming network connections. Allow it, or other devices cannot reach the page.
- The Animation Dashboard app never uses --lan; it always stays on this Mac.

## Settings (optional)
- PERSIAN_STORIES = path to the Persian Stories folder (default: the folder next to Sarv Studio Code)
- PLAN_DASHBOARD_DATA = where the "last seen" copy is kept
- SARV_USER = whose log files this Mac writes (reza or edris; also read from SARV_USER= in the code folder's .env). The spend total adds every person's 05_ops/cost-log*.csv and shows the split per person when more than one has rows. The cost-log link opens your own file; add ?person=<name> to view another person's.

## Stage 2 (Claude Code on the Mac, one step at a time)
Paste this into Claude Code (desktop app, folder: Sarv Studio Code):

> Read dashboard/README.md. Goal: wrap dashboard/server.py and index.html as a Mac app named "Plan Dashboard" with its own window and Dock icon, installed in ~/Applications. Keep it read-only. Say in plain language what you will do before each step. Ask me before any install. Use the lightest option (Python plus pywebview if python3 is on this Mac; otherwise tell me the options and costs). Task links must open in my normal browser. Do not delete anything. After building, open the app, press Refresh, take a screenshot and tell me literally what you see. Log the job in 05_ops/time-log.csv and decisions.md.
