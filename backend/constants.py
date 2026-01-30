"""
Centralized constants for the backend
"""

# Encoding related
COMMON_ENCODINGS = ["utf-8", "gbk", "gb18030", "big5", "latin-1"]
CHINESE_ENCODINGS = ["utf-8", "gbk", "gb2312", "gb18030", "big5"]

# Chinese character pattern
CHINESE_CHAR_PATTERN = r"[\u4e00-\u9fff]"

# Common Chinese surnames for name extraction
COMMON_CHINESE_SURNAMES = (
    "李王张刘陈杨黄赵周吴徐孙马朱胡郭何林罗高郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶杜丁蒋沈任姚卢"
    "傅钟姜崔谭廖范汪陆金石戴贾韦夏邱方侯邹熊孟秦白江阎薛闫段雷龙黎史陶贺顾毛郝龚邵万钱严覃河洪武莫孔"
    "汤向常温康施文牛樊葛邢安齐易乔伍庞颜倪庄聂章鲁岳翟殷詹申欧耿关兰焦俞左柳甘祝包宁尹"
)

# Relationship type names (English to Chinese)
RELATIONSHIP_TYPE_NAMES = {
    "family": "家庭关系",
    "friend": "朋友关系",
    "enemy": "敌对关系",
    "lover": "恋人关系",
    "colleague": "同事关系",
    "other": "其他关系",
}

# Plot event type names (English to Chinese)
EVENT_TYPE_NAMES = {
    "conflict": "冲突",
    "revelation": "揭示",
    "turning_point": "转折点",
    "climax": "高潮",
    "resolution": "解决",
}

# Analysis configurations
ANALYSIS_SAMPLE_SIZES = {
    "quick": 3,
    "standard": 10,
    "deep": -1,  # -1 means all chapters
}

ANALYSIS_SUMMARY_LIMITS = {
    "quick": 5,
    "standard": 20,
    "deep": -1,
}

# Concurrency limits
MAX_CONCURRENT_LLM_REQUESTS = 5

# File Parser patterns
CHAPTER_PATTERNS = [
    r"第[一二三四五六七八九十百千万零\d]+[章节回][\s:：]?.*",
    r"[【\[]?第[\d一二三四五六七八九十百千万零]+[章节回][】\]]?.*",
    r"Chapter\s+\d+.*",
    r"CHAPTER\s+\d+.*",
    r"卷[一二三四五六七八九十\d]+.*",
    r"^\d+[\.\s、].*",
]
