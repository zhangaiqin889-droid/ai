import os, re, json, base64, tempfile, subprocess, secrets
from urllib.parse import urlparse
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import yt_dlp

app=FastAPI(title="免费视频识别")
TOKEN=os.environ.get("VIDEO_ACCESS_TOKEN","")
HOSTS=("douyin.com","iesdouyin.com","tiktok.com","youtube.com","youtu.be","bilibili.com","b23.tv")
MAX_SECONDS=180

class Request(BaseModel):
    url: str
    token: str = ""

def permitted(url):
    p=urlparse(url)
    return p.scheme=="https" and any(p.hostname==h or (p.hostname or "").endswith("."+h) for h in HOSTS)

@app.get("/health")
def health(): return {"status":"ready","features":["video_metadata","frames","ocr","audio_file_extraction"],"vision_model":False,"speech_recognition":False}

@app.get("/",response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang="zh"><meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="utf-8"><title>视频识别</title><style>body{font:17px sans-serif;max-width:650px;margin:30px auto;padding:12px;background:#f7f7f8}input,button{box-sizing:border-box;width:100%;padding:14px;margin:8px 0;border:1px solid #aaa;border-radius:8px}button{background:#252525;color:white}pre{white-space:pre-wrap;overflow-wrap:anywhere}img{width:100%}</style><h2>免费视频内容提取</h2><p>支持公开可访问的视频。无登录绕过。当前提供关键画面与画面文字提取，尚不包含完整AI视觉/语音模型。</p><input id="url" placeholder="粘贴抖音视频完整链接"><input id="token" type="password" placeholder="访问密钥"><button onclick="run()">提取视频内容</button><div id="out"></div><script>async function run(){let out=document.getElementById('out');out.textContent='正在处理……';try{let r=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:document.getElementById('url').value,token:document.getElementById('token').value})});let j=await r.json();out.innerHTML='';let p=document.createElement('pre');p.textContent=JSON.stringify({...j,frames:undefined},null,2);out.appendChild(p);for(let f of j.frames||[]){let im=document.createElement('img');im.src='data:image/jpeg;base64,'+f.image;out.appendChild(im)}}catch(e){out.textContent='请求失败：'+e.message}}</script></html>"""

@app.post("/analyze")
def analyze(req: Request):
    if not TOKEN or not secrets.compare_digest(req.token,TOKEN):
        raise HTTPException(401,"访问密钥不正确")
    if not permitted(req.url):
        raise HTTPException(400,"仅支持已允许的视频平台HTTPS链接")
    with tempfile.TemporaryDirectory() as tmp:
        opts={"quiet":True,"no_warnings":True,"noplaylist":True,"socket_timeout":12,"retries":1,"extractor_retries":1,"http_headers":{"User-Agent":"Mozilla/5.0"},"outtmpl":tmp+"/video.%(ext)s","format":"worst[height<=480]/worst","max_filesize":30*1024*1024}
        try:
            with yt_dlp.YoutubeDL({**opts,"skip_download":True}) as y:
                info=y.extract_info(req.url,download=False)
            if info.get("duration") and info["duration"]>MAX_SECONDS: raise HTTPException(400,"视频超过3分钟限制")
            result={"title":info.get("title"),"duration":info.get("duration"),"description":(info.get("description") or "")[:2500],"uploader":info.get("uploader"),"subtitles_available":list((info.get("subtitles") or {}).keys()),"frames":[]}
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([req.url])
            media=next((x for x in Path(tmp).glob("video.*") if x.suffix not in (".part",".ytdl")),None)
            if not media: return {**result,"error":"平台未提供可下载的视频"}
            if media.stat().st_size>30*1024*1024: raise HTTPException(413,"下载超出30MB限制")
            for n,sec in enumerate((1,3,8)):
                image=Path(tmp)/f"frame{n}.jpg"
                try:
                    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(sec),"-i",str(media),"-frames:v","1","-vf","scale=480:-2","-y",str(image)],timeout=12,check=True)
                    if image.exists():
                        o=subprocess.run(["tesseract",str(image),"stdout","-l","chi_sim+eng"],capture_output=True,text=True,timeout=8)
                        result["frames"].append({"time_seconds":sec,"ocr":o.stdout.strip()[:1000],"image":base64.b64encode(image.read_bytes()).decode()})
                except Exception: pass
            return result
        except HTTPException: raise
        except Exception as ex:
            raise HTTPException(422,"无法获取视频：可能需要登录、链接已失效或平台限制。"+str(ex)[:250])
