"""
Summary generation prompts
"""

GENERATE_CHAPTER_SUMMARY_PROMPT = """请为以下小说章节生成一个简洁的摘要。

【要求】
1. 摘要长度：100-200字
2. 包含：主要事件、涉及人物、情节发展
3. 语言风格：客观、简洁
4. 避免剧透关键转折（如果是悬疑类）

【章节标题】
{title}

【章节内容】
{content}

【摘要】
"""

GENERATE_NOVEL_SUMMARY_PROMPT = """请为以下小说生成一个完整的内容简介。

【要求】
1. 简介长度：300-500字
2. 结构：背景设定 → 主要人物 → 核心冲突 → 故事走向
3. 不要透露结局
4. 突出小说的特色和看点

【小说信息】
书名：{title}
作者：{author}

【各章节摘要】
{chapter_summaries}

【内容简介】
"""

GENERATE_CHARACTER_SUMMARY_PROMPT = """请为小说中的以下人物生成一个角色简介。

【人物信息】
姓名：{name}
别名：{aliases}

【相关文本片段】
{text_excerpts}

【要求】
1. 简介长度：100-200字
2. 包含：身份背景、性格特点、在故事中的作用
3. 基于文本内容，不要虚构

【角色简介】
"""

GENERATE_RELATIONSHIP_SUMMARY_PROMPT = """请为以下两个角色之间的关系生成一段描述。

【角色信息】
角色A：{character_a}
角色B：{character_b}

【相关文本片段】
{text_excerpts}

【要求】
1. 描述长度：50-100字
2. 说明关系类型、亲密程度、关系发展
3. 基于文本内容进行描述

【关系描述】
"""
