"""
Relationship analysis prompts
"""

ANALYZE_RELATIONSHIPS_PROMPT = """你是一个专业的小说人物关系分析专家。

请分析以下小说文本中人物之间的关系。

【已识别的人物】
{characters}

【关系类型说明】
- family: 亲属关系（父母、子女、兄弟姐妹、配偶等）
- friend: 朋友关系（挚友、同窗、同道等）
- enemy: 敌对关系（仇人、对手、敌人等）
- lover: 恋人关系（恋人、暧昧对象等）
- colleague: 同事关系（同僚、上下级、师徒等）
- other: 其他关系

【输出格式】
对于每对有关系的人物，提供：
- source: 人物A的名字
- target: 人物B的名字
- type: 关系类型（上述类型之一）
- subtype: 具体关系（如"父子"、"夫妻"、"死敌"等）
- strength: 关系强度（0.0-1.0，越高表示关系越紧密或重要）
- description: 关系描述（简短说明两人关系的性质和特点）

【小说文本】
{text}

【输出】
请只返回JSON数组：
```json
[
  {{
    "source": "人物A",
    "target": "人物B",
    "type": "family",
    "subtype": "父子",
    "strength": 0.9,
    "description": "血缘关系，父慈子孝"
  }}
]
```
"""

ANALYZE_RELATIONSHIP_EVOLUTION_PROMPT = """你是一个专业的小说分析专家，擅长追踪人物关系的演变。

请分析以下不同章节中，指定人物关系的变化过程。

【分析对象】
人物A: {character_a}
人物B: {character_b}

【各章节文本】
{chapter_texts}

【分析要求】
1. 追踪两人关系的起点
2. 记录关键转折事件
3. 分析关系变化的原因
4. 评估当前关系状态

【输出格式】
```json
{{
  "initial_state": {{
    "type": "初始关系类型",
    "description": "初始关系描述"
  }},
  "evolution": [
    {{
      "chapter": 3,
      "event": "关键事件描述",
      "change": "关系变化描述",
      "new_type": "新的关系类型"
    }}
  ],
  "current_state": {{
    "type": "当前关系类型",
    "strength": 0.8,
    "description": "当前关系描述"
  }}
}}
```
"""
