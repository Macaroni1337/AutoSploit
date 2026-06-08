<center><img src="https://user-images.githubusercontent.com/14183473/55991044-e9317000-5c6e-11e9-8730-a2e9d5c3ea68.jpg"></image></center>
<br>
As the name might suggest AutoSploit attempts to automate the exploitation of remote hosts. Targets can be collected automatically through Shodan, Censys or Zoomeye. But options to add your custom targets and host lists have been included as well. The available Metasploit modules have been selected to facilitate Remote Code Execution and to attempt to gain Reverse TCP Shells and/or Meterpreter sessions. Workspace, local host and local port for MSF facilitated back connections are configured by filling out the dialog that comes up before the exploit component is started.

_**Operational Security Consideration:**_

Receiving back connections on your local machine might not be the best idea from an OPSEC standpoint. Instead consider running this tool from a VPS that has all the dependencies required, available.

The new version of AutoSploit has a feature that allows you to set a proxy before you connect and a custom user-agent.

---

## Python 3 Modernisation (Macaroni1337 — June 2025)

This fork has been fully migrated to **Python 3** (tested on 3.10+). The original codebase was Python 2.7 only. A summary of what changed and what it means for you:

### What changed

| Area | Change |
|---|---|
| Python version | Python 2.7 → Python 3.10+. `pip2` / `python` commands below should now be `pip3` / `python3` (or just `python` in modern virtualenvs) |
| `raw_input()` | Replaced with `input()` everywhere |
| `print` statements | All corrected to `print()` calls |
| `distutils.spawn` | Replaced with `shutil.which` (distutils removed in Python 3.12) |
| `readline` | Made optional — the tool runs without it on platforms where readline is unavailable (e.g. Windows) |
| Shodan client | Raw HTTP calls replaced with the **official `shodan` Python library** |
| Censys client | Rewritten for the **v2 API** (`search.censys.io/api/v2`) — the v1 endpoint is no longer available |
| ZoomEye client | Hardcoded shared credentials removed. Now uses a **personal API key** stored in `etc/tokens/zoomeye.key` |
| Metasploit | Original subprocess/RC-script path kept. **pymetasploit3** added as an optional RPC-based alternative |
| Scope gate | New mandatory authorisation gate added before any exploit fires |
| Safe mode | New `--safe` flag added for dry-run reconnaissance |
| Dependencies | `requirements.txt` updated to current stable versions |

### New API key requirement — ZoomEye

ZoomEye previously used shared credentials bundled in the repository. Those are gone. You now need your own ZoomEye API key:

