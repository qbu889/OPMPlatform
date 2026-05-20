# Claude Code Skills 安装指南

## 已配置的 Skills

以下 skills 已在 `.claude/settings.local.json` 中启用：

- superpowers
- gsd
- find-skills
- web-design-guidelines
- frontend-design
- agent-browser

## 安装方法

### 方法 1: 使用官方技能市场（推荐）

在 Claude Code 中运行：
```
/skills marketplace
```

然后浏览并安装所需的 skills。

### 方法 2: 手动下载

1. 访问 Claude Code Skills 仓库：
   - https://github.com/anthropics/claude-code-skills
   - 或搜索各个 skill 的独立仓库

2. 下载 skill 文件夹到：
   ```
   .claude/skills/<skill-name>/
   ```

3. 每个 skill 应包含：
   - `SKILL.md` - 技能描述和使用说明
   - 其他支持文件

### 方法 3: 从社区获取

常见的 skills 来源：
- GitHub 搜索 "claude-code-skill"
- Claude Code 社区论坛
- npm packages (需要特殊配置)

## 验证安装

在 Claude Code 中运行：
```
/skills list
```

查看已安装的 skills。

## 注意事项

- Skills 是本地 Markdown 文件，不是 npm 包
- 每个 skill 必须有 `SKILL.md` 文件
- 确保权限设置允许读取 `.claude/skills/` 目录
