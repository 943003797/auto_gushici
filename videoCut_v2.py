from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg, is_ffmpeg_available
from scenedetect.frame_timecode import FrameTimecode
from pathlib import Path
import os
import glob
import subprocess
import locale
import sys

material_dir = 'D:/Material/new_video'
material_origin_dir = 'D:/Material/origin'
# 设置编码
if sys.platform.startswith('win'):
    # Windows系统编码设置
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def split_video_into_scenes(video_path, threshold=45):
    # Open our video, create a scene manager, and add a detector.
    # 提高阈值以只检测明显的硬切换转场
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    scene_list = scene_manager.get_scene_list()
    return scene_list

def adjust_scene_boundaries(scene_list, video_path, adjust_frames=2):
    """
    调整场景边界，排除可能的边界模糊帧
    adjust_frames: 向前后调整的帧数
    """
    adjusted_scenes = []
    
    # 获取视频的帧率
    video = open_video(video_path)
    framerate = video.frame_rate
    
    for i, scene in enumerate(scene_list):
        start_frame = scene[0].frame_num + adjust_frames
        end_frame = scene[1].frame_num - adjust_frames
        
        # 确保调整后的边界合理
        if i > 0:
            # 确保不与前一个场景重叠
            prev_end = adjusted_scenes[-1][1].frame_num
            if start_frame <= prev_end:
                start_frame = prev_end + 1
                
        # 确保结束帧在开始帧之后
        if end_frame <= start_frame:
            continue
            
        # 创建调整后的场景对象
        adjusted_start = FrameTimecode(start_frame, fps=framerate)
        adjusted_end = FrameTimecode(end_frame, fps=framerate)
        
        adjusted_scenes.append((adjusted_start, adjusted_end))
    
    return adjusted_scenes

