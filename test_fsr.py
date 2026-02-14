from src.ai_models.ali_model.audio import get_transcription_by_audio
import json

result = get_transcription_by_audio('江雪柳宗元.MP3')
with open('1.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(result)