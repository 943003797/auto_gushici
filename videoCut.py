from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg, is_ffmpeg_available
from scenedetect.frame_timecode import FrameTimecode
from pathlib import Path
from src.ai_models.big_model.video import video
import os
import glob
import subprocess
import locale
import sys

material_dir = 'D:/Material/new_video'
material_origin_dir = 'D:/Material/origin'
v = video()
# 设置编码
if sys.platform.startswith('win'):
    # Windows系统编码设置
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def split_video_into_scenes(video_path, threshold=25):
    # Open our video, create a scene manager, and add a detector.
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

def precise_cut_with_reencoding(video_path, scene, output_path, adjust_frames=0):
    """
    使用重新编码的方式进行精确切割
    """
    # 计算精确的切割时间点
    start_time = scene[0].get_seconds() + adjust_frames / scene[0].framerate
    end_time = scene[1].get_seconds() - adjust_frames / scene[1].framerate
    duration = end_time - start_time
    print(f"start_time：{start_time}")
    print(f"end_time：{end_time}")
    print(f"duration1：{duration}")
    
    # 使用ffmpeg进行精确切割（优化压缩参数）
    cmd = [
        'ffmpeg', '-i', video_path,
        '-loglevel', 'error',   # 只显示错误
        '-ss', str(start_time),  # 开始时间
        '-t', str(duration),     # 持续时间
        '-c:v', 'libx264',       # 重新编码视频
        '-preset', 'slow',       # 编码预设：slow提供更好压缩率
        '-crf', '26',           # 质量设置：26是压缩率与画质的平衡点
        '-profile:v', 'main',    # H.264主配置文件
        '-level', '4.0',        # H.264级别设置
        '-pix_fmt', 'yuv420p',  # 像素格式：确保兼容性
        '-b:v', '0',            # 设置码率为自动（基于CRF）
        '-g', '30',             # GOP大小：每30帧一个关键帧
        '-sc_threshold', '0',   # 禁用场景变化检测
        '-keyint_min', '30',    # 最小关键帧间隔
        '-x264-params', 'aq-mode=3:aq-strength=0.8:psy-rd=1.0:deblock=-1,-1', # 高级编码参数
        '-c:a', 'aac',          # 重新编码音频
        '-b:a', '96k',          # 音频码率：降低到96k减小文件大小
        '-ar', '44100',         # 音频采样率
        '-avoid_negative_ts', 'make_zero',
        '-y',                   # 覆盖输出文件
        str(output_path)
    ]
    
    try:
        # 不捕获输出，让错误信息直接显示在终端
        result = subprocess.run(cmd, check=True)
        # 大模型二次裁剪
        print(f"duration：{duration}")
        if(duration > 9):
            print(f"output_path：{output_path}")
            splitTime = v.get_video_tag(video_path=output_path)
            if splitTime is None:
                print("无法获取视频时长")
            else:
                # 将整数字符串转为秒数
                start_time = int(splitTime["start"])
                end_time = int(splitTime["end"])
                # 二次裁剪：按 start_time 和 end_time 重新截取并覆盖原文件
                tmp_path = output_path.with_suffix('.tmp.mp4')
                cmd_trim = [
                    'ffmpeg', '-i', str(output_path),
                    '-ss', str(start_time),
                    '-to', str(end_time),
                    '-loglevel', 'error',   # 只显示错误
                    '-c:v', 'libx264',       # 重新编码视频
                    '-preset', 'slow',       # 编码预设：slow提供更好压缩率
                    '-crf', '26',           # 质量设置：26是压缩率与画质的平衡点
                    '-profile:v', 'main',    # H.264主配置文件
                    '-level', '4.0',        # H.264级别设置
                    '-pix_fmt', 'yuv420p',  # 像素格式：确保兼容性
                    '-b:v', '0',            # 设置码率为自动（基于CRF）
                    '-g', '30',             # GOP大小：每30帧一个关键帧
                    '-sc_threshold', '0',   # 禁用场景变化检测
                    '-keyint_min', '30',    # 最小关键帧间隔
                    '-x264-params', 'aq-mode=3:aq-strength=0.8:psy-rd=1.0:deblock=-1,-1', # 高级编码参数
                    '-c:a', 'aac',          # 重新编码音频
                    '-b:a', '96k',          # 音频码率：降低到96k减小文件大小
                    '-ar', '44100',         # 音频采样率
                    '-avoid_negative_ts', 'make_zero',
                    '-y',
                    str(tmp_path)
                ]
                print(f"      执行二次裁剪命令...")
                subprocess.run(cmd_trim, check=True)
                
                # 安全地替换原文件
                try:
                    # 先删除原文件
                    if output_path.exists():
                        output_path.unlink()
                    # 将临时文件重命名为最终文件
                    tmp_path.rename(output_path)
                    print(f"      二次裁剪完成，文件已覆盖")
                except Exception as file_error:
                    # 如果文件操作失败，清理临时文件
                    if tmp_path.exists():
                        tmp_path.unlink()
                    print(f"      文件替换失败: {file_error}")
                    raise file_error
                    
                print(f"二次start_time：{start_time}")
                print(f"二次end_time：{end_time}")
        # 大模型二次裁剪
        return True, None
    except subprocess.CalledProcessError as e:
        # 直接输出错误信息
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

