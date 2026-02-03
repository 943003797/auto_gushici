import os, dashscope
from http import HTTPStatus
from dotenv import load_dotenv

load_dotenv()

def v5_reRank(query: str, documents: list):
    docs = []
    reRankList = []
    for doc in documents:
        docs.append(doc["content"])
    rank_results = text_rerank(query, docs)
    for result in rank_results:
        reRankList.append(documents[result])
    return reRankList

def text_rerank(query: str, documents: list):
    dashscope.api_key = os.getenv("ALI_KEY")
    resp = dashscope.TextReRank.call(
        model="qwen3-rerank",
        query=query,
        documents=documents,
        top_n=len(documents),
        return_documents=True,
        instruct="Given a web search query, retrieve relevant passages that answer the query."
    )
    if resp.status_code == HTTPStatus.OK:
        return extract_indices_from_response(resp)
    else:
        print(resp)
        return None

def extract_indices_from_response(response):
    """从API响应中提取index值"""
    if response and hasattr(response, 'output') and response.output:
        indices = []
        for result in response.output.results:
            indices.append(result.index)
        return indices
    return []


if __name__ == '__main__':
    query="什么是文本排序模型"
    documents=[
        "文本排序模型广泛用于搜索引擎和推荐系统中，它们根据文本相关性对候选文本进行排序",
        "量子计算是计算科学的一个前沿领域",
        "预训练语言模型的发展给文本排序模型带来了新的进展"
    ]
    
    # 获取API响应
    response = text_rerank(query, documents)
    print(response)
    
    # if response:
    #     # 提取index值
    #     indices = extract_indices_from_response(response)
    #     print(indices)