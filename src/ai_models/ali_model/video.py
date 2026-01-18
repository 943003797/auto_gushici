import dashscope, os, requests
from http import HTTPStatus
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

class video_embedding:
    def __init__(self, model="tongyi-embedding-vision-plus"):
        self.model = model
    
    def get_embedding_video(self, local_file: str):
        file_uploader = FileUploader(model_name=self.model)
        file_url = file_uploader.upload(local_file)
        input = [{'video': file_url}]
        # 调用模型接口
        dashscope.api_key = os.getenv("ALI_KEY")
        resp = dashscope.MultiModalEmbedding.call(
            model=self.model,
            input=input
        )
        if resp.status_code == HTTPStatus.OK:
            result = {
                "status_code": resp.status_code,
                "request_id": getattr(resp, "request_id", ""),
                "code": getattr(resp, "code", ""),
                "message": getattr(resp, "message", ""),
                "output": resp.output,
                "usage": resp.usage
            }
            print('get embedding success')
            
            # 取出embedding数据
            embeddings = resp.output['embeddings']
            first_embedding = embeddings[0]
            embedding = first_embedding['embedding']
            return embedding
        return Fasle

    def get_embedding_text(self, text: str):
        input = [{'text': text}]
        # 调用模型接口
        dashscope.api_key = os.getenv("ALI_KEY")
        resp = dashscope.MultiModalEmbedding.call(
            model=self.model,
            input=input
        )
        if resp.status_code == HTTPStatus.OK:
            result = {
                "status_code": resp.status_code,
                "request_id": getattr(resp, "request_id", ""),
                "code": getattr(resp, "code", ""),
                "message": getattr(resp, "message", ""),
                "output": resp.output,
                "usage": resp.usage
            }
            
            # 取出embedding数据
            embeddings = resp.output['embeddings']
            first_embedding = embeddings[0]
            embedding = first_embedding['embedding']
            return embedding
        return Fasle

class FileUploader:
    def __init__(self, model_name: str):
        """
        初始化文件上传器
        
        参数:
            model_name (str): 指定文件将要用于哪个模型，如 qwen-vl-plus
        """
        self.model_name = model_name
        self.api_key = os.getenv("ALI_KEY")
        if not self.api_key:
            raise Exception("请设置 ALI_KEY 环境变量")
    
    def upload(self, file_path: str) -> str:
        """
        上传本地文件到OSS，并返回临时URL
        
        参数:
            file_path (str): 待上传的本地文件路径（图片、视频、音频等）
            
        返回:
            str: OSS文件链接（oss://开头的临时URL）
        """
        policy_data = self._get_upload_policy()
        oss_url = self._upload_file(policy_data, file_path)
        
        return oss_url
    
    def _get_upload_policy(self) -> dict:
        """获取文件上传凭证"""
        url = "https://dashscope.aliyuncs.com/api/v1/uploads"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        params = {
            "action": "getPolicy",
            "model": self.model_name
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get upload policy: {response.text}")
        
        return response.json()['data']
    
    def _upload_file(self, policy_data: dict, file_path: str) -> str:
        """将文件上传到临时存储OSS"""
        # 处理Windows路径
        import os
        original_path = file_path
        file_path = os.path.join(os.path.dirname(original_path), os.path.basename(original_path))
        file_name = Path(file_path).name
        key = f"{policy_data['upload_dir']}/{file_name}"
        with open(original_path, 'rb') as file:
            files = {
                'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
                'Signature': (None, policy_data['signature']),
                'policy': (None, policy_data['policy']),
                'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
                'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
                'key': (None, key),
                'success_action_status': (None, '200'),
                'file': (file_name, file)
            }
            response = requests.post(policy_data['upload_host'], files=files)
            if response.status_code != 200:
                raise Exception(f"Failed to upload file: {response.text}")
        
        return f"oss://{key}"

if __name__ == "__main__":
    ve = video_embedding()
    embedding = ve.get_embedding_text(text="你好")
    print(embedding)