def remove_audio_from_video(input_path, output_path):
    """
    去除视频中的音频轨道并优化压缩
    """
    cmd = [
        'ffmpeg', '-i', str(input_path),
        '-loglevel', 'error',   # 只显示错误
        '-an',              # 去除音频
        '-c:v', 'libx264',  # 重新编码视频以优化压缩
        '-preset', 'slow',   # 编码预设：slow提供更好压缩率
        '-crf', '28',      # 质量设置：较高值减小文件大小
        '-profile:v', 'main', # H.264主配置文件
        '-level', '4.0',   # H.264级别设置
        '-pix_fmt', 'yuv420p', # 像素格式
        '-b:v', '0',       # 设置码率为自动（基于CRF）
        '-g', '30',        # GOP大小
        '-sc_threshold', '0', # 禁用场景变化检测
        '-y',              # 覆盖输出文件
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
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
    
    # 过滤掉超过15秒的场景
    max_duration_seconds = 15
    min_duration_seconds = 2
    filtered_scene_list = []

    for i, scene in enumerate(adjusted_scene_list):
        # 计算场景持续时间（以秒为单位）
        start_time_seconds = scene[0].get_frames() / scene[0].framerate
        end_time_seconds = scene[1].get_frames() / scene[1].framerate
        duration = end_time_seconds - start_time_seconds
        
        if duration <= max_duration_seconds and duration >= min_duration_seconds:
            filtered_scene_list.append(scene)
            # print(f'    Scene {i+1}: Start {scene[0].get_timecode()} / Frame {scene[0].frame_num}, '
            #       f'End {scene[1].get_timecode()} / Frame {scene[1].frame_num}, '
            #       f'Duration: {duration:.2f}s - INCLUDED')
        # else:
        #     print(f'    Scene {i+1}: Start {scene[0].get_timecode()} / Frame {scene[0].frame_num}, '
        #           f'End {scene[1].get_timecode()} / Frame {scene[1].frame_num}, '
        #           f'Duration: {duration:.2f}s - SKIPPED (too long)')

    # 简洁的Start和End时间循环输出
    for i, scene in enumerate(filtered_scene_list):
        start_time = scene[0].get_timecode()
        end_time = scene[1].get_timecode()
        # print(f"Scene {i+1}: Start {start_time}, End {end_time}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 使用精确切割方法处理每个场景
    if filtered_scene_list:  # 确保有场景需要处理
        
        for i, scene in enumerate(filtered_scene_list):
            # 生成输出文件名
            output_filename = f"{global_scene_counter}.mp4"
            output_path = output_dir / output_filename
            
            print(f"\n")
            print(f"切割分段:{i+1}")
            
            # 使用精确切割方法
            success, error = precise_cut_with_reencoding(video_path, scene, output_path)
            
            if success:
                print(f"分段处理完成: {output_filename}")
                
                # 去声音处理
                temp_path = output_path
                final_path = output_path
                
                # 先检查是否需要去声音（这里我们假设总是需要去声音）
                # 如果想要可选处理，可以添加一个配置变量
                audio_removed_path = output_dir / f"no_audio_{output_filename}"
                
                success_audio, error_audio = remove_audio_from_video(temp_path, audio_removed_path)
                
                if success_audio:
                    # 删除原文件，重命名去声音版本
                    temp_path.unlink()
                    audio_removed_path.rename(final_path)
                else:
                    print(f"    音频去除失败: {error_audio}")
                
                global_scene_counter += 1
            else:
                print(f"    切割失败: {error}")
        
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
        
print("\n所有视频处理完成！")
