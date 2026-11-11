"""基于真实提取的多模态证据形成可直接使用的中文视频创作提示词。"""
import json
from pathlib import Path

out=Path("output")
p=out/"report.json"
if not p.exists():
    raise SystemExit("缺少提取报告")
d=json.loads(p.read_text(encoding="utf-8"))
if d.get("status")!="extracted" or not d.get("frames") or not d.get("playback"):
    (out/"反推状态.txt").write_text("未取得完整视频与关键帧，禁止虚构： "+str(d.get("error",d.get("status"))),encoding="utf-8")
    raise SystemExit("缺少原始视频证据")
caps=d.get("visual_understanding",{})
caption_map={str(x.get("frame")):str(x.get("description","")).strip() for x in caps.get("captions",[])}
dur=d.get("duration","未知")
shots=[]
for i,x in enumerate(d["frames"]):
    t=x.get("second","?")
    img=x.get("image","")
    desc=caption_map.get(img,"")
    ocr=str(x.get("screen_text","")).strip()
    shots.append(f"镜头{i+1}｜参考{t}秒，关键帧{img}：\n可见主体与环境：{desc if desc else '未完成视觉描述，需查看关键帧确认'}\n画面文字：{ocr or '无可靠识别'}\n制作建议：保留此帧的角色比例、服装、场景、光影与构图，使用低幅度自然运动；原镜头具体运镜、转场和运动轨迹未经核实。")
transcript=str(d.get("transcript","")).strip() or "未识别到可核实的人声。"
text=f"""# 视频反推与原创生成提示词

## 素材核验
来源：{d.get('url','')}
标题：{d.get('title','未知')}
时长：{dur} 秒
完整MP4：{d['playback'].get('file')}
已提取关键帧：{len(d['frames'])}张
视觉识别状态：{caps.get('status','未知')}（模型描述未人工核验）

## 可直接使用的AI视频制作提示词
根据以下真实参考镜头，制作一条原创9:16竖屏短视频，整体时长约{dur}秒。保持核心人物脸型、发型、衣着、体态与场景色彩在镜头之间一致。将各参考帧的主体、背景、色彩、光影、空间层次及构图转化为流畅的短片；动画只添加幅度适度、自然可信的动作。根据真实画面证据采用一致的2D/3D插画或实拍质感，不得在未知时擅自指定。采用稳定运镜、柔和转场和连贯节奏，字幕置于安全区，清晰可读。背景音乐仅以视频主题作原创配乐建议，不声称与原片一致。

### 逐镜头参考提示词
{chr(10).join(shots)}

### 已提取声音内容（自动转写，可能有误）
{transcript}

### 可复制关键词
9:16竖屏，主体统一，风格一致，场景与人物连续，构图还原，色彩与光影匹配，逐镜头生成，柔和运动，高清，画面稳定，字幕清晰，避免五官变形、手指错误、闪烁、服饰漂移、主体突变。

### 真实性边界
- 真实下载并提取视频、关键帧、语音；这里只描述已获得的视觉与听觉证据。
- 视觉模型输出可能有识别错误，实际画面以随附图像为准。
- 单张关键帧不足以确定原片中两帧之间的动作、运镜和剪辑。
- ASR不是完整音乐分析；歌词及背景声需复核。
"""
(out/"视频反推提示词.md").write_text(text,encoding="utf-8")
print("生成反推制作提示词：",len(shots),"个镜头；",len(transcript),"字语音证据")
