"""将已提取视频证据转换为可供ChatGPT直接使用的反推提示词。
仅使用真实获得的数据；无法获取视频时不臆造内容。
"""
import json
from pathlib import Path

ROOT=Path("output")
report_path=ROOT/"report.json"
if not report_path.exists():
    raise SystemExit("未找到视频提取报告")
data=json.loads(report_path.read_text(encoding="utf-8"))
if data.get("status")!="extracted" or not data.get("frames"):
    (ROOT/"反推状态.txt").write_text("未取得视频画面，禁止编造反推提示词。\n错误："+str(data.get("error","unknown")),encoding="utf-8")
    raise SystemExit("需要实际视频画面后才能反推")

caps=data.get("visual_understanding",{})
descriptions={x.get("frame"):x.get("description","") for x in caps.get("captions",[])}
lines=[
"# 视频制作提示词反推｜证据驱动",
"",
"**原视频链接：** "+str(data.get("url","")),
"**识别状态：** 视频关键帧已提取；视觉模型状态："+str(caps.get("status","not_run")),
"",
"## 可观察到的画面证据"
]
for i,frame in enumerate(data.get("frames",[])):
    filename=frame.get("image",f"frame_{i:02d}.jpg")
    lines.extend([
        f"### {frame.get('second','?')} 秒",
        "- 图片文件："+filename,
        "- 画面文字："+(frame.get("screen_text") or "未识别到"),
        "- AI画面描述："+(descriptions.get(filename) or "尚未通过视觉模型分析，需由ChatGPT查看关键帧"),
    ])
lines.extend([
    "","## 声音及原文证据",
    data.get("transcript") or "未获取到有效语音转写，不能猜测对白、音乐、音效。",
    "","## 交给 ChatGPT 的专业反推指令",
    "请使用以上真实时间点的关键帧图片、画面OCR和音频转写，为该视频生成原创AI视频制作提示词。先根据逐帧证据说明主体、环境、动作、构图、镜头、光线、色彩、风格；结合实际音频文字说明对白。再按时间顺序输出可直接用于AI视频模型的中文提示词及独立分镜。凡只有静帧不能确认的运动、特效、音乐、音色、因果和制作工具，明确标注‘无法从现有证据确认’，不得补写成原视频事实。可以另列‘原创创作建议’，但必须与识别结果分开。不得模仿受保护的独特作品或角色。若视觉描述缺失，请直接查看随附帧图片，不得依据标题编造画面。",
    "","## 证据限制",
    "- 关键帧不能证明两帧之间的全部动作、运动轨迹和剪辑。",
    "- Whisper 识别的是语音，不等于音乐识别。",
    "- 仅抓取元数据或字幕不能代表已完整理解视频。",
])
(ROOT/"视频反推提示词.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("已生成证据驱动反推提示词，视觉模型状态："+str(caps.get("status","not_run")))
