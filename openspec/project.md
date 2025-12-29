# Project Context

## Purpose

auto_gushici是一个古诗词短视频自动剪辑系统，利用AI智能体技术自动生成包含古诗词内容的短视频。该系统集成了多智能体协作、音频处理、视频剪辑和素材管理功能，为用户提供一键式古诗词视频创作解决方案。

## Tech Stack

- **核心语言**: Python 3.13+
- **AI框架**: AutoGen AgentChat (多智能体协作框架)
- **语音服务**: DashScope (阿里云语音合成)
- **UI框架**: Gradio
- **视频处理**: 剪映草稿API (pyjianyingdraft)
- **配置管理**: Python-dotenv

## Project Conventions

### Code Style

- 使用Python标准代码风格 (PEP 8)
- 函数和变量命名使用下划线分隔 (snake_case)
- 类名使用PascalCase
- 重要函数需要添加类型注解

### Architecture Patterns

- **多智能体架构**: 基于AutoGen的多智能体协作模式
- **模块化设计**: 按功能分离为agent、autocut、material等模块
- **配置驱动**: 使用JSON配置文件管理草稿和业务配置
- **资源管理**: 统一的素材管理目录结构

### Testing Strategy

- 单元测试优先，确保核心功能的稳定性
- 集成测试验证多智能体协作流程
- 端到端测试确保完整视频生成流程

### Git Workflow

- 主分支 (main) 保持稳定可部署状态
- 功能分支 (feature/*) 用于新功能开发
- 修复分支 (hotfix/*) 用于紧急修复
- 提交信息使用清晰的描述性标题

## Domain Context

### 古诗词视频制作领域知识

- **音频处理**: TTS语音合成，背景音乐混音，音效处理
- **视频剪辑**: 自动剪裁、场景切换、转场效果
- **素材管理**: 字体、背景视频、音效、封面等资源组织
- **AI协作**: 多智能体分工协作，实现复杂的内容生成流程

### 业务流程

1. **内容策划**: AI智能体分析古诗词内容，制定视频策略
2. **素材准备**: 自动收集或生成所需的音频、视频、图像素材
3. **剪辑合成**: 智能剪辑算法将素材组合成完整视频
4. **质量优化**: 自动调整音频音量、视频节奏等技术参数

## Important Constraints

- **依赖外部API**: 需要稳定的网络连接访问DashScope等云服务
- **资源文件管理**: 大量音视频素材需要有效的存储和管理策略
- **处理性能**: 视频渲染和音频处理可能消耗较多计算资源
- **格式兼容性**: 需要支持主流视频格式的输入输出

## External Dependencies

- **阿里云DashScope**: 语音合成服务，提供TTS功能
- **pyJianYingDraft**: 剪映草稿API，视频剪辑和导出功能
- **Gradio**: Web UI界面框架
- **AutoGen**: AI智能体对话框架

### 详细文档

- **pyJianYingDraft 使用指南**: `openspec/doc/pyJianYingDraft_README.md`
  - 完整的库使用说明
  - 自动剪辑功能实现原理
  - 与项目集成的最佳实践
