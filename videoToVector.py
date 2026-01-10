import os
from videoToText.index import video
from Vector.main import VectorDB
import time

folder_path = r"D:/Material/fragment"
vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video")
video = video()
i = 99999
while True:
    if i > 1:
        break
    file_path = os.path.join(folder_path, f"{i}.mp4")
    if not os.path.exists(file_path):
        print(f"文件 {i}.mp4 不存在")
        i += 1
        continue
    # 读取视频时长
    duration = video.get_video_duration(file_path)
    # 视频内容分析
    tag = video.get_video_tag(file_path)
    # 拼装metadata
    tag["duration"] = duration
    tag["fileName"] = f"{i}.mp4"
    # 调用添加文档方法
    if vector_db.add_documents(texts=[tag["tags"]], metadatas=[tag]):
        print(f"文件 {i}.mp4 已嵌入 \n{tag}")
    else:
        print(f"文件 {i}.mp4 嵌入失败")
    i += 99999
