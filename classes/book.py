from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import json


Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    author = Column(String)
    pages = Column(Integer)

    def __init__(self, name: str, author: str, pages: int):
        super().__init__()
        self.name = name
        self.author = author
        self.pages = pages

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class BookJson(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Book):
            return {c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns}
        return json.JSONEncoder.default(self, obj)

    def from_json(json_list: dict):
        items = []
        for item in json_list:
            another_book = Book(item['name'], item['author'], item['pages'])
            another_book.id = item['id']
            items.append(another_book)
        return items

