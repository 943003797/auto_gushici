import os, json
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from src.ai_models.ali_model.video import video_embedding
import uuid

class VectorDB:
    def __init__(self, collection_name: str = "video", db_path: str = "./Vector/db/video"):
        """
        初始化向量数据库
        
        Args:
            collection_name: ChromaDB集合名称
            db_path: 数据库文件存储路径
        """
        load_dotenv()
        
        self.collection_name = collection_name
        self.db_path = db_path
        self.client = None
        self.collection = None
        self.openai_client = None
        
        self._init_chromadb()
        # self._init_openai_client()
    
    def _init_chromadb(self):
        """初始化ChromaDB客户端和集合"""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"使用已存在的集合: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(name=self.collection_name)
            print(f"创建新集合: {self.collection_name}")
    
    def _init_openai_client(self):
        """初始化OpenAI客户端（阿里云兼容模式）"""
        api_key = os.getenv("ALI_KEY")
        if not api_key:
            raise ValueError("未找到ALI_KEY环境变量，请确保已正确设置阿里云API Key")
            print("获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key")
        
        self.openai_client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        print("阿里云text-embedding-v4模型客户端初始化完成")
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        将文本转换为向量嵌入
        
        Args:
            texts: 要转换的文本列表
            
        Returns:
            向量嵌入列表
        """
        embeddings = []
        print(f"正在为 {texts} 生成向量嵌入...")
        
        for text in texts:
            ve = video_embedding()
            embedding_vector = ve.get_embedding_text(text=text) 
            embeddings.append(embedding_vector)
        
        print("向量嵌入生成完成")
        return embeddings
    
    def add_documents(self, fileNamePath: List[str], ids: Optional[List[str]] = None, 
                     metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        添加文档到向量数据库
        
        Args:
            texts: 文档文本列表
            ids: 文档ID列表（可选，默认自动生成）
            metadatas: 文档元数据列表（可选）
            
        Returns:
            添加是否成功
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in fileNamePath]
        if len(fileNamePath) != len(ids):
            raise ValueError("texts和ids的长度必须一致")
        ve = video_embedding()
        embedding = ve.get_embedding_video(local_file=fileNamePath[0])
        try:
            self.collection.add(
                ids=ids,
                embeddings=embedding,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def search(self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        搜索相似文档
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            where: 过滤条件（可选）
            
        Returns:
            搜索结果字典
        """
        query_embedding = self._get_embeddings([query_text])[0]
        print(f"匹配视频: {query_text}")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            集合信息字典
        """
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "path": self.db_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_collection(self):
        """删除当前集合"""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"集合 {self.collection_name} 已删除")
            # 重新初始化集合
            self._init_chromadb()
        except Exception as e:
            print(f"删除集合失败: {e}")


    # # 使用示例
    def test():
        # 初始化向量数据库
        vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video_db")
        
        # 添加文档
        documents = ["This is a document about pineapple"]
        metadatas = [{"source": "document1"}]
        success = vector_db.add_documents(documents, metadatas=metadatas)
        if success:
            print("文档添加成功")

if __name__ == "__main__":
    # 初始化向量数据库
    vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video")
    
    # 添加文档
    # documents = ["2"]
    # metadatas = [{"source": "document1"}]
    # success = vector_db.add_documents(documents, metadatas=metadatas)
    # if success:
    #     print("文档添加成功")


    # vector_db.add_documents(['毛笔'], ['1'], metadatas=[{"emotion": "平静"}])

    results = vector_db.search(query_text='它被公认为宋词里的万古愁心之祖', n_results=1, where={"duration": "5"})
    # results = json.loads(results)  
    print(results)
    # print(results["metadatas"][0][0]["fileName"])
