# 创意能力（与商业机会库独立）

## 1. Creative Ideation
来源：[NousResearch/hermes-agent — creative-ideation](https://github.com/NousResearch/hermes-agent/tree/c9b20d7bc08dec1e10779a06d7d9073bc6e7e418/optional-skills/creative/creative-ideation)。MIT，原 Skill 版本 2.1.0。个人 AI 软件工厂插件增加独立 `creative-ideation` 路由 Skill；原始源代码/方法参考以此固定 SHA 追溯。没有部署庞大的 Hermes Agent 主程序，也不需要付费模型。

## 2. Unbuilt Ideas
以 Git 子模块锁定整个开源创意 Markdown 资料仓库：
- 来源：https://github.com/Rapid-alchemistry/unbuilt-ideas
- 固定 SHA：`65568eea1284adb7169f4f5ff431d38a80b345c6`
- MIT 许可；仓库是创意文档集合，不是可执行数据库或 AI 服务。

本仓库已加入 `tools/创意能力/unbuilt-ideas` Git 子模块。要离线获得全部创意文档，在已克隆的本仓库目录运行：

```bash
git submodule update --init --recursive
```

## 区分
通用创意（音乐、视频、故事、设计、软件、产品）调用 `creative-ideation` 和 `creative-idea-vault`。商业副业、投资及利润验证才调用原有 `business-ideas-research`。无用户确认不得使用收费模型、自动部署、删除项目或添加定期抓取。当前仅确认开源源与主控插件配置，未将任何未经验证的创意称作已盈利。