1. Register at [zoomeye.org](https://www.zoomeye.org) and generate a personal API key
2. On first run, AutoSploit will prompt you for it and save it to `etc/tokens/zoomeye.key`
3. Or create the file manually: `echo "YOUR_KEY" > etc/tokens/zoomeye.key`

### Censys v2 credentials

Censys now requires an **API ID** and **API Secret** (not a single token):

1. Log in at [search.censys.io](https://search.censys.io) → Account → API
2. On first run AutoSploit will prompt for both and save them to `etc/tokens/censys.key` (secret) and `etc/tokens/censys.id` (ID)

### New flags

**`--safe`** — Reconnaissance and module selection only. Exploitation modules are never fired. Use this to review what AutoSploit would target before committing to a live run.

```bash
python autosploit.py -s -q "apache" --safe
```

**`--scope PATH`** — Restrict exploitation to hosts within a defined scope file. Any gathered host not matching the scope is skipped. The file accepts individual IPs and CIDR ranges, one per line. Lines starting with `#` are comments.

```
# scope.txt
10.0.0.0/24
192.168.1.50
```

```bash
python autosploit.py -e -C default 10.0.0.1 4444 --scope scope.txt
```

**`--msf-rpc`** — Use pymetasploit3 to connect to a running `msfrpcd` daemon instead of shelling out to `msfconsole`. Useful when you want programmatic control or are running MSF headlessly.

```bash
# Start the MSF RPC daemon first
msfrpcd -P mypassword -S -f

# Then run AutoSploit with RPC
python autosploit.py -e -C default 10.0.0.1 4444 --msf-rpc --msf-rpc-pass mypassword
```

Additional RPC flags: `--msf-rpc-host` (default `127.0.0.1`), `--msf-rpc-port` (default `55553`).

### Mandatory authorisation gate

Before any exploitation module fires, AutoSploit will print a warning and require you to type:

```
I HAVE WRITTEN AUTHORISATION
```

exactly (case-sensitive). Anything else aborts the run. This applies to both interactive terminal mode and CLI mode. It does **not** apply to `--safe` / `--dry-run` runs.

---

# Helpful links

 - [Usage](https://github.com/NullArray/AutoSploit#usage)
 - [Installing](https://github.com/NullArray/AutoSploit#Installation)
 - [Dependencies](https://github.com/NullArray/AutoSploit#dependencies)
 - [User Manual](https://github.com/NullArray/AutoSploit/wiki)
   - [Extensive usage breakdown](https://github.com/NullArray/AutoSploit/wiki/Usage#usage-options)
   - [Screenshots](https://github.com/NullArray/AutoSploit/wiki/Examples-and-images)
   - [Reporting bugs/ideas](https://github.com/NullArray/AutoSploit/wiki/Bugs-and-ideas#bugs)
   - [Development guidelines](https://github.com/NullArray/AutoSploit/wiki/Development-information#development-of-autosploit)
 - [Shoutouts](https://github.com/NullArray/AutoSploit#acknowledgements)
 - [Development](https://github.com/NullArray/AutoSploit#active-development)
 - [Discord server](https://discord.gg/9BeeZQk)
 - [README translations](https://github.com/NullArray/AutoSploit#translations)

# Installation

> **Python 3 note:** All commands below that use `pip2` or reference Python 2 should be replaced with `pip3` (or `pip`) and `python3` (or `python`). The virtualenv step for macOS should also use `python3 -m venv` rather than `virtualenv`.

Installing AutoSploit is very simple, you can find the latest stable release [here](https://github.com/NullArray/AutoSploit/releases/latest). You can also download the master branch as a [zip](https://github.com/NullArray/AutSploit/zipball/master) or [tarball](https://github.com/NullArray/AutSploit/tarball/master) or follow one of the below methods;


##### Docker Compose
Using Docker Compose is by far the easiest way to get AutoSploit up and running without too much of a hassle.
```
git clone https://github.com/NullArray/AutoSploit.git
cd Autosploit/Docker
docker-compose run --rm autosploit
```

##### Docker
Just using Docker.
```
git clone https://github.com/NullArray/AutoSploit.git
cd Autosploit/Docker
# If you wish to edit default postgres service details, edit database.yml. Should work out of the box
# nano database.yml
docker network create -d bridge haknet
docker run --network haknet --name msfdb -e POSTGRES_PASSWORD=s3cr3t -d postgres
docker build -t autosploit .
docker run -it --network haknet -p 80:80 -p 443:443 -p 4444:4444 autosploit
```

Dev team contributor [Khast3x](https://github.com/khast3x) recently improved Docker operations as well as add more details to the README.md in the `Docker` subdirectory. For more information on deploying AutoSploit with Docker please be sure to click [here](https://github.com/NullArray/AutoSploit/tree/master/Docker) 


##### Cloning (Linux / Kali)
```bash
git clone https://github.com/NullArray/AutoSploit
cd AutoSploit
pip3 install -r requirements.txt
sudo python3 autosploit.py
```

> The tool requires root/administrator privileges to run. On Linux use `sudo`. On Kali running as root, call `python3 autosploit.py` directly.

AutoSploit is compatible with macOS, however you need to run it inside a virtual environment:

```bash
git clone https://github.com/NullArray/AutoSploit.git
cd AutoSploit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo python autosploit.py
```

## Usage

Starting the program with `python3 autosploit.py` will open an AutoSploit terminal session. The options for which are as follows.
```
1. Usage And Legal
2. Gather Hosts
3. Custom Hosts
4. Add Single Host
5. View Gathered Hosts
6. Exploit Gathered Hosts
99. Quit
```

Choosing option `2` will prompt you for a platform specific search query. Enter `IIS` or `Apache` in example and choose a search engine. After doing so the collected hosts will be saved to be used in the `Exploit` component.

AutoSploit can be started with a number of command line arguments/flags. Type `python3 autosploit.py -h` to display all the options available to you.

```
usage: python autosploit.py -c[z|s|a] -q QUERY [-O|A]
                            [-C WORKSPACE LHOST LPORT] [-e] [--whitewash PATH] [-H]
                            [--ruby-exec] [--msf-path] PATH [-E EXPLOIT-FILE-PATH]
                            [--rand-agent] [--proxy PROTO://IP:PORT] [-P AGENT] [-D QUERY,QUERY,..]

search engines:
  -c, --censys          use censys.io as the search engine to gather hosts
  -z, --zoomeye         use zoomeye.org as the search engine to gather hosts
  -s, --shodan          use shodan.io as the search engine to gather hosts
  -a, --all             search all available search engines to gather hosts
  -O, --overwrite       overwrite the host file with new search results
  -A, --append          append discovered hosts to the existing host file

requests:
  --proxy PROTO://IP:PORT
  --random-agent
  -P USER-AGENT, --personal-agent USER-AGENT
  -q QUERY, --query QUERY

exploits:
  -E PATH, --exploit-file PATH
  -C WORKSPACE LHOST LPORT, --config WORKSPACE LHOST LPORT
  -e, --exploit
  -d, --dry-run         never call msfconsole (original dry-run flag)
  -f PATH, --exploit-file-to-use PATH
  -H SCORE, --is-honeypot SCORE

misc arguments:
  --ruby-exec
  --msf-path MSF-PATH
  --whitelist PATH
  -D SEARCH [SEARCH ...]
  --safe                dry-run mode — recon only, no exploits fired
  --scope PATH          scope file of allowed IPs/CIDRs

msf rpc:
  --msf-rpc             use pymetasploit3 RPC instead of msfconsole subprocess
  --msf-rpc-host HOST   (default: 127.0.0.1)
  --msf-rpc-port PORT   (default: 55553)
  --msf-rpc-pass PASSWORD
```


## Dependencies

AutoSploit now requires **Python 3.10 or later**.

Install all dependencies with:

```bash
pip3 install -r requirements.txt
```

Current dependencies:

```
requests==2.32.3
psutil==6.1.1
beautifulsoup4==4.12.3
shodan==1.31.0
pymetasploit3==1.0.3
```

Since the program invokes functionality from the Metasploit Framework you need to have this installed also. Get it from Rapid7 by clicking [here](https://www.rapid7.com/products/metasploit/).

### API keys required

You will need at least one of the following to gather targets:

| Service | Where to get a key | Stored at |
|---|---|---|
| Shodan | [account.shodan.io](https://account.shodan.io) | `etc/tokens/shodan.key` |
| Censys | [search.censys.io](https://search.censys.io) → Account → API | `etc/tokens/censys.key` + `etc/tokens/censys.id` |
| ZoomEye | [zoomeye.org](https://www.zoomeye.org) → Profile → API Key | `etc/tokens/zoomeye.key` |

AutoSploit will prompt you for any missing keys on first run and save them automatically.

## Acknowledgements

Special thanks to [Ekultek](https://github.com/Ekultek) without whoms contributions to the project, the new version would have been a lot less spectacular.

Thanks to [Khast3x](https://github.com/khast3x) for setting up Docker support.

Python 3 migration, Censys v2 / ZoomEye v2 API updates, pymetasploit3 integration, scope gate and safe-mode additions by [Macaroni1337](https://github.com/Macaroni1337).

Last but certainly not least. Thanks to all who have submitted Pull Requests, bug reports, useful and productive contributions in general.  

### Active Development

If you would like to contribute to the development of this project please be sure to read [CONTRIBUTING.md](https://github.com/NullArray/AutoSploit/blob/master/CONTRIBUTING.md) as it contains our contribution guidelines.

Please, also, be sure to read our [contribution standards](https://github.com/NullArray/AutoSploit/wiki/Development-information#contribution-standards) before sending pull requests

If you need some help understanding the code, or want to chat with some other AutoSploit community members, feel free to join our [Discord server](https://discord.gg/DZe4zr2).

### Note

If you happen to encounter a bug please feel free to [Open a Ticket](https://github.com/NullArray/AutoSploit/issues).

Thanks in advance.

## Translations

 - [FR](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-fr.md)
 - [ZH](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-zh.md)
 - [DE](https://github.com/NullArray/AutoSploit/blob/master/.github/.translations/README-de.md)
