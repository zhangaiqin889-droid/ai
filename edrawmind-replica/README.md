# 万兴脑图 V14 功能等效复刻 — 施工记录（2026-11-13）

**施工引擎：已安装 Replica Skill / replica-recon、Remaster。** 仅独立重建公共功能和交互，不复制闭源源码、私有 API、受保护素材或品牌视觉。当前源码在独立工作分支，不动用户正式意大利语网站。

## 官方功能证据
- 官方用户指南：https://edrawmind.wondershare.com/guide/
- 版本历史：https://edrawmind.wondershare.com/whats-new.html （2026-09-15 V14）
- AI 视频：https://edrawmind.wondershare.com/guide/ai-video-export-function.html
- AI PPT：https://edrawmind.wondershare.com/guide/ai-presentation.html

## 要求追踪
| ID | 功能 | 状态 |
|---|---|---|
| F01 | 树节点新增/兄弟主题/更新/删除/移动/防循环 | 核心引擎已实现，单元测试通过 |
| F02 | 撤销/重做和状态序列化 | 核心引擎已实现，单元测试通过 |
| F03 | 节点关系线和清理 | 数据层已实现，单元测试通过 |
| F04 | Markdown/JSON 导入导出 | 数据层已实现，单元测试通过 |
| F05 | 节点任务数据、层级和布局类型 | 数据层已实现，单元测试通过 |
| F06 | 专业图形交互、样式/手绘/布局渲染 | 尚未实现 |
| F07 | 多视图：大纲、看板、甘特、演示 | 尚未实现（仅数据基础） |
| F08 | PDF/Office/图片/其他脑图格式导入导出 | 尚未实现 |
| F09 | AI 文档分析、扩展、摘要、校对 | 尚未实现 |
| F10 | 可编辑 PPTX、信息图、知识卡生成 | 尚未实现 |
| F11 | AI 脑图视频：画面、分镜、配音、字幕、合成 | 尚未实现 |
| F12 | 模板库、云协作、历史、权限 | 尚未实现 |
| F13 | 意大利语学习扩展和正式网站集成 | 尚未实现 |

## 真正执行的验收
在 Vercel 独立 Sandbox 中通过 GitHub 克隆此分支，运行：
```bash
cd edrawmind-replica && node --test tests/mindmap.test.mjs
```
结果：7 tests、7 pass、0 fail。测试仅覆盖数据引擎，不覆盖 UI/视频/AI/成品或 V14 完整对标。没有完整 1:1 复刻成功的结论。

## 技术约束
不自动使用付费 AI/API，不修改生产网站，不把静态页面/假按钮当作完成功能。
