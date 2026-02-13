#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频切割系统 v3.0
采用全新架构设计的智能视频切割工具

主要特性：
- 模块化架构设计
- 配置驱动的参数管理
- 统一的日志系统
- 智能场景检测
- 自动短片段处理
- 倍速调节功能
"""

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode
from pathlib import Path
import os
import glob
import subprocess
import sys
import logging
import json
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Scene:
    """场景数据类"""
    start_time: FrameTimecode
    end_time: FrameTimecode
    duration: float
    start_seconds: float
    end_seconds: float
    
    @classmethod
    def from_tuple(cls, scene_tuple: Tuple[FrameTimecode, FrameTimecode]):
        start_time, end_time = scene_tuple
        duration = (end_time.get_frames() - start_time.get_frames()) / start_time.framerate
        return cls(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            start_seconds=start_time.get_seconds(),
            end_seconds=end_time.get_seconds()
        )


@dataclass
class ProcessingResult:
    """处理结果数据类"""
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    processing_type: str = "normal"
    actual_duration: Optional[float] = None


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "video_cut_config.json"):
        self.config_file = config_file
        self.default_config = {
            "video_paths": {
                "material_dir": "D:/Material/new_video",
                "origin_dir": "D:/Material/origin", 
                "output_dir": "D:/Material/video_cuted"
            },
            "scene_detection": {
                "threshold": 45,
                "adjust_frames": 3
            },
            "video_processing": {
                "min_duration": 3.0,  # 短片段合并阈值
                "max_duration": 60.0,  # 长场景拆分阈值
                "split_duration": 30.0,  # 拆分片段长度
                "min_split_duration": 10.0,  # 最小拆分长度
                "discard_threshold": 1.0,  # 丢弃小于此长度的片段
                "speed_adjust_range": [1.0, 4.0],  # 倍速调节范围
                "speed_target_duration": 4.5  # 倍速调节目标长度
            },
            "ffmpeg": {
                "video_codec": "libx264",
                "preset": "ultrafast",
                "crf": 18,
                "pixel_format": "yuv420p",
                "log_level": "error"
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置
                    self._merge_config(self.default_config, loaded_config)
                    return self.default_config
        except Exception as e:
            logging.warning(f"加载配置文件失败，使用默认配置: {e}")
        
        # 保存默认配置
        self.save_config(self.default_config)
        return self.default_config
    
    def save_config(self, config: dict):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def _merge_config(self, default: dict, loaded: dict):
        """递归合并配置"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def get(self, path: str, default=None):
        """获取配置项"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, path: str, value):
        """设置配置项"""
        keys = path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value


class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = "VideoCut", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class SceneDetector:
    """场景检测器"""
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
    
    def detect_scenes(self, video_path: str) -> List[Scene]:
        """检测视频场景"""
        try:
            threshold = self.config.get('scene_detection.threshold', 45)
            self.logger.info(f"开始检测场景，阈值: {threshold}")
            
            video = open_video(video_path)
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=threshold))
            
            scene_manager.detect_scenes(video, show_progress=True)
            scene_list = scene_manager.get_scene_list()
            
            scenes = [Scene.from_tuple(scene) for scene in scene_list]
            self.logger.info(f"检测到 {len(scenes)} 个场景")
            
            return scenes
        except Exception as e:
            self.logger.error(f"场景检测失败: {e}")
            raise
    
    def adjust_boundaries(self, scenes: List[Scene], video_path: str) -> List[Scene]:
        """调整场景边界"""
        try:
            adjust_frames = self.config.get('scene_detection.adjust_frames', 3)
            
            video = open_video(video_path)
            framerate = video.frame_rate
            adjusted_scenes = []
            
            for i, scene in enumerate(scenes):
                start_frame = scene.start_time.frame_num + adjust_frames
                end_frame = scene.end_time.frame_num - adjust_frames
                
                # 确保调整后的边界合理
                if i > 0 and adjusted_scenes:
                    prev_end = adjusted_scenes[-1].end_time.frame_num
                    if start_frame <= prev_end:
                        start_frame = prev_end + 1
                
                if end_frame <= start_frame:
                    continue
                
                # 创建调整后的场景
                adjusted_start = FrameTimecode(start_frame, fps=framerate)
                adjusted_end = FrameTimecode(end_frame, fps=framerate)
                
                adjusted_scene = Scene(
                    start_time=adjusted_start,
                    end_time=adjusted_end,
                    duration=(end_frame - start_frame) / framerate,
                    start_seconds=start_frame / framerate,
                    end_seconds=end_frame / framerate
                )
                
                adjusted_scenes.append(adjusted_scene)
            
            self.logger.info(f"边界调整完成，调整帧数: {adjust_frames}")
            return adjusted_scenes
            
        except Exception as e:
            self.logger.error(f"边界调整失败: {e}")
            raise


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
    
    def split_long_scenes(self, scenes: List[Scene]) -> List[Scene]:
        """拆分长场景"""
        max_duration = self.config.get('video_processing.max_duration', 60.0)
        split_duration = self.config.get('video_processing.split_duration', 30.0)
        min_split_duration = self.config.get('video_processing.min_split_duration', 10.0)
        
        split_scenes = []
        
        for scene in scenes:
            if scene.duration <= max_duration:
                split_scenes.append(scene)
            else:
                self.logger.info(f"长场景拆分: {scene.duration:.2f}s")
                framerate = scene.start_time.framerate
                current_start = scene.start_seconds
                end_time = scene.end_seconds
                
                while current_start + min_split_duration <= end_time:
                    split_end = min(current_start + split_duration, end_time)
                    remaining = end_time - split_end
                    
                    if remaining < min_split_duration and split_end < end_time:
                        break
                    
                    start_frame = FrameTimecode(int(current_start * framerate), fps=framerate)
                    end_frame = FrameTimecode(int(split_end * framerate), fps=framerate)
                    
                    split_scene = Scene(
                        start_time=start_frame,
                        end_time=end_frame,
                        duration=split_end - current_start,
                        start_seconds=current_start,
                        end_seconds=split_end
                    )
                    
                    split_scenes.append(split_scene)
                    current_start = split_end
        
        return split_scenes
    
    def process_short_scenes(self, scenes: List[Scene]) -> Tuple[List[Scene], List[Scene]]:
        """处理短片段：丢弃或倍速调节"""
        discard_threshold = self.config.get('video_processing.discard_threshold', 1.0)
        speed_range = self.config.get('video_processing.speed_adjust_range', [1.0, 4.0])
        target_duration = self.config.get('video_processing.speed_target_duration', 4.5)
        
        processed_scenes = []
        discarded_scenes = []
        
        for scene in scenes:
            if scene.duration < discard_threshold:
                self.logger.info(f"丢弃短片段: {scene.duration:.2f}s < {discard_threshold}s")
                discarded_scenes.append(scene)
            elif speed_range[0] <= scene.duration < speed_range[1]:
                self.logger.info(f"倍速调节片段: {scene.duration:.2f}s → {target_duration}s")
                # 标记为需要倍速调节的场景
                scene.speed_adjusted = True
                scene.target_duration = target_duration
                processed_scenes.append(scene)
            else:
                processed_scenes.append(scene)
        
        return processed_scenes, discarded_scenes


class VideoCutter:
    """视频切割器"""
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
    
    def cut_scene(self, video_path: str, scene: Scene, output_path: Path) -> ProcessingResult:
        """切割单个场景"""
        try:
            if hasattr(scene, 'speed_adjusted') and scene.speed_adjusted:
                return self._cut_with_speed_adjustment(video_path, scene, output_path)
            else:
                return self._cut_normal_scene(video_path, scene, output_path)
                
        except Exception as e:
            self.logger.error(f"场景切割失败: {e}")
            return ProcessingResult(success=False, error_message=str(e))
    
    def _cut_normal_scene(self, video_path: str, scene: Scene, output_path: Path) -> ProcessingResult:
        """正常切割场景"""
        cmd = self._build_ffmpeg_command(
            video_path, scene.start_seconds, scene.duration, output_path, speed_factor=None
        )
        
        return self._execute_ffmpeg(cmd)
    
    def _cut_with_speed_adjustment(self, video_path: str, scene: Scene, output_path: Path) -> ProcessingResult:
        """带倍速调节的切割"""
        speed_factor = scene.target_duration / scene.duration
        
        cmd = self._build_ffmpeg_command(
            video_path, scene.start_seconds, scene.duration, output_path, speed_factor=speed_factor
        )
        
        return self._execute_ffmpeg(cmd)
    
    def _build_ffmpeg_command(self, video_path: str, start_time: float, duration: float, 
                            output_path: Path, speed_factor: Optional[float] = None) -> List[str]:
        """构建FFmpeg命令"""
        video_codec = self.config.get('ffmpeg.video_codec', 'libx264')
        preset = self.config.get('ffmpeg.preset', 'ultrafast')
        crf = self.config.get('ffmpeg.crf', 18)
        pixel_format = self.config.get('ffmpeg.pixel_format', 'yuv420p')
        log_level = self.config.get('ffmpeg.log_level', 'error')
        
        # 构建基本命令
        cmd = ['ffmpeg', '-i', video_path, '-loglevel', log_level]
        cmd.extend(['-ss', str(start_time), '-t', str(duration)])
        
        # 添加倍速滤镜（在编码参数之前）
        if speed_factor:
            cmd.extend(['-vf', f'setpts={speed_factor}*PTS'])
        
        # 添加视频编码参数
        cmd.extend(['-c:v', video_codec, '-preset', preset, '-crf', str(crf), '-pix_fmt', pixel_format])
        cmd.extend(['-an', '-avoid_negative_ts', 'make_zero', '-y', str(output_path)])
        
        return cmd
    
    def _execute_ffmpeg(self, cmd: List[str]) -> ProcessingResult:
        """执行FFmpeg命令"""
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            return ProcessingResult(success=True, processing_type="normal")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            return ProcessingResult(success=False, error_message=error_msg)
        except Exception as e:
            return ProcessingResult(success=False, error_message=str(e))


class MainController:
    """主控制器"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        self.scene_detector = SceneDetector(self.config, self.logger)
        self.video_processor = VideoProcessor(self.config, self.logger)
        self.video_cutter = VideoCutter(self.config, self.logger)
        
        self.scene_counter = self._get_initial_scene_counter()
    
    def _get_initial_scene_counter(self) -> int:
        """获取初始场景计数器"""
        output_dir = Path(self.config.get('video_paths.output_dir'))
        max_num = 0
        
        if output_dir.exists():
            for file in output_dir.glob('*.mp4'):
                try:
                    num = int(file.stem)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        
        return max_num + 1
    
    def process_videos(self):
        """处理所有视频"""
        material_dir = self.config.get('video_paths.material_dir')
        origin_dir = self.config.get('video_paths.origin_dir')
        
        # 获取所有MP4文件
        mp4_files = glob.glob(os.path.join(material_dir, '*.mp4'))
        
        if not mp4_files:
            self.logger.error(f"在 {material_dir} 目录中没有找到MP4文件")
            return
        
        self.logger.info(f"找到 {len(mp4_files)} 个MP4文件")
        
        # 创建目录
        self._create_directories()
        
        # 处理每个视频文件
        for video_path in mp4_files:
            self._process_single_video(video_path, origin_dir)
    
    def _process_single_video(self, video_path: str, origin_dir: str):
        """处理单个视频文件"""
        self.logger.info(f"开始处理: {video_path}")
        
        try:
            # 1. 场景检测
            scenes = self.scene_detector.detect_scenes(video_path)
            
            # 2. 边界调整
            scenes = self.scene_detector.adjust_boundaries(scenes, video_path)
            
            # 3. 长场景拆分
            scenes = self.video_processor.split_long_scenes(scenes)
            
            # 4. 短片段处理
            scenes, discarded = self.video_processor.process_short_scenes(scenes)
            
            # 5. 切割视频
            self._cut_scenes(video_path, scenes, discarded)
            
            # 6. 移动原视频
            self._move_original_video(video_path, origin_dir)
            
        except Exception as e:
            self.logger.error(f"视频处理失败: {e}")
    
    def _cut_scenes(self, video_path: str, scenes: List[Scene], discarded: List[Scene]):
        """切割场景"""
        output_dir = Path(self.config.get('video_paths.output_dir'))
        
        # 统计信息
        total_scenes = len(scenes) + len(discarded)
        processed_count = 0
        discarded_count = len(discarded)
        speed_adjusted_count = sum(1 for s in scenes if hasattr(s, 'speed_adjusted'))
        
        self.logger.info(f"开始处理 {total_scenes} 个场景...")
        
        for i, scene in enumerate(scenes):
            output_filename = f"{self.scene_counter}.mp4"
            output_path = output_dir / output_filename
            
            self.logger.info(f"处理场景 {i+1}/{len(scenes)}: {output_filename} ({scene.duration:.2f}s)")
            
            result = self.video_cutter.cut_scene(video_path, scene, output_path)
            
            if result.success:
                self.logger.info(f"✓ {output_filename} 处理成功")
                processed_count += 1
                self.scene_counter += 1
            else:
                self.logger.error(f"✗ {output_filename} 处理失败: {result.error_message}")
        
        # 输出统计信息
        self.logger.info(f"处理完成: 成功 {processed_count} 个，丢弃 {discarded_count} 个")
        if speed_adjusted_count > 0:
            self.logger.info(f"倍速调节: {speed_adjusted_count} 个")
    
    def _create_directories(self):
        """创建必要的目录"""
        output_dir = Path(self.config.get('video_paths.output_dir'))
        origin_dir = Path(self.config.get('video_paths.origin_dir'))
        
        output_dir.mkdir(parents=True, exist_ok=True)
        origin_dir.mkdir(parents=True, exist_ok=True)
    
    def _move_original_video(self, video_path: str, origin_dir: str):
        """移动原视频到origin目录"""
        try:
            origin_dir = Path(origin_dir)
            video_filename = Path(video_path).name
            origin_video_path = origin_dir / video_filename
            
            # 处理重名文件
            counter = 1
            while origin_video_path.exists():
                stem = Path(video_path).stem
                suffix = Path(video_path).suffix
                origin_video_path = origin_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            os.rename(video_path, origin_video_path)
            self.logger.info(f"原视频已移动到: {origin_video_path}")
            
        except Exception as e:
            self.logger.error(f"移动原视频失败: {e}")


def main():
    """主函数"""
    try:
        controller = MainController()
        controller.process_videos()
        controller.logger.info("所有视频处理完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()