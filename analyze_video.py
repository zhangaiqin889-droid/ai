import os, json, subprocess, pathlib, sys, shutil
import yt_dlp
URL=os.environ.get("VIDEO_URL","").strip()
OUT=pathlib.Path("output"); OUT.mkdir(exist_ok=True)
ALLOWED=("douyin.com","iesdouyin.com","tiktok.com","youtube.com","youtu.be","bilibili.com","b23.tv")
from urllib.parse import urlparse
host=(urlparse(URL).hostname or "").lower()
if urlparse(URL).scheme!="https" or not any(host==d or host.endswith("."+d) for d in ALLOWED):
    raise SystemExit("Invalid platform URL")
config={"format":"worst[height<=480]/worst","outtmpl":str(OUT/"source.%(ext)s"),"noplaylist":True,"retries":1,"socket_timeout":15,"max_filesize":40*1024*1024,"quiet":True,"writesubtitles":True,"writeautomaticsub":True,"subtitleslangs":["zh-Hans","zh","en"]}
result={"url":URL,"status":"started","frames":[],"transcript":"","warnings":[]}
try:
    with yt_dlp.YoutubeDL(config) as y:
        info=y.extract_info(URL,download=False)
        result.update({"title":info.get("title"),"duration":info.get("duration"),"uploader":info.get("uploader"),"description":(info.get("description") or "")[:5000]})
        if info.get("duration",0)>180: raise RuntimeError("仅处理3分钟以内的视频")
        y.download([URL])
    media=next((p for p in OUT.glob("source.*") if p.suffix.lower() in [".mp4",".webm",".mkv"]),None)
    if media is None: raise RuntimeError("未找到视频文件")
    if media.stat().st_size>40*1024*1024: raise RuntimeError("视频大小超限")
    # 生成可播放 MP4 成品，并随关键帧上传为工作流 Artifact
    playback=OUT/"video_playback.mp4"
    encode=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(media),
        "-map","0:v:0","-map","0:a:0?","-vf","scale=trunc(min(480\\,iw)/2)*2:-2",
        "-c:v","libx264","-preset","veryfast","-crf","28","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","96k","-movflags","+faststart","-y",str(playback)],
        capture_output=True,text=True,timeout=180)
    if encode.returncode == 0 and playback.is_file() and playback.stat().st_size>0:
        result["playback"]={"file":playback.name,"bytes":playback.stat().st_size,"format":"mp4"}
    else:
        playback.unlink(missing_ok=True)
        result["warnings"].append("MP4 export failed: "+encode.stderr[-250:])
    for i,t in enumerate([1,3,6,10,20,40,60,90,120,150]):
        if result.get("duration") and t>result["duration"]: break
        f=OUT/f"frame_{i:02d}.jpg"
        p=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",str(media),"-frames:v","1","-vf","scale=640:-2","-y",str(f)],capture_output=True,timeout=25)
        if p.returncode==0 and f.is_file():
            o=subprocess.run(["tesseract",str(f),"stdout","-l","chi_sim+eng"],capture_output=True,text=True,timeout=20)
            result["frames"].append({"second":t,"image":f.name,"screen_text":o.stdout.strip()[:1200]})
    wav=OUT/"audio.wav"
    p=subprocess.run(["ffmpeg","-v","error","-i",str(media),"-vn","-ac","1","-ar","16000","-y",str(wav)],capture_output=True,timeout=60)
    if p.returncode==0:
        try:
            from faster_whisper import WhisperModel
            model=WhisperModel("tiny",device="cpu",compute_type="int8")
            segments,_=model.transcribe(str(wav),beam_size=1)
            result["transcript"]="\n".join(f"[{s.start:.1f}-{s.end:.1f}] {s.text}" for s in segments)
        except Exception as e: result["warnings"].append("transcription unavailable: "+str(e)[:140])
    else: result["warnings"].append("audio extraction failed")
    # 使用免费的开源视觉语言模型进行实际画面理解（区别于OCR）
    result["visual_understanding"]={"status":"not_verified","model":"HuggingFaceTB/SmolVLM2-256M-Video-Instruct","captions":[]}
    frames=[OUT / f"frame_{i:02d}.jpg" for i in range(10)]
    frames=[f for f in frames if f.is_file()][:3]
    if frames:
        try:
            import torch
            from transformers import AutoProcessor, AutoModelForImageTextToText
            model_id="HuggingFaceTB/SmolVLM2-256M-Video-Instruct"
            processor=AutoProcessor.from_pretrained(model_id)
            model=AutoModelForImageTextToText.from_pretrained(model_id).to("cpu")
            model.eval()
            for frame in frames:
                messages=[{"role":"user","content":[{"type":"image","path":str(frame)},{"type":"text","text":"Describe the visible people, animals, objects and actions in this image, using short factual English. Do not guess unseen events."}]}]
                inputs=processor.apply_chat_template(messages,add_generation_prompt=True,tokenize=True,return_dict=True,return_tensors="pt")
                with torch.inference_mode():
                    generated=model.generate(**inputs,max_new_tokens=90,do_sample=False)
                new_tokens=generated[:,inputs["input_ids"].shape[1]:]
                caption=processor.batch_decode(new_tokens,skip_special_tokens=True)[0]
                result["visual_understanding"]["captions"].append({"frame":frame.name,"description":caption})
            result["visual_understanding"]["status"]="generated_unreviewed"
        except Exception as err:
            result["visual_understanding"]["status"]="failed"
            result["visual_understanding"]["error"]=str(err)[:300]
            result["warnings"].append("visual model error (not a successful visual analysis)")
    result["status"]="extracted"
except Exception as e:
    result["status"]="failed"
    result["error"]=str(e)[:500]
finally:
    (OUT/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    for file in OUT.glob("source.*"): file.unlink(missing_ok=True)
    (OUT/"audio.wav").unlink(missing_ok=True)
    print(json.dumps({k:v for k,v in result.items() if k!="transcript"},ensure_ascii=False))
    if result["status"]!="extracted": sys.exit(1)
