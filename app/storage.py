from typing import List, Dict
from app.agents.models import Article, EmailRecipient
from datetime import datetime

class MemoryDB:
    def __init__(self):
        self._articles: Dict[int, Article] = {}
        self._next_id = 1
        self.recipients: List[EmailRecipient] = []

    def add_article(self, source: str, title: str, url: str, content: str) -> Article:
        art = Article(
            id=self._next_id,
            source=source,
            title=title,
            url=url,
            content=content,
            created_at=datetime.utcnow(),
        )
        self._articles[self._next_id] = art
        self._next_id += 1
        return art

    def list_articles(self) -> List[Article]:
        return sorted(self._articles.values(), key=lambda a: a.created_at, reverse=True)

    def get_article(self, article_id: int) -> Article | None:
        return self._articles.get(article_id)

    def update_article(self, article_id: int, title: str | None, content: str | None) -> Article | None:
        art = self._articles.get(article_id)
        if not art: return None
        if title: art.title = title
        if content: art.content = content
        self._articles[article_id] = art
        return art

    def delete_article(self, article_id: int) -> bool:
        return bool(self._articles.pop(article_id, None))

DB = MemoryDB()
