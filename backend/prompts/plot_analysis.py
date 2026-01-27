"""
Plot analysis prompts
"""

ANALYZE_PLOT_PROMPT = """你是一个专业的文学评论家，擅长分析小说的叙事结构。

请分析以下小说文本的情节结构。

【分析维度】
1. 主线情节：推动故事发展的核心事件
2. 支线情节：辅助性的故事线
3. 伏笔与悬念：未解之谜、暗示性描写
4. 冲突与高潮：戏剧性的对抗或转折

【小说文本】
{text}

【输出格式】
```json
{{
  "main_plot": {{
    "summary": "主线概述",
    "key_events": ["事件1", "事件2"]
  }},
  "subplots": [
    {{
      "name": "支线名称",
      "summary": "支线概述",
      "related_characters": ["角色1", "角色2"]
    }}
  ],
  "foreshadowing": [
    {{
      "content": "伏笔内容",
      "chapter": 1,
      "potential_meaning": "可能的含义"
    }}
  ],
  "conflicts": [
    {{
      "type": "冲突类型",
      "parties": ["冲突方1", "冲突方2"],
      "description": "冲突描述"
    }}
  ],
  "climax_hints": ["高潮暗示1", "高潮暗示2"]
}}
```
"""

TRACK_PLOT_THREAD_PROMPT = """你是一个专业的小说分析师，擅长追踪情节线索。

请在以下多个章节中追踪指定的情节线索。

【追踪目标】
情节线索: {plot_thread}

【章节内容】
{chapters}

【分析要求】
1. 标记该线索在每个章节中的出现位置
2. 记录线索的发展变化
3. 分析线索的走向趋势
4. 预测可能的结局

【输出格式】
```json
{{
  "thread_name": "线索名称",
  "appearances": [
    {{
      "chapter": 1,
      "content": "相关内容",
      "development": "发展情况"
    }}
  ],
  "trend": "发展趋势分析",
  "prediction": "结局预测"
}}
```
"""

IDENTIFY_FORESHADOWING_PROMPT = """你是一个细心的文学分析师，擅长发现小说中的伏笔和暗示。

请仔细阅读以下小说文本，识别其中可能存在的伏笔。

【伏笔类型】
1. 语言暗示：通过对话或描述暗示未来事件
2. 物品伏笔：特定物品可能在后文发挥作用
3. 行为伏笔：角色的异常行为暗示其动机或结局
4. 环境伏笔：场景描写暗示即将发生的事件
5. 结构伏笔：叙事结构上的暗示

【小说文本】
{text}

【输出格式】
```json
[
  {{
    "type": "伏笔类型",
    "content": "原文引用",
    "location": "出现位置（章节/段落）",
    "analysis": "分析说明",
    "confidence": 0.8,
    "potential_payoff": "可能的呼应/结果"
  }}
]
```
"""
