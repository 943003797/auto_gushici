import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from BigModel.video import video
from Vector.main import VectorDB
import time
from typing import Dict, List, Tuple
import sys

# 全局变量：控制线程数
# 可以通过修改这个值来全局控制所有处理的线程数
DEFAULT_MAX_WORKERS = 3


class VideoToVectorProcessor:
    def __init__(self, folder_path: str, max_workers: int = None):
        self.folder_path = folder_path
        # 使用全局变量作为默认线程数，如果没有指定的话
        self.max_workers = max_workers if max_workers is not None else DEFAULT_MAX_WORKERS
        self.vector_db = VectorDB(collection_name="video", db_path="./Vector/db/video")
        self.video_processor = video()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def process_single_video(self, file_index: int) -> Tuple[bool, str]:
        """处理单个视频文件"""
        file_path = os.path.join(self.folder_path, f"{file_index}.mp4")
        
        try:
            if not os.path.exists(file_path):
                return False, f"文件 {file_index}.mp4 不存在"
            
            # 读取视频时长
            duration = self.video_processor.get_video_duration(file_path)
            
            # 视频内容分析
            tag = self.video_processor.get_video_tag(file_path)
            
            # 拼装metadata
            tag["duration"] = duration
            tag["fileName"] = f"{file_index}.mp4"
            
            # 调用添加文档方法
            if self.vector_db.add_documents(texts=[tag["tags"]], metadatas=[tag]):
                self.logger.info(f"文件 {file_index}.mp4 已嵌入")
                return True, f"文件 {file_index}.mp4 处理成功"
            else:
                return False, f"文件 {file_index}.mp4 嵌入失败"
                
        except Exception as e:
            error_msg = f"处理文件 {file_index}.mp4 时发生错误: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def find_video_files(self) -> List[int]:
        """查找所有存在的视频文件"""
        video_files = []
        
        # 查找所有存在的视频文件（不要求连续）
        i = 1
        max_check = 5000  # 设置最大检查数量，避免无限循环
        while i <= max_check:
            file_path = os.path.join(self.folder_path, f"{i}.mp4")
            if os.path.exists(file_path):
                video_files.append(i)
            i += 1
        
        return video_files
    
    def process_all_videos(self) -> None:
        """处理所有视频文件"""
        video_files = self.find_video_files()
        
        if not video_files:
            self.logger.warning(f"在目录 {self.folder_path} 中未找到任何视频文件")
            return
        
        self.logger.info(f"找到 {len(video_files)} 个视频文件，将使用 {self.max_workers} 个线程进行处理")
        
        # 使用线程池处理视频
        successful_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self.process_single_video, file_index): file_index 
                for file_index in video_files
            }
            
            # 收集结果
            for future in as_completed(future_to_index):
                file_index = future_to_index[future]
                try:
                    success, message = future.result()
                    if success:
                        successful_count += 1
                        self.logger.info(f"{message}")
                    else:
                        failed_count += 1
                        self.logger.warning(f"{message}")
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"处理文件 {file_index}.mp4 时发生未捕获异常: {str(e)}")
        
        # 输出统计结果
        self.logger.info(f"处理完成! 成功: {successful_count}, 失败: {failed_count}, 总计: {len(video_files)}")


def main():
    parser = argparse.ArgumentParser(description="多线程视频向量化处理工具")
    parser.add_argument("--folder", "-f", 
                       default=r"D:/Material/fragment", 
                       help="视频文件夹路径 (默认: D:/Material/fragment)")
    # parser.add_argument("--workers", "-w", 
    #                    type=int, 
    #                    default=2, 
    #                    help="线程数 (默认: 2)")
    parser.add_argument("--verbose", "-v", 
                       action="store_true", 
                       help="显示详细日志")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查文件夹是否存在
    if not os.path.exists(args.folder):
        print(f"错误: 文件夹 {args.folder} 不存在")
        sys.exit(1)
    
    # 创建处理器并运行
    processor = VideoToVectorProcessor(args.folder)
    processor.process_all_videos()


if __name__ == "__main__":
    main()
