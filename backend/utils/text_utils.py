"""
Text processing utilities
"""
import re
from typing import List, Tuple


def count_words(text: str) -> int:
    """Count words/characters in text (Chinese-aware)"""
    # Remove whitespace
    text = text.strip()
    
    # For Chinese text, count characters
    # For English text, count words
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    if chinese_chars > len(text) * 0.3:
        # Primarily Chinese - count characters
        return len(re.sub(r'\s+', '', text))
    else:
        # Primarily English - count words
        return len(text.split())


def split_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    # Chinese and English sentence endings
    pattern = r'[。！？.!?]+["\'"』」]*'
    
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def extract_quotes(text: str) -> List[Tuple[str, str]]:
    """Extract quoted dialogue from text
    
    Returns list of (quote, speaker) tuples.
    Speaker might be empty if not identifiable.
    """
    quotes = []
    
    # Chinese quotes
    chinese_quote_pattern = r'[「『"](.*?)[」』"]'
    for match in re.finditer(chinese_quote_pattern, text):
        quote = match.group(1)
        # Try to find speaker before the quote
        before_text = text[max(0, match.start() - 50):match.start()]
        speaker = _extract_speaker(before_text)
        quotes.append((quote, speaker))
    
    # English quotes
    english_quote_pattern = r'"([^"]*)"'
    for match in re.finditer(english_quote_pattern, text):
        quote = match.group(1)
        before_text = text[max(0, match.start() - 50):match.start()]
        speaker = _extract_speaker(before_text)
        quotes.append((quote, speaker))
    
    return quotes


def _extract_speaker(text: str) -> str:
    """Try to extract speaker name from text before a quote"""
    # Common patterns
    patterns = [
        r'(\w+)道[：:]?\s*$',
        r'(\w+)说[：:]?\s*$',
        r'(\w+)问[：:]?\s*$',
        r'(\w+)笑道[：:]?\s*$',
        r'(\w+)\s+said',
        r'(\w+)\s+asked',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ""


def clean_text(text: str) -> str:
    """Clean text by removing unwanted characters"""
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove special control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to max length, preserving word boundaries"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    # Try to break at word boundary
    last_space = truncated.rfind(' ')
    last_punct = max(truncated.rfind('。'), truncated.rfind('.'), truncated.rfind('，'))
    
    break_point = max(last_space, last_punct)
    if break_point > max_length * 0.7:
        truncated = truncated[:break_point]
    
    return truncated + suffix


def extract_names(text: str) -> List[str]:
    """Extract potential character names from text"""
    names = set()
    
    # Chinese name patterns (2-4 characters)
    chinese_name_pattern = r'(?:^|[，。！？、；：""（）\s])([李王张刘陈杨黄赵周吴徐孙马朱胡郭何林罗高郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶杜丁蒋沈任姚卢傅钟姜崔谭廖范汪陆金石戴贾韦夏邱方侯邹熊孟秦白江阎薛闫段雷龙黎史陶贺顾毛郝龚邵万钱严覃河洪武莫孔汤向常温康施文牛樊葛邢安齐易乔伍庞颜倪庄聂章鲁岳翟殷詹申欧耿关兰焦俞左柳甘祝包宁尹][\u4e00-\u9fff]{1,3})(?=[，。！？、；：""（）\s]|$)'
    
    for match in re.finditer(chinese_name_pattern, text):
        name = match.group(1)
        if 2 <= len(name) <= 4:
            names.add(name)
    
    return list(names)


def highlight_text(text: str, keywords: List[str], tag: str = 'mark') -> str:
    """Highlight keywords in text with HTML tags"""
    for keyword in keywords:
        if keyword:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(f'<{tag}>{keyword}</{tag}>', text)
    
    return text
