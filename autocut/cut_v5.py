class AutoCut:
    def __init__(self, content):
        """
        初始化AutoCut类，解析文案内容
        
        Args:
            content (str): 待解析的文案内容
        """
        self.content = content
        self.parsed_data = self._parse_content()
    
    def _parse_content(self):
        """
        解析文案内容，将文本按句子分割并转换为指定结构
        
        Returns:
            list: 包含多个字典的列表，每个字典包含id、text、audio_length、video_path
        """
        # 按句子分割文本，去除空行和只包含空格的行
        sentences = []
        lines = self.content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line:  # 非空行
                sentences.append(line)
        
        # 构建返回数据
        parsed_data = []
        for i, sentence in enumerate(sentences, 1):
            parsed_data.append({
                "id": i,
                "text": sentence,
                "audio_length": None,  # 暂时为空，后续可以添加语音识别功能
                "video_path": ""      # 暂时为空，后续可以添加视频处理功能
            })
        
        return parsed_data
    
    def get_parsed_data(self):
        """
        获取解析后的数据
        
        Returns:
            list: 解析后的数据结构
        """
        return self.parsed_data
    
    def add_audio_length(self, sentence_id, length):
        """
        为指定句子添加音频时长
        
        Args:
            sentence_id (int): 句子ID
            length (float): 音频时长（秒）
        """
        for item in self.parsed_data:
            if item["id"] == sentence_id:
                item["audio_length"] = length
                break
    
    def add_video_path(self, sentence_id, video_path):
        """
        为指定句子添加视频路径
        
        Args:
            sentence_id (int): 句子ID
            video_path (str): 视频文件路径
        """
        for item in self.parsed_data:
            if item["id"] == sentence_id:
                item["video_path"] = video_path
                break
    
    def get_total_duration(self):
        """
        计算总音频时长
        
        Returns:
            float: 总时长（秒）
        """
        total_duration = 0
        for item in self.parsed_data:
            if item["audio_length"] is not None:
                total_duration += item["audio_length"]
        return total_duration
    
    def get_sentence_by_id(self, sentence_id):
        """
        根据ID获取指定句子
        
        Args:
            sentence_id (int): 句子ID
            
        Returns:
            dict or None: 找到的句子字典，如果不存在返回None
        """
        for item in self.parsed_data:
            if item["id"] == sentence_id:
                return item
        return None

if __name__ == "__main__":
    # 示例文案内容
    example_content = """
    是曾经拥有过全世界的绚烂，最后只剩下一地鸡毛的凄凉。
    这种落差，比从未拥有过更让人绝望。
    """
    # 创建AutoCut实例
    auto_cut = AutoCut(example_content)
    
    # 打印解析后的数据
    print(auto_cut.get_parsed_data())