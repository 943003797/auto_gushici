import os
from videoToText.index import video
from Vector.main import VectorDB
import time

folder_path = r"D:/Material/fragment"
vector_db0 = VectorDB(collection_name="video_0", db_path="./Vector/db/video")
vector_db1 = VectorDB(collection_name="video_1", db_path="./Vector/db/video")
vector_db2 = VectorDB(collection_name="video_2", db_path="./Vector/db/video")
vector_db3 = VectorDB(collection_name="video_3", db_path="./Vector/db/video")
vector_db4 = VectorDB(collection_name="video_4", db_path="./Vector/db/video")
vector_db5 = VectorDB(collection_name="video_5", db_path="./Vector/db/video")
vector_db6 = VectorDB(collection_name="video_6", db_path="./Vector/db/video")
vector_db7 = VectorDB(collection_name="video_7", db_path="./Vector/db/video")
vector_db8 = VectorDB(collection_name="video_8", db_path="./Vector/db/video")
vector_db9 = VectorDB(collection_name="video_9", db_path="./Vector/db/video")
vector_db10 = VectorDB(collection_name="video_10", db_path="./Vector/db/video")
video = video()
i = 1
while True:
    # 从1开始循环到无限
    if i > 99999:
        break
    file_path = os.path.join(folder_path, f"{i}.mp4")
    if not os.path.exists(file_path):
        print(f"文件 {i}.mp4 不存在")
        i += 1
        continue
    # 确定collection索引
    duration = video.get_video_duration(file_path)
    if duration is None:
        duration = 0
    dbindex = int(duration)  # 每1秒一个区间，index从0开始
    if(dbindex < 1):
        continue
    if dbindex > 10:
        dbindex = 0
    print(f"视频 {i}.mp4 时长 {duration} 秒，索引 {dbindex}")
    # 视频内容转换为向量
    tag = video.get_video_tag(file_path)
    if tag is False:
        print(f"文件 {i}.mp4 跳过")
        i += 1
        continue
    print(tag)
    # 调用添加文档方法
    documents = [tag]
    metadatas = [{"fileName": f"{i}.mp4"}]
    vector_db = locals()[f"vector_db{dbindex}"]
    if vector_db.add_documents(texts=documents, metadatas=metadatas):
        print(f"文件 {i}.mp4：{tag} 已嵌入")
    else:
        print(f"文件 {i}.mp4：{tag} 嵌入失败")
    i += 1
