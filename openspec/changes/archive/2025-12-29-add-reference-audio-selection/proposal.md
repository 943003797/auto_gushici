# Change: 为v3重新生成语音功能增加参考音频选择

## Why
当前v3语音生成功能在 `generate_audio_indextts2` 函数中硬编码使用 `material/reference_audio/风吟.wav` 作为参考音频。用户希望能够选择不同的参考音频文件，以获得更个性化的语音合成效果。

## What Changes
- 为v3界面添加参考音频选择组件
- 修改TTS生成函数支持动态参考音频选择
- 在语音重新生成功能中集成参考音频选择
- 更新UI界面以显示可选的参考音频文件列表

## Impact
- Affected specs: TTS语音生成功能
- Affected code: 
  - `agent/agent_v3.py` - TTS生成函数
  - `v3.py` - 主界面文件
- 参考音频目录: `material/reference_audio/` 下的4个文件