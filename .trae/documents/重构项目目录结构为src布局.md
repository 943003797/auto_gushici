# 项目目录结构重构计划

## 当前状态分析
- 项目根目录混乱，Python模块散布在多个目录中
- 需要保留根目录的指定文件：v1.py, v3.py, v4.py, v5.py, videoCut.py, videoToVector.py
- 注意：v2.py在当前项目中不存在

## 重构目标
将项目重构为标准的Python src布局，提高代码组织性和可维护性

## 重构计划

### 1. 创建src/目录结构
```
src/
├── __init__.py
├── core/                    # 核心功能模块
│   ├── __init__.py
│   ├── cover/              # 封面生成相关
│   │   ├── __init__.py
│   │   ├── cover.py
│   │   └── cover_ui.py
│   └── utils/              # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── ai_models/               # AI模型相关
│   ├── __init__.py
│   ├── ali_model/          # 阿里模型
│   │   ├── __init__.py
│   │   ├── fileHelp.py
│   │   └── video.py
│   └── big_model/          # 大模型
│       ├── __init__.py
│       ├── llm.py
│       └── video.py
├── agents/                 # 智能体相关
│   ├── __init__.py
│   ├── agent.py
│   ├── agent_ui.py
│   ├── agent_v3.py
│   ├── agent_v5.py
│   └── agentv4/
│       ├── __init__.py
│       ├── agent.py
│       └── prompt.md
├── video_processing/        # 视频处理相关
│   ├── __init__.py
│   ├── autocut/            # 自动剪辑
│   │   ├── __init__.py
│   │   ├── auto_cut.py
│   │   ├── auto_cut_v2.py
│   │   ├── auto_cut_v3.py
│   │   ├── auto_cut_v4.py
│   │   └── cut_v5.py
│   └── vector_db/         # 向量数据库
│       ├── __init__.py
│       └── main.py
├── tts/                    # 文本转语音
│   ├── __init__.py
│   ├── cosyvoice/
│   │   ├── __init__.py
│   │   └── tts.py
│   └── minimax/
│       ├── __init__.py
│       └── tts.py
├── text_to_image/          # 文本转图像
│   ├── __init__.py
│   └── main.py
└── tests/                  # 测试文件
    ├── __init__.py
    ├── cosyvoicev3.py
    ├── index_tts2.py
    └── index_tts2_create.py
```

### 2. 保留的根目录文件
```
根目录保留：
├── v1.py
├── v3.py  
├── v4.py
├── v5.py
├── videoCut.py
├── videoToVector.py
├── .env.example
├── .gitignore
├── .python-version
├── AGENTS.md
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
└── start_videoToVector.bat
```

### 3. 保留的目录结构
```
保留原有结构：
├── material/              # 素材资源目录
├── openspec/              # 规范文档目录
├── .trae/                 # IDE配置目录
└── Vector/db/             # 数据库文件
```

### 4. 实施步骤
1. **创建src/目录结构** - 建立新的目录架构
2. **移动Python模块** - 将各个模块按功能分类移动到src/下
3. **更新导入路径** - 修改所有Python文件中的import语句
4. **清理根目录** - 移动不必要的Python文件到src/
5. **验证重构** - 确保所有功能正常工作

### 5. 注意事项
- 需要更新所有Python文件的import语句
- 保持原有的功能逻辑不变
- 确保相对导入和绝对导入的正确性
- 测试所有模块的导入是否正常

这个重构方案将显著改善项目的代码组织结构，使其符合Python最佳实践，同时保持现有功能的完整性。