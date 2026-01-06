import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import uuid

class VectorDB:
    def __init__(self, collection_name: str = "my_collection", db_path: str = "./Vector/db/video_db"):
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
        self._init_openai_client()
    
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
        print(f"正在为 {len(texts)} 个文本生成向量嵌入...")
        
        for text in texts:
            completion = self.openai_client.embeddings.create(
                model="text-embedding-v4",
                input=text
            )
            embedding_vector = completion.data[0].embedding
            embeddings.append(embedding_vector)
        
        print("向量嵌入生成完成")
        return embeddings
    
    def add_documents(self, texts: List[str], ids: Optional[List[str]] = None, 
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
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if len(texts) != len(ids):
            raise ValueError("texts和ids的长度必须一致")
        
        embeddings = self._get_embeddings(texts)
        
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def search(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        搜索相似文档
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            
        Returns:
            搜索结果字典
        """
        query_embedding = self._get_embeddings([query_text])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
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
        
    #     # 搜索相似文档
    #     query = "I like tropical fruits"
    #     results = vector_db.search(query, n_results=2)
        
    #     print(f"\n查询: {query}")
    #     print("搜索结果:")
    #     for i, (doc, distance, meta) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0])):
    #         print(f"  {i+1}. 文档: {doc}")
    #         print(f"     相似度: {1 - distance:.4f}")
    #         print(f"     元数据: {meta}")
    
    # 获取集合信息
    # info = vector_db.get_collection_info()
    # print(f"\n集合信息: {info}")


if __name__ == "__main__":
    # 初始化向量数据库
    vector_db = VectorDB(collection_name="video_10", db_path="./Vector/db/video")
    
    # 添加文档
    # documents = ["2"]
    # metadatas = [{"source": "document1"}]
    # success = vector_db.add_documents(documents, metadatas=metadatas)
    # if success:
    #     print("文档添加成功")


    # # vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video_db")
    # # # vector_db.add_documents(['毛笔'], ['1'])

    results = vector_db.search('铃铛', n_results=5)
    print(results)
