# GitHub 云端 OpenClaw 工作 Agent（安装配置）

## 已写入 GitHub
- `.github/workflows/openclaw-replica-worker.yml`：GitHub Actions 标准 Runner 上安装固定版本 `openclaw@2026.11.1`；只读拉取当前仓库及固定版本的 Replica Skill、Remaster；运行 CLI、技能发现和脑图核心测试；上传证据。
- `cloud-agent/skills/software-replica/SKILL.md`：OpenClaw 原生工作区复刻 Skill；工作流执行时复制到 `~/.openclaw/workspace/skills/software-replica/SKILL.md`。
- `edrawmind-replica/`：现存独立开发目录，主要数据引擎已有 7 项测试通过；远未达到万兴 V14 完全功能等效。

## 当前限制（不能伪装完成）
GitHub 是代码仓库；GitHub-hosted Actions Runner 每次启动、执行、退出，不提供全天候运行 OpenClaw Gateway。
目前未配置且未授权任何可用的云端免费 LLM 模型，不能执行自然语言 Agent 的真实端到端工作，更不能自动一比一复刻闭源的万兴软件。未来绑定免费模型需要核验免费额度、API、权限和效果；禁止自动产生付费请求。
此工作流只读访问仓库，不存放 API Key 或复制用户私有材料；默认不发布到生产网站。
本文件为配置记录，不是安装成功报告；只有 GitHub Actions 实际执行并查看日志，方可确认 Runner 中成功安装与加载 Skill。
官方来源：https://docs.openclaw.ai/install ；https://docs.openclaw.ai/tools/skills ；https://docs.openclaw.ai/cli/agent

## 真正验收门槛
1. GitHub Actions job 全绿：OpenClaw version / agent --help / skills check / Remaster CLI / Replica Skill / node tests。
2. Agent 带真实免费模型执行一次独立任务，并产出可检查文件；多轮状态能恢复。
3. 以万兴官方可访问参考为基准，功能矩阵逐项验证视觉、交互、模板资源、AI、导出、PPT/视频，并在合法授权范围内复刻。
4. 安全预览接入意大利语站，测试通过再发布；保护旧站与旧数据。

[工作流页面](https://github.com/zhangaiqin889-droid/ai/actions/workflows/openclaw-replica-worker.yml)
