---
name: project-status
description: AutoSploit Python 3 migration status — what was done, what still needs a live Kali environment to validate
metadata:
  type: project
---

Python 3 migration completed 2026-06-08.  All imports clean under Python 3.14 with -W error.  Banner renders and --help displays correctly.

**Why:** Codebase was Python 2.7-only (EOL 2020); owner wants it Kali-ready.

**What was done:**
- All `raw_input()` → `input()` across 5 files
- Fixed backwards compat shim in terminal.py
- Fixed bare `print error_traceback` → `print(error_traceback)` in main.py
- Replaced `distutils.spawn.find_executable` with `shutil.which`
- Made `readline` import optional (Windows compat)
- Fixed `map()` iterator subscript in ip_generator.py
- Fixed bytes vs str bugs in issue_creator.py, zoomeye.py, settings.py
- Fixed unclosed file handles at module level in settings.py
- Fixed stale regex escapes (`\w`, `\-`)
- Replaced raw-HTTP Shodan client with official `shodan` Python library
- Added `pymetasploit3` to requirements.txt (RPC path documented in exploiter.py comments)
- Added `lib/scope.py` — authorization gate + scope validator
- Added `--safe` and `--scope PATH` CLI flags
- Authorization gate added to exploiter.start_exploit() (must type full phrase)
- Scope file filtering added (CIDR/IP, skips out-of-scope hosts with warning)
- requirements.txt updated to current stable pinned versions

**How to apply:** Next steps require a live Kali environment — see what is broken/incomplete below.

**Session 2 additions (2026-06-08):**
- Censys rewritten for v2 API (search.censys.io/api/v2/hosts/search, Basic auth, cursor pagination)
- ZoomEye rewritten: hardcoded credentials removed, now uses personal API key from etc/tokens/zoomeye.key
- API_KEYS / load_api_keys updated to include zoomeye; API_URLS updated to current endpoints
- pymetasploit3 RPC path fully implemented in exploiter._exploit_via_rpc(); connects to msfrpcd, runs modules, detects new sessions, logs to CSV
- Added --msf-rpc / --msf-rpc-host / --msf-rpc-port / --msf-rpc-pass CLI flags
- Terminal exploit path also prompts for RPC vs subprocess choice
- Token routing fixed in terminal.py do_api_search and cmd.py single_run_args (zoomeye now gets its own token)
- --safe dry-run tested end-to-end: scope filtering, out-of-scope labelling, no exploit fires

**Still needs live testing (updated):**
1. Metasploit subprocess path — msfconsole not on this machine; RC-script generation logic is sound but output parsing untested against real MSF output
2. pymetasploit3 RPC path — implemented but needs live msfrpcd to validate connection, module execution, and session detection
3. Shodan library — needs real API key; pagination (only fetches first page currently) may need expanding
4. Censys v2 — rewritten but needs real API ID+secret to validate response parsing
5. ZoomEye v2 — rewritten but needs real API key; response format assumption (matches[i]["ip"] is a string) needs confirming against live API
6. issue_creator.py auto-filing — GitHub auth.key token almost certainly expired; will fail silently
7. Service checks (postgres, apache2) — Linux only; Windows exits with "platform not supported" (expected)
8. Admin check — blocks --help without root/admin (expected)
