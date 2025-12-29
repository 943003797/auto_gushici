## ADDED Requirements
### Requirement: 参考音频选择
系统 SHALL 支持用户从预定义的参考音频文件中选择不同的语音样本，以个性化语音合成效果。

#### Scenario: 用户选择参考音频文件
- **WHEN** 用户在TTS界面中选择不同的参考音频文件
- **THEN** 系统 SHALL 使用选定的参考音频进行后续的语音合成

#### Scenario: 参考音频文件列表显示
- **WHEN** 界面加载参考音频选择组件
- **THEN** 系统 SHALL 自动扫描 `material/reference_audio/` 目录并显示所有可用的音频文件

## MODIFIED Requirements
### Requirement: TTS语音生成
系统 SHALL 提供文本转语音功能，支持动态参考音频选择和多种语音生成模式。

#### Scenario: 使用选定参考音频生成TTS
- **WHEN** 用户点击配音或重新生成配音按钮，并已选择参考音频
- **THEN** 系统 SHALL 使用用户选定的参考音频文件调用IndexTTS-2模型生成语音

#### Scenario: 默认参考音频回退
- **WHEN** 用户未选择参考音频或选定的文件不可用
- **THEN** 系统 SHALL 回退到默认的 `material/reference_audio/风吟.wav` 进行语音合成

#### Scenario: 参考音频试听
- **WHEN** 用户在参考音频下拉菜单中选择特定文件
- **THEN** 系统 SHALL 立即播放选定的参考音频文件供用户预览