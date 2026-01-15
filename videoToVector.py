import sys, os, argparse, logging, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from BigModel.video import video
from Vector.main import VectorDB
from typing import List, Tuple

# 控制线程数
DEFAULT_MAX_WORKERS = 3

# 源视频目录（需要处理的视频）
SOURCE_VIDEO_FOLDER = r"D:/Material/video_tmp"

# 目标视频目录（处理后移动到此）
DEST_VIDEO_FOLDER = r"D:/Material/video"

# 每个文件夹存放的视频数量
VIDEOS_PER_FOLDER = 2000

class VideoToVectorProcessor:
    def __init__(self, max_workers: int = None):
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
        
        # 确保目标目录存在
        os.makedirs(DEST_VIDEO_FOLDER, exist_ok=True)
        
        # 初始化目标路径计算
        self._next_folder, self._next_file = self._get_next_destination()
    
    def _get_next_destination(self) -> Tuple[int, int]:
        """获取下一个可用的存储路径（文件夹号, 文件号）
        
        Returns:
            Tuple[文件夹号, 文件号]
        """
        try:
            if not os.path.exists(DEST_VIDEO_FOLDER):
                return 1, 1
            
            # 获取所有纯数字命名的文件夹
            folders = []
            for item in os.listdir(DEST_VIDEO_FOLDER):
                folder_path = os.path.join(DEST_VIDEO_FOLDER, item)
                if os.path.isdir(folder_path) and item.isdigit():
                    folders.append(int(item))
            
            if not folders:
                return 1, 1
            
            # 获取最大文件夹名
            max_folder = max(folders)
            max_folder_path = os.path.join(DEST_VIDEO_FOLDER, str(max_folder))
            
            # 获取最大文件夹下的所有 mp4 文件
            files = []
            for item in os.listdir(max_folder_path):
                file_path = os.path.join(max_folder_path, item)
                if os.path.isfile(file_path) and item.endswith('.mp4'):
                    file_name = item[:-4]
                    if file_name.isdigit():
                        files.append(int(file_name))
            
            if not files:
                # 文件夹为空，从该文件夹的1号文件开始
                return max_folder, 1
            
            # 获取最大文件名
            max_file = max(files)
            
            if max_file >= VIDEOS_PER_FOLDER:
                # 当前文件夹已满，使用下一个文件夹
                return max_folder + 1, 1
            else:
                # 当前文件夹未满，使用下一个文件号
                return max_folder, max_file + 1
            
        except Exception as e:
            logging.getLogger().warning(f"计算下一个存储路径失败，使用默认值: {e}")
            return 1, 1
    
    def _get_destination_path(self) -> Tuple[str, str]:
        """计算目标文件夹路径和文件名
        
        Returns:
            Tuple[文件夹路径, 文件名]
            例如: ('D:/Material/video/1', '1.mp4')
        """
        folder_path = os.path.join(DEST_VIDEO_FOLDER, f"{self._next_folder}")
        file_name = f"{self._next_file}.mp4"
        
        return folder_path, file_name
    
    def _move_video(self, source_path: str) -> Tuple[bool, str]:
        """移动视频文件到目标目录
        
        Args:
            source_path: 源文件路径
            
        Returns:
            Tuple[是否成功, 消息]
        """
        try:
            folder_path, file_name = self._get_destination_path()
            
            # 创建目标文件夹
            os.makedirs(folder_path, exist_ok=True)
            
            # 目标完整路径
            dest_path = os.path.join(folder_path, file_name)
            
            # 移动文件
            shutil.move(source_path, dest_path)
            
            # 更新下一个目标路径
            if self._next_file >= VIDEOS_PER_FOLDER:
                self._next_folder += 1
                self._next_file = 1
            else:
                self._next_file += 1
            
            return True, dest_path
            
        except Exception as e:
            return False, f"移动文件失败: {str(e)}"
    
    def process_single_video(self, file_index: int) -> Tuple[bool, str]:
        """处理单个视频文件"""
        file_path = os.path.join(SOURCE_VIDEO_FOLDER, f"{file_index}.mp4")
        
        try:
            if not os.path.exists(file_path):
                return False, f"文件 {file_index}.mp4 不存在"
            
            # 检查视频分辨率是否为1920*1080
            width, height = self.video_processor.get_video_resolution(file_path)
            if width is None or height is None:
                return False, f"文件 {file_index}.mp4 无法获取分辨率"
            
            if width != 1920 or height != 1080:
                self.logger.info(f"文件 {file_index}.mp4 分辨率为 {width}*{height}，跳过（仅处理1920*1080视频）")
                return False, f"分辨率不符: {width}*{height}"
            
            # 读取视频时长
            duration = self.video_processor.get_video_duration(file_path)
            
            # 视频内容分析
            tag = self.video_processor.get_video_info_tag(file_path)
            
            # 拼装metadata
            tag["duration"] = str(duration)
            print(f"视频时长: {duration} 秒")
            # 计算目标路径
            folder_path, file_name = self._get_destination_path()
            tag["fileName"] = f"{os.path.basename(folder_path)}/{file_name}"
            
            # 调用添加文档方法
            if self.vector_db.add_documents(fileNamePath=[file_path], metadatas=[tag]):
                # 移动视频文件到目标目录
                move_success, move_message = self._move_video(file_path)
                if move_success:
                    self.logger.info(f"文件 {file_index}.mp4 已嵌入并移动到 {move_message}")
                    return True, f"文件 {file_index}.mp4 处理成功"
                else:
                    self.logger.warning(f"文件 {file_index}.mp4 已嵌入但移动失败: {move_message}")
                    return True, f"文件 {file_index}.mp4 处理成功（移动失败）"
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
            file_path = os.path.join(SOURCE_VIDEO_FOLDER, f"{i}.mp4")
            if os.path.exists(file_path):
                video_files.append(i)
            i += 1
        
        return video_files
    
    def process_all_videos(self) -> None:
        """处理所有视频文件"""
        video_files = self.find_video_files()
        
        if not video_files:
            self.logger.warning(f"在目录 {SOURCE_VIDEO_FOLDER} 中未找到任何视频文件")
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
                       default=SOURCE_VIDEO_FOLDER, 
                       help=f"视频文件夹路径 (默认: {SOURCE_VIDEO_FOLDER})")
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
    processor = VideoToVectorProcessor()
    processor.process_all_videos()


if __name__ == "__main__":
    main()
