"""
File parser service for various novel formats
"""

import re
from typing import Dict, Any, List, Optional

import chardet


class FileParser:
    """Parse various file formats to extract novel content"""

    # Common chapter title patterns for Chinese novels
    CHAPTER_PATTERNS = [
        r"第[一二三四五六七八九十百千万零\d]+[章节回][\s:：]?.*",
        r"[【\[]?第[\d一二三四五六七八九十百千万零]+[章节回][】\]]?.*",
        r"Chapter\s+\d+.*",
        r"CHAPTER\s+\d+.*",
        r"卷[一二三四五六七八九十\d]+.*",
        r"^\d+[\.\s、].*",
    ]

    def __init__(self):
        self.chapter_pattern = re.compile(
            "|".join(f"({p})" for p in self.CHAPTER_PATTERNS), re.MULTILINE | re.IGNORECASE
        )

    async def parse(self, content: bytes, file_ext: str, filename: str) -> Dict[str, Any]:
        """Parse file content based on extension"""

        if file_ext == ".txt":
            return await self._parse_txt(content, filename)
        elif file_ext == ".docx":
            return await self._parse_docx(content, filename)
        elif file_ext == ".epub":
            return await self._parse_epub(content, filename)
        elif file_ext == ".mobi":
            return await self._parse_mobi(content, filename)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    async def _parse_txt(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse TXT file"""
        # Detect encoding
        detected = chardet.detect(content)
        encoding = detected.get("encoding", "utf-8")

        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            # Fallback encodings
            for enc in ["utf-8", "gbk", "gb2312", "gb18030", "big5"]:
                try:
                    text = content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = content.decode("utf-8", errors="ignore")

        # Extract title from filename
        title = filename.rsplit(".", 1)[0]

        # Split into chapters
        chapters = self._split_chapters(text)

        # Calculate total words
        total_words = sum(ch["word_count"] for ch in chapters)

        return {
            "title": title,
            "author": self._extract_author(text),
            "chapters": chapters,
            "total_words": total_words,
        }

    async def _parse_docx(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse DOCX file"""
        try:
            from docx import Document
            from io import BytesIO

            doc = Document(BytesIO(content))

            # Extract all paragraphs
            text = "\n".join([para.text for para in doc.paragraphs])

            title = filename.rsplit(".", 1)[0]
            chapters = self._split_chapters(text)
            total_words = sum(ch["word_count"] for ch in chapters)

            return {
                "title": title,
                "author": self._extract_author(text),
                "chapters": chapters,
                "total_words": total_words,
            }
        except ImportError:
            raise ImportError("python-docx is required for DOCX parsing")

    async def _parse_epub(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse EPUB file"""
        try:
            from ebooklib import epub
            from bs4 import BeautifulSoup
            from io import BytesIO

            book = epub.read_epub(BytesIO(content))

            # Get metadata
            title = book.get_metadata("DC", "title")
            title = title[0][0] if title else filename.rsplit(".", 1)[0]

            author = book.get_metadata("DC", "creator")
            author = author[0][0] if author else None

            # Extract text from all documents
            chapters = []
            for item in book.get_items():
                if item.get_type() == 9:  # ITEM_DOCUMENT
                    soup = BeautifulSoup(item.get_content(), "lxml")
                    text = soup.get_text(separator="\n", strip=True)

                    if text.strip():
                        # Try to get chapter title
                        h_tags = soup.find_all(["h1", "h2", "h3"])
                        chapter_title = h_tags[0].get_text(strip=True) if h_tags else None

                        chapters.append(
                            {
                                "title": chapter_title or f"Chapter {len(chapters) + 1}",
                                "content": text,
                                "word_count": len(text),
                            }
                        )

            total_words = sum(ch["word_count"] for ch in chapters)

            return {
                "title": title,
                "author": author,
                "chapters": chapters,
                "total_words": total_words,
            }
        except ImportError:
            raise ImportError("ebooklib and beautifulsoup4 are required for EPUB parsing")

    async def _parse_mobi(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse MOBI file"""
        # MOBI parsing is complex, for now we'll raise an error
        # In production, use mobi library or convert to EPUB first
        raise NotImplementedError(
            "MOBI parsing is not fully implemented. Please convert to EPUB or TXT format."
        )

    def _split_chapters(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chapters based on chapter patterns"""
        lines = text.split("\n")
        chapters = []
        current_chapter = {"title": "前言/序章", "content": [], "word_count": 0}

        for line in lines:
            # Check if line matches chapter pattern
            if self.chapter_pattern.match(line.strip()):
                # Save current chapter if it has content
                if current_chapter["content"]:
                    current_chapter["content"] = "\n".join(current_chapter["content"])
                    current_chapter["word_count"] = len(current_chapter["content"])
                    if current_chapter["word_count"] > 0:
                        chapters.append(current_chapter)

                # Start new chapter
                current_chapter = {"title": line.strip(), "content": [], "word_count": 0}
            else:
                current_chapter["content"].append(line)

        # Don't forget the last chapter
        if current_chapter["content"]:
            current_chapter["content"] = "\n".join(current_chapter["content"])
            current_chapter["word_count"] = len(current_chapter["content"])
            if current_chapter["word_count"] > 0:
                chapters.append(current_chapter)

        # If no chapters were found, treat entire text as one chapter
        if not chapters:
            chapters = [{"title": "全文", "content": text, "word_count": len(text)}]

        return chapters

    def _extract_author(self, text: str) -> Optional[str]:
        """Try to extract author from text"""
        # Common author patterns
        patterns = [
            r"作者[：:]\s*(.+)",
            r"著者[：:]\s*(.+)",
            r"作\s*者[：:]\s*(.+)",
            r"by\s+(.+)",
            r"Author[：:]\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:5000], re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                # Clean up author name
                author = author.split("\n")[0].strip()
                if len(author) < 50:  # Reasonable author name length
                    return author

        return None
