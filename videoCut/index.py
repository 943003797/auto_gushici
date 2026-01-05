from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg, is_ffmpeg_available
from pathlib import Path
import os
import glob

def split_video_into_scenes(video_path, threshold=27.0):
    # Open our video, create a scene manager, and add a detector.
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    scene_list = scene_manager.get_scene_list()
    return scene_list

# 检查是否可用ffmpeg
if not is_ffmpeg_available():
    print("警告: 未找到ffmpeg，请确保ffmpeg已安装并添加到PATH中")
    exit(1)

# 获取D:/Material目录下所有.mp4文件
material_dir = 'D:/Material/'
mp4_files = glob.glob(os.path.join(material_dir, '*.mp4'))

print(f"找到 {len(mp4_files)} 个MP4文件: {mp4_files}")

# 检查是否找到任何MP4文件
if not mp4_files:
    print("在 D:/Material/ 目录中没有找到任何.mp4文件")
    exit(1)

# 初始化全局场景计数器
global_scene_counter = 1

# Process each video file
for video_path in mp4_files:
    print(f"\n正在处理视频: {video_path}")
    
    # 分析视频并获取场景列表
    scene_list = split_video_into_scenes(video_path)
    
    # 过滤掉超过15秒的场景
    max_duration_seconds = 15
    min_duration_seconds = 1
    filtered_scene_list = []

    for i, scene in enumerate(scene_list):
        # 计算场景持续时间（以秒为单位）
        start_time_seconds = scene[0].get_frames() / scene[0].framerate
        end_time_seconds = scene[1].get_frames() / scene[1].framerate
        duration = end_time_seconds - start_time_seconds
        
        if duration <= max_duration_seconds and duration >= min_duration_seconds:
            filtered_scene_list.append(scene)
            print(f'    Scene {i+1}: Start {scene[0].get_timecode()} / Frame {scene[0].frame_num}, '
                  f'End {scene[1].get_timecode()} / Frame {scene[1].frame_num}, '
                  f'Duration: {duration:.2f}s - INCLUDED')
        else:
            print(f'    Scene {i+1}: Start {scene[0].get_timecode()} / Frame {scene[0].frame_num}, '
                  f'End {scene[1].get_timecode()} / Frame {scene[1].frame_num}, '
                  f'Duration: {duration:.2f}s - SKIPPED (too long)')

    print(f"\n原始场景数: {len(scene_list)}, 过滤后场景数: {len(filtered_scene_list)}")
    scene_list = filtered_scene_list

    # 循环输出处理后的场景列表
    for i, scene in enumerate(scene_list):
        print(f"Processed Scene {i+1}: {scene}")

    print("\n--- 简洁循环输出 Start 和 End 时间 ---")
    # 简洁的Start和End时间循环输出
    for i, scene in enumerate(scene_list):
        start_time = scene[0].get_timecode()
        end_time = scene[1].get_timecode()
        print(f"Scene {i+1}: Start {start_time}, End {end_time}")

    print("\n--- 开始分割视频 ---")
    # 创建输出目录 - 使用一个统一的目录
    output_dir = Path(f"D:/Material/split/")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 使用临时文件列表和自定义分割方法，以实现连续编号
    if scene_list:  # 确保有场景需要处理
        print(f"正在使用高级分割方法分割视频 {Path(video_path).stem}...")
        
        # 临时分割视频到一个临时目录
        temp_output_dir = Path(f"D:/Material/temp_split_{Path(video_path).stem}/")
        temp_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用scenedetect的split_video_ffmpeg函数分割视频到临时目录
        result = split_video_ffmpeg(
            input_video_path=video_path, 
            scene_list=scene_list, 
            output_dir=temp_output_dir,
            output_file_template='TempScene-$SCENE_NUMBER.mp4',
            arg_override='-c copy',  # 直接复制流，不重新编码
            show_progress=True
        )
        
        if result == 0:
            # 重命名并移动文件到最终目录，使用全局计数器
            import shutil
            
            # 获取临时目录中的所有分割文件
            temp_files = sorted(temp_output_dir.glob("*.mp4"))
            
            for temp_file in temp_files:
                # 生成新的文件名，使用全局计数器
                new_filename = f"{global_scene_counter}.mp4"
                final_path = output_dir / new_filename
                
                # 移动并重命名文件
                shutil.move(str(temp_file), str(final_path))
                
                print(f"已保存: {final_path.name}")
                global_scene_counter += 1
            
            # 删除临时目录
            import shutil
            shutil.rmtree(temp_output_dir)
            
            print(f"\n视频分割完成！片段已保存到: {output_dir}")
        else:
            print(f"\n视频分割过程中出现错误，返回码: {result}")
            
            # 清理临时目录
            import shutil
            if temp_output_dir.exists():
                shutil.rmtree(temp_output_dir)
    else:
        print(f"没有符合条件的场景需要分割: {video_path}")
        
print("\n所有视频处理完成！")
