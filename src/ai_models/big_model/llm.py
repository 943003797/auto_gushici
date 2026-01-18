from zai import ZhipuAiClient
import os
from dotenv import load_dotenv

load_dotenv()


class LLM:
    def __init__(self, model: str = "glm-4.5-flash"):
        self.model = model
        self.client = ZhipuAiClient(api_key=os.getenv("BIG_MODEL"))

    def get_tag(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": f"""
                                    给出视频的情绪标签（emotion）、场景标签（scene）、人物关系（person_relation）、互动标签（interaction）、抽象概念标签（abstract_concept）。
                                    文案：{text}
                                    从各标签：情绪标签（emotion）、场景标签（scene）、人物关系（person_relation）、互动标签（interaction）、抽象概念标签（abstract_concept）中，各选出唯一一个最符合文案的标签。用|隔开。
                                    参考标签（必须从参考标签中分别选择出唯一一个权重最高的标签）：
                                    情绪标签（emotion）： 平静|忧郁|豪迈|欢快|严肃|孤独|惆怅|温馨|沉重|激动|惊讶|思念
                                    场景标签（scene）： 苍山|江海|大漠|云海|雨天|雪天|枯树|宫廷|院子|古道|古寺|书房|灯火|树林|市井|码头|田园
                                    人物关系（person_relation）： 独处|好友|师徒|君臣|眷侣|路人
                                    互动标签（interaction）： 书写|绘画|研墨|诵读|翻阅|对弈|抚琴|点香|对酌|独饮|行礼|相迎|赠别|挥手|远眺|观望|信步|游历|垂钓|采摘|耕作
                                    抽象概念标签（abstract_concept）（提取时注意，视频注意视频是无声的）： 情感共鸣|时间流逝|留白艺术

                                    返回格式：
                                    标签1|标签2|标签3...
                                    """
                    }
                ],
                stream=False,              # 禁用流式输出
                max_tokens=4096,          # 最大输出 tokens
                temperature=0.7           # 控制输出的随机性
            )
            
            # 直接获取内容，假设 response 有 choices 属性
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            else:
                # 如果不是预期的格式，尝试其他可能的属性
                return str(response)
                
        except Exception as e:
            print(f"[ERROR] LLM.get_tag 出错: {e}")
            # 返回默认标签
            return "忧郁|江海|独处|独饮|情感共鸣"
    
    def get_video_description(self, wenan: str, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": f"""
                                    综合完整文案的内容。为这句文案：{text}，描述一个合适的配视频场景。字数在20字以内。下面是完整的文案：
                                    完整文案：{wenan}
                                    以JSON格式返回：{"video_description": "视频描述"}
                                    """
                    }
                ],
                stream=False,              # 禁用流式输出
                max_tokens=4096,          # 最大输出 tokens
                temperature=0.7           # 控制输出的随机性
            )
            
            # 直接获取内容，假设 response 有 choices 属性
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            else:
                # 如果不是预期的格式，尝试其他可能的属性
                return str(response)
                
        except Exception as e:
            print(f"[ERROR] LLM.get_video_description 出错: {e}")
            # 返回默认描述

if __name__ == "__main__":
    llm = LLM()
    result = llm.get_tag("开篇连用14个叠字，寻寻觅觅，冷冷清清，凄凄惨惨戚戚。")
    print(f"标签结果: {result}")