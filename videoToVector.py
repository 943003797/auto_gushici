import os
from videoToText.index import video
from Vector.main import VectorDB

folder_path = r"D:/Material/split"
vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video_db")
video = video()
i = 0
while True:
    # 从1开始循环到无限
    i += 1
    file_path = os.path.join(folder_path, f"{i}.mp4")
    print(file_path)
    if not os.path.exists(file_path):
        print(f"文件 {i}.mp4 不存在")
        break
    tag = video.get_video_tag(file_path)
    print(tag)
    # 调用添加文档方法
    documents = [tag]
    metadatas = [{"fileName": f"{i}.mp4"}]
    if vector_db.add_documents(texts=documents, metadatas=metadatas):
        print(f"文件 {i}.mp4：{tag} 已嵌入")
    else:
        print(f"文件 {i}.mp4：{tag} 嵌入失败")
