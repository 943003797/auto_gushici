import dashscope, os, json
from http import HTTPStatus
from AliModel.fileHelp import FileUploader


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

if __name__ == "__main__":
    ve = video_embedding()
    embedding = ve.get_embedding_text(text="你好")
    print(embedding)
