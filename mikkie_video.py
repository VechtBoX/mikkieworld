import os, time, json, urllib.request, urllib.error
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/mikkieworld/output")
MPT_API_BASE = "http://127.0.0.1:8080/api/v1"
os.makedirs(OUTPUT_DIR, exist_ok=True )

def _post(ep, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"{MPT_API_BASE}{ep}", data=data, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def _get(ep):
    with urllib.request.urlopen(f"{MPT_API_BASE}{ep}", timeout=30) as r: return json.loads(r.read())

def _download(fp, dest):
    urllib.request.urlretrieve(f"{MPT_API_BASE}/download/{urllib.request.quote(fp, safe='')}", dest)

def check_mpt():
    try: _get("/tasks"); return True
    except: return False

def generate_video(prompt, style="mikkie_world", language="nl", voice="nl-NL-MaartenNeural", duration=60, aspect_ratio="16:9"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUTPUT_DIR, f"video_{ts}.mp4")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🎬 MIKKIE WORLD | {prompt}")
    if not check_mpt():
        raise RuntimeError("❌ Start MoneyPrinterTurbo eerst: cd ~/MoneyPrinterTurbo && source venv/bin/activate && python3 main.py")
    print("→ API bereikbaar ✅  Taak aanmaken...")
    resp = _post("/videos", {"video_subject": prompt, "video_language": language, "voice_name": voice, "video_duration": duration, "video_aspect": aspect_ratio, "subtitle_enabled": True, "bgm_type": "random", "bgm_volume": 0.2})
    task_id = (resp.get("data") or {}).get("task_id") or resp.get("task_id")
    if not task_id: raise ValueError(f"Geen task_id: {resp}")
    print(f"→ Taak: {task_id}  Genereren", end="", flush=True)
    elapsed, video_path = 0, None
    while elapsed < 600:
        time.sleep(5); elapsed += 5; print(".", end="", flush=True)
        try: d = _get(f"/tasks/{task_id}").get("data", {})
        except: continue
        s = str(d.get("state") or d.get("status", ""))
        if s in ("complete","completed","success","done","1"):
            video_path = d.get("video_path") or d.get("file_path"); print(f"\n✅ Klaar na {elapsed}s!"); break
        elif s in ("failed","error","-1"): raise RuntimeError(f"Mislukt: {d.get('message','?')}")
    if not video_path: raise TimeoutError("Timeout na 600s")
    print(f"→ Downloaden...")
    _download(video_path, out)
    print(f"✅ Video: {out} ({os.path.getsize(out)/1048576:.1f} MB)")
    return out

if __name__ == "__main__":
    generate_video("Een schattige aap en olifant bouwen een boomhut in het bos")
