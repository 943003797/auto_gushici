# auto_gushici
古诗词短视频自动剪辑系统

## 项目简介

auto_gushici是一个基于AI智能体的古诗词短视频自动剪辑系统，通过多智能体协作技术自动生成包含古诗词内容的短视频。该系统集成了语音合成、视频剪辑、素材管理等功能，为用户提供一键式古诗词视频创作解决方案。

## 核心功能

- 🤖 **多智能体协作**: 基于AutoGen的AI智能体分工协作
- 🎵 **语音合成**: 使用DashScope进行高质量TTS语音合成
- 🎬 **自动剪辑**: 集成剪映草稿API实现智能视频剪辑
- 📁 **素材管理**: 统一的字体、背景、音效、封面等资源管理
- 🎨 **一键生成**: 从古诗词文本到完整视频的自动化流程

## 技术架构

- **语言**: Python 3.13+
- **AI框架**: AutoGen AgentChat (多智能体协作框架)
- **语音服务**: 阿里云DashScope
- **UI框架**: Gradio
- **视频处理**: 剪映草稿API (pyjianyingdraft)

## 项目结构

```
auto_gushici/
├── agent/              # AI智能体模块
│   ├── agent.py       # 核心智能体
│   ├── agent_v3.py    # 智能体v3版本
│   ├── agent_scope.py # AgentScope集成
│   └── agent_ui.py    # UI交互智能体
├── autocut/           # 自动剪辑模块
│   ├── auto_cut.py    # 自动剪辑核心
│   ├── auto_cut_v2.py # 版本2
│   └── auto_cut_v3.py # 版本3
├── material/          # 素材资源
│   ├── baseDraft/     # 草稿模板
│   ├── bgm/          # 背景音乐
│   ├── bgv/          # 背景视频
│   ├── fonts/        # 字体文件
│   ├── reference_audio/ # 参考音频
│   └── sfx/          # 音效文件
├── openspec/         # OpenSpec文档
│   ├── AGENTS.md     # 智能体指令
│   └── project.md    # 项目规范
└── *.py             # 主程序文件
```

## 快速开始

1. **环境准备**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或 venv\Scripts\activate  # Windows
   ```

2. **安装依赖**
   ```bash
   pip install -e .
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置必要的API密钥
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

## 配置说明

主要配置文件：
- `.env`: 环境变量配置
- `material/baseDraft/draft_*.json`: 草稿模板配置
- `material/baseDraft/draft_*_config.json`: 业务逻辑配置

## 开发指南

- 遵循OpenSpec规范进行开发
- 使用多智能体架构进行功能模块设计
- 重视素材资源的组织和管理
- 关注音频视频处理的技术细节

### 详细技术文档

- **pyJianYingDraft 自动剪辑**: `openspec/doc/pyJianYingDraft_README.md`
  - 完整的剪映草稿库使用指南
  - 自动剪辑功能实现原理
  - 轨道管理和动画效果应用
  - 与古诗词视频制作的最佳实践

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。在贡献代码前，请确保：
1. 遵循现有的代码风格和架构模式
2. 添加适当的测试用例
3. 更新相关文档

---

*让古诗词在AI的助力下，重新焕发出新的光彩* ✨
