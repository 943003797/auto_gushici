from src.ai_models.ali_model.fileHelp import FileUploader
import dashscope
import os
import json
import requests
import os
from time import sleep

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
# 若没有配置环境变量，请用百炼API Key将下行替换为：dashscope.api_key = "sk-xxx"
dashscope.api_key = os.getenv("ALI_KEY")


def new_task(file_url: str) -> str:
    url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription'
    headers = {
        "Authorization": f"Bearer {os.getenv('ALI_KEY')}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
        "X-DashScope-OssResourceResolve": "enable"
    }
    file_uploader = FileUploader(model_name='fun-asr')
    file_url = file_uploader.upload('testAudio.mp3')
    payload = {
        "model": "fun-asr",
        "input": {
            "file_urls": [file_url]
        },
        "parameters": {
            "channel_id": [0]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to create task: {response.text}")
    return response.json()['output']['task_id']

def get_transcription(task_id: str) -> dict:
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('ALI_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get task status: {response.text}")
    if response.json()['output']['task_status'] != 'SUCCEEDED':
        sleep(2)
        return get_transcription(task_id)
    transcription = requests.get(response.json()['output']['results'][0]['transcription_url'])
    return transcription.json()

def get_transcription_by_audio(file_path: str) -> dict:
    """
    从音频文件中获取转录结果
    
    参数:
        file_path (str): 音频文件的路径
        
    返回:
        dict: 包含转录结果的字典
    """
    new_task_id = new_task(file_path)
    return get_transcription(new_task_id)
