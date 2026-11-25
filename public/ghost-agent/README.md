# THE GHOST V3 PC Companion

Install Python 3.10+, then in this folder run:

```powershell
py -m pip install -r requirements.txt
py ghost_agent.py
```

The first run creates `ghost-agent.token` and prints it. Keep it secret. macOS/Linux: use `python3` instead of `py`.

The service binds to 127.0.0.1:8765. Do not expose that port directly to the internet or bind to 0.0.0.0. For phone/remote access, create an authenticated Cloudflare Tunnel hostname pointing to http://localhost:8765, set GHOST_ALLOWED_ORIGIN to https://ghosttest.pk3285004.workers.dev before starting the agent, and add the HTTPS tunnel URL and token in THE GHOST → CORE. Enable Cloudflare Access on the tunnel hostname too.

Commands: help, status, processes, network, disk, uptime, hostname, platform, clear. No arbitrary shell execution, file transfer, or remote desktop is implemented. CPU temperature may be unavailable depending on hardware/OS.