def simple_video_cut(video_path, scene, output_path, adjust_frames=0):
    """
    简单的视频切割功能，只根据场景切换进行拆分
    只保留视频流，丢弃音频流
    """
    # 计算精确的切割时间点
    start_time = scene[0].get_seconds() + adjust_frames / scene[0].framerate
    end_time = scene[1].get_seconds() - adjust_frames / scene[1].framerate
    duration = end_time - start_time
    print(f"start_time：{start_time}")
    print(f"end_time：{end_time}")
    print(f"duration：{duration}")
    
    # 使用ffmpeg进行切割，只保留视频
    cmd = [
        'ffmpeg', '-i', video_path,
        '-loglevel', 'error',   # 只显示错误
        '-ss', str(start_time),  # 开始时间
        '-t', str(duration),     # 持续时间
        '-c:v', 'libx264',      # 视频重新编码，确保画面完整性
        '-preset', 'ultrafast', # 最快编码预设，保持原始质量
        '-crf', '18',          # 接近无损的质量设置
        '-pix_fmt', 'yuv420p',  # 像素格式：确保兼容性
        '-an',                 # 丢弃音频流
        '-avoid_negative_ts', 'make_zero',
        '-y',                   # 覆盖输出文件
        str(output_path)
    ]
    
    try:
        # 执行ffmpeg命令
        result = subprocess.run(cmd, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        # 输出错误信息
        if e.stderr:
            try:
                error_msg = e.stderr.decode('utf-8', errors='ignore')
                print(f"FFmpeg错误: {error_msg}")
            except:
                print("FFmpeg执行失败")
        else:
            print("FFmpeg执行失败")
        return False, str(e)
    except Exception as e:
        print(f"执行异常: {str(e)}")
        return False, f"执行异常: {str(e)}"



# 检查是否可用ffmpeg
if not is_ffmpeg_available():
    print("警告: 未找到ffmpeg，请确保ffmpeg已安装并添加到PATH中")
    exit(1)

# 获取D:/Material目录下所有.mp4文件
mp4_files = glob.glob(os.path.join(material_dir, '*.mp4'))

print(f"找到 {len(mp4_files)} 个MP4文件: {mp4_files}")

# 检查是否找到任何MP4文件
if not mp4_files:
    print("在 D:/Material/ 目录中没有找到任何.mp4文件")
    exit(1)
output_dir = Path(f"D:/Material/video_cuted/")
# 读取 output_dir 中数字最大的文件名
max_num = 0
if output_dir.exists():
    for file in output_dir.glob('*.mp4'):
        try:
            num = int(file.stem)
            if num > max_num:
                max_num = num
        except ValueError:
            pass
# 初始化全局场景计数器
global_scene_counter =  max_num + 1

# Process each video file
for video_path in mp4_files:
    print(f"\n正在处理: {video_path}")
    
    # 分析视频并获取场景列表
    scene_list = split_video_into_scenes(video_path)
    
    # 调整场景边界以避免边界模糊
    adjusted_scene_list = adjust_scene_boundaries(scene_list, video_path, adjust_frames=3)
    
    # 显示所有检测到的硬切换场景
    print(f"检测到 {len(adjusted_scene_list)} 个硬切换场景:")
    for i, scene in enumerate(adjusted_scene_list):
        start_time = scene[0].get_timecode()
        end_time = scene[1].get_timecode()
        duration = (scene[1].get_frames() - scene[0].get_frames()) / scene[0].framerate
        print(f"  Scene {i+1}: {start_time} - {end_time} ({duration:.1f}s)")

    def split_long_scenes(scenes, max_duration=60, split_duration=30, min_split_duration=10):
        """
        将超过max_duration秒的场景按split_duration秒拆分
        小于min_split_duration的片段将被丢弃
        保留所有硬切换场景，只对过长场景进行拆分
        """
        split_scenes = []
        
        for i, scene in enumerate(scenes):
            start_time_seconds = scene[0].get_frames() / scene[0].framerate
            end_time_seconds = scene[1].get_frames() / scene[1].framerate
            duration = end_time_seconds - start_time_seconds
            
            if duration <= max_duration:
                # 长度合适，直接保留
                split_scenes.append(scene)
            else:
                # 长度超过限制，需要拆分
                print(f"    场景 {i+1} 时长 {duration:.2f}s，将拆分为{15}秒片段")
                current_start = start_time_seconds
                framerate = scene[0].framerate
                split_count = 0
                
                while current_start + min_split_duration <= end_time_seconds:
                    # 计算当前片段的结束时间（不超过split_duration）
                    split_end = min(current_start + split_duration, end_time_seconds)
                    
                    # 如果剩余长度小于最小长度，停止拆分
                    remaining_length = end_time_seconds - split_end
                    if remaining_length < min_split_duration and split_end < end_time_seconds:
                        print(f"    剩余长度 {remaining_length:.2f}s < 最小长度，停止拆分")
                        break
                    
                    # 创建拆分后的场景
                    start_frame = FrameTimecode(int(current_start * framerate), fps=framerate)
                    end_frame = FrameTimecode(int(split_end * framerate), fps=framerate)
                    
                    split_count += 1
                    print(f"    分段 {split_count}: {current_start:.2f}s - {split_end:.2f}s ({split_end-current_start:.2f}s)")
                    
                    split_scenes.append((start_frame, end_frame))
                    
                    # 更新下一个片段的开始时间
                    current_start = split_end
                    
                    # 如果已经到达视频末尾，停止
                    if current_start >= end_time_seconds:
                        break
        
        return split_scenes

    def merge_short_scenes(scenes, min_duration=3):
        """
        将时长小于min_duration秒的短片段合并到前一个片段
        """
        merged_scenes = []
        
        for i, scene in enumerate(scenes):
            # 计算当前场景持续时间
            start_time_seconds = scene[0].get_frames() / scene[0].framerate
            end_time_seconds = scene[1].get_frames() / scene[1].framerate
            duration = end_time_seconds - start_time_seconds
            
            if duration >= min_duration:
                # 时长足够，直接保留
                merged_scenes.append(scene)
            else:
                # 时长不足，合并到前一个片段
                if merged_scenes:
                    print(f"    短片段 {i+1} 时长 {duration:.2f}s < {min_duration}s，合并到前一个片段")
                    # 扩展前一个片段的结束时间
                    prev_scene = merged_scenes[-1]
                    new_end_frame = scene[1]
                    merged_scenes[-1] = (prev_scene[0], new_end_frame)
                    print(f"    合并后前一片段延长到: {new_end_frame.get_timecode()}")
                else:
                    # 如果没有前一个片段，直接保留
                    print(f"    短片段 {i+1} 时长 {duration:.2f}s < {min_duration}s，但没有前一片段可合并，保留原片段")
                    merged_scenes.append(scene)
        
        return merged_scenes

    # 对超过60秒的长场景进行拆分
    split_scenes = split_long_scenes(adjusted_scene_list)
    
    # 调试信息
    print(f"原始场景数量: {len(adjusted_scene_list)}")
    print(f"拆分后场景数量: {len(split_scenes)}")
    
    # 使用所有场景（不再进行短片段合并）
    final_scenes = split_scenes

    def process_short_scenes(video_path, scene, output_path):
        """
        处理短片段：
        1. 丢弃小于1秒的片段
        2. 对1-4秒片段进行倍速调节，使其变为4-5秒
        """
        # 计算场景持续时间
        start_time = scene[0].get_seconds()
        end_time = scene[1].get_seconds()
        duration = end_time - start_time
        
        if duration < 1.0:
            # 小于1秒，丢弃
            print(f"    片段时长 {duration:.2f}s < 1s，跳过")
            return False, "时长不足1秒，已跳过"
        
        if duration < 4.0:
            # 1-4秒，需要倍速调节使其变为4.5秒
            target_duration = 4.5  # 目标时长
            # 计算setpts倍数：目标时长/原时长
            # 2秒 → 4.5秒：setpts=2.25*PTS
            # 3秒 → 4.5秒：setpts=1.5*PTS
            setpts_factor = target_duration / duration
            
            print(f"    片段时长 {duration:.2f}s，需要倍速调节")
            print(f"    目标时长: {target_duration:.2f}s，setpts倍数: {setpts_factor:.2f}x")
            print(f"    验证: {duration:.2f}s × {setpts_factor:.2f} = {duration * setpts_factor:.2f}s")
            
            # 如果倍数过大，限制到最大安全值
            max_safe_factor = 2.0
            if setpts_factor > max_safe_factor:
                print(f"    倍数 {setpts_factor:.2f}x 过大，限制到 {max_safe_factor:.2f}x")
                print(f"    实际输出时长: {duration * max_safe_factor:.2f}s")
                setpts_factor = max_safe_factor
            
            # 使用倍速调节的切割方法（只保留视频，丢弃音频）
            # 参考原代码使用-vf参数进行倍速处理
            cmd = [
                'ffmpeg', '-i', video_path,
                '-loglevel', 'error',
                '-ss', str(start_time),  # 开始时间
                '-t', str(duration),     # 持续时间
                '-c:v', 'libx264',       # 视频编码器
                '-preset', 'ultrafast',  # 编码预设
                '-crf', '18',           # 质量设置
                '-pix_fmt', 'yuv420p',  # 像素格式
                '-an',                  # 丢弃音频流
                '-vf', f'setpts={setpts_factor}*PTS',  # 视频倍速处理（参考原代码）
                '-avoid_negative_ts', 'make_zero',
                '-y',                   # 覆盖输出
                str(output_path)
            ]
            
            try:
                result = subprocess.run(cmd, check=True)
                return True, "倍速调节成功"
            except subprocess.CalledProcessError as e:
                if e.stderr:
                    try:
                        error_msg = e.stderr.decode('utf-8', errors='ignore')
                        print(f"FFmpeg错误: {error_msg}")
                    except:
                        print("FFmpeg执行失败")
                return False, str(e)
        else:
            # 大于等于4秒，正常处理
            return simple_video_cut(video_path, scene, output_path)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 处理场景统计
    processed_count = 0
    skipped_count = 0
    speed_adjusted_count = 0

    # 使用精确切割方法处理每个场景
    if final_scenes:  # 确保有场景需要处理
        print(f"开始处理 {len(final_scenes)} 个场景...")
        
        for i, scene in enumerate(final_scenes):
            # 计算场景持续时间用于预检查
            start_time = scene[0].get_seconds()
            end_time = scene[1].get_seconds()
            duration = end_time - start_time
            
            # 生成输出文件名
            output_filename = f"{global_scene_counter}.mp4"
            output_path = output_dir / output_filename
            
            print(f"\n")
            print(f"切割分段:{i+1}/{len(final_scenes)} - {output_filename} (时长: {duration:.2f}s)")
            
            # 使用短片段处理方法
            success, error = process_short_scenes(video_path, scene, output_path)
            
            if success:
                print(f"分段处理完成: {output_filename}")
                processed_count += 1
                global_scene_counter += 1
            else:
                print(f"    处理结果: {error}")
                skipped_count += 1
                if "倍速调节" in str(error):
                    speed_adjusted_count += 1
        
        print(f"\n场景处理统计:")
        print(f"  成功处理: {processed_count} 个")
        print(f"  跳过丢弃: {skipped_count} 个")
        if speed_adjusted_count > 0:
            print(f"  倍速调节: {speed_adjusted_count} 个")
    else:
        print("警告: 没有找到任何场景需要处理！")
        
    print(f"\n视频分割完成！片段已保存到: {output_dir}")
    
    # 移动原视频到 origin 目录
    try:
        origin_dir = Path(material_origin_dir)
        origin_dir.mkdir(parents=True, exist_ok=True)
        
        video_filename = Path(video_path).name
        origin_video_path = origin_dir / video_filename
        
        # 如果目标文件已存在，添加序号
        counter = 1
        while origin_video_path.exists():
            stem = Path(video_path).stem
            suffix = Path(video_path).suffix
            origin_video_path = origin_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # 移动文件
        os.rename(video_path, origin_video_path)
        print(f"原视频已移动到: {origin_video_path}")
        
    except Exception as e:
        print(f"移动原视频失败: {e}")
else:
    print(f"没有符合条件的场景需要分割: {video_path}")
        
# 显示处理统计信息
original_count = len(adjusted_scene_list)
final_count = len(final_scenes)

if original_count != final_count:
    print(f"场景拆分统计: 检测到 {original_count} 个硬切换场景，拆分后 {final_count} 个分段")
else:
    print(f"场景处理完成: {original_count} 个硬切换场景，无需拆分")
        
print("\n所有视频处理完成！")
