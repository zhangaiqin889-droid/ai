# 开源软件复刻工具（长期保存）

本目录通过 **Git submodule** 固定完整上游代码版本，属于仓库的一部分。原有 AI 项目文件保持原样，不覆盖或删除。

- **Replica Skill**：11 个 Agent 技能，包括软件侦察、架构、后端、构建、差异比较、测试、部署等。来源 https://github.com/Jakeschincariol/replica-skill ，固定提交 `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`。
- **Remaster**：软件与网站分析、差异测试、复刻工作流 CLI 与 Skill。来源 https://github.com/thenavidm/remaster ，固定提交 `10a59350a132d847df3d4568bb1f1e23f049e146`。

## 下载完整工具

```bash
git clone --recurse-submodules https://github.com/zhangaiqin889-droid/ai.git
```

如果本地已克隆主仓库：
```bash
git submodule update --init --recursive
```

Remaster CLI：
```bash
node tools/复刻工具/remaster/skills/clone/scripts/remaster.mjs --help
```

Replica Skills 放在 `tools/复刻工具/replica-skill/replica-*/SKILL.md`，使用相关 Agent 时按需注册/加载，而非替换现有 Agent 配置。

## 已核验范围

云端沙盒真实克隆了两份上游仓库。Replica Skill 原项目执行 57 项 Python 测试，全部通过；Remaster CLI `--help` 成功。GitHub 持久保存源码引用及固定版本，不等于在 ChatGPT 模型内部安装，也不表示万兴脑图已复刻成功。今后运行时需在相应计算环境初始化 Git 子模块；付费模型/API 调用不得自动启用。GitHub 仓库本身为公共仓库，禁止存放密钥、私有代码或用户未授权资料。
