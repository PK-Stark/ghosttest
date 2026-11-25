#!/usr/bin/env python3
"""THE GHOST V3 companion: read-only PC telemetry and a safe command allowlist."""
import os,json,time,socket,platform,secrets,argparse
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
try: import psutil
except ImportError: raise SystemExit("Run: python -m pip install psutil")
HERE=Path(__file__).resolve().parent
TOKEN=os.environ.get("GHOST_API_TOKEN","").strip()
if not TOKEN:
    p=HERE/"ghost-agent.token"
    if p.exists(): TOKEN=p.read_text().strip()
    else:
        TOKEN=secrets.token_urlsafe(32);p.write_text(TOKEN)
        try:p.chmod(0o600)
        except OSError:pass
ORIGIN=os.environ.get("GHOST_ALLOWED_ORIGIN","https://ghosttest.pk3285004.workers.dev")
LAST=psutil.net_io_counters();LAST_T=time.time()
def human(v):
    for u in ("B","KB","MB","GB","TB"):
        if v<1024:return "%.1f %s"%(v,u)
        v/=1024
    return "%.1f PB"%v
def snapshot():
    global LAST,LAST_T
    cpu=psutil.cpu_percent(interval=.15);m=psutil.virtual_memory();s=psutil.swap_memory();d=psutil.disk_usage(str(Path.home()))
    n=psutil.net_io_counters();now=time.time();dt=max(.01,now-LAST_T);rx=max(0,n.bytes_recv-LAST.bytes_recv)/dt;tx=max(0,n.bytes_sent-LAST.bytes_sent)/dt;LAST,LAST_T=n,now
    ips=[]
    for group in psutil.net_if_addrs().values():
        for a in group:
            if a.family==socket.AF_INET and not a.address.startswith("127."):ips.append(a.address)
    procs=[]
    for p in psutil.process_iter(["pid","name","memory_percent"]):
        try:procs.append({"pid":p.info["pid"],"name":p.info["name"] or "unknown","cpu":p.cpu_percent(None),"memory":p.info["memory_percent"] or 0})
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    temp=None
    try:
        vals=[x.current for group in psutil.sensors_temperatures().values() for x in group if x.current is not None]
        if vals:temp=round(max(vals),1)
    except Exception:pass
    return {"hostname":socket.gethostname(),"platform":platform.platform(),"uptime":human(time.time()-psutil.boot_time()),"cpu_percent":cpu,"cpu_temp":temp,"memory":{"percent":m.percent,"used_human":human(m.used),"total_human":human(m.total)},"swap":{"percent":s.percent},"disk":{"percent":d.percent,"free_human":human(d.free)},"network":{"online":bool(ips),"ips":sorted(set(ips)),"rx_rate":rx,"tx_rate":tx},"processes":sorted(procs,key=lambda x:x["cpu"],reverse=True)[:12]}
def run(cmd):
    c=cmd.strip().lower()
    if c=="help":return "Allowed: help, status, processes, network, disk, uptime, hostname, platform, clear"
    if c=="clear":return "__CLEAR__"
    if c=="status":
        x=snapshot();return "CPU %.1f%% | RAM %.1f%% | DISK %.1f%%"%(x["cpu_percent"],x["memory"]["percent"],x["disk"]["percent"])
    if c=="processes":return "\n".join("%7s  %-26s CPU %.1f%% MEM %.1f%%"%(p["pid"],p["name"][:26],p["cpu"],p["memory"]) for p in snapshot()["processes"])
    if c=="network":
        x=snapshot()["network"];return "IP: "+(", ".join(x["ips"]) or "none")+"\nStatus: "+("online" if x["online"] else "offline")
    if c=="disk":
        x=psutil.disk_usage(str(Path.home()));return "Used %s / %s (%s%%), free %s"%(human(x.used),human(x.total),x.percent,human(x.free))
    if c=="uptime":return human(time.time()-psutil.boot_time())
    if c=="hostname":return socket.gethostname()
    if c=="platform":return platform.platform()
    return "Command not allowed. Type help."
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def headers(self,status=200):
        self.send_response(status);o=self.headers_in.get("Origin","")
        if o==ORIGIN:self.send_header("Access-Control-Allow-Origin",o);self.send_header("Vary","Origin")
        self.send_header("Access-Control-Allow-Headers","Authorization, Content-Type");self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS");self.send_header("Content-Type","application/json");self.send_header("Cache-Control","no-store");self.end_headers()
    def reply(self,status,obj):
        self.send_response(status);o=self.headers.get("Origin","")
        if o==ORIGIN:self.send_header("Access-Control-Allow-Origin",o);self.send_header("Vary","Origin")
        self.send_header("Access-Control-Allow-Headers","Authorization, Content-Type");self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS");self.send_header("Content-Type","application/json");self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(json.dumps(obj).encode())
    def auth(self):return secrets.compare_digest(self.headers.get("Authorization",""),"Bearer "+TOKEN)
    def do_OPTIONS(self):self.reply(204,{})
    def do_GET(self):
        if not self.auth():return self.reply(401,{"error":"Unauthorized"})
        if self.path!="/api/metrics":return self.reply(404,{"error":"Not found"})
        try:self.reply(200,snapshot())
        except Exception as e:self.reply(500,{"error":str(e)})
    def do_POST(self):
        if not self.auth():return self.reply(401,{"error":"Unauthorized"})
        if self.path!="/api/command":return self.reply(404,{"error":"Not found"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>2048:return self.reply(413,{"error":"Too large"})
            body=json.loads(self.rfile.read(n) or b"{}");self.reply(200,{"output":run(str(body.get("command",""))[:120])})
        except Exception as e:self.reply(400,{"error":str(e)})
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8765);a=ap.parse_args()
    print("THE GHOST PC companion:",a.host,a.port);print("Allowed origin:",ORIGIN);print("Private API token:",TOKEN);print("Keep this service on localhost; use an authenticated HTTPS tunnel for remote access.")
    ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
