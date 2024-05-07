import sqlite3
from sqlite3 import ProgrammingError
from abc import ABC, abstractmethod

try:
    from typing import Self
except ImportError as exc:
    from typing_extensions import Self    

from blogwise.utils import ipsum_p


class Model(ABC):
    db: sqlite3.Connection = None
    table_name: str 
    columns: list 

    @classmethod
    def init_db(cls, db_uri: str) -> None:
        cls.db = sqlite3.connect(db_uri, check_same_thread=False)
        cls.db.row_factory = sqlite3.Row
        cls.create_table()

    @classmethod
    def create_table(cls):
        statement = f'CREATE TABLE IF NOT EXISTS {cls.table_name} ({", ".join(cls.columns)})'
        with cls.db:
            cls.db.execute(statement)

    @classmethod
    def drop_table(cls):
        statement = f'DROP TABLE {cls.table_name}'
        with cls.db:
            cls.db.execute(statement)

    @classmethod
    def create(cls, **kwargs):
        tbl_vals = ", ".join([f':{k}' for k in kwargs.keys() if k in cls.columns])
        tbl_cols = ", ".join([k for k in kwargs.keys() if k in cls.columns])
        statement = 'INSERT INTO {} ({}) VALUES ({})'.format(cls.table_name, tbl_cols, tbl_vals)
        select = f'SELECT rowid, * from {cls.table_name} WHERE rowid=?'
        try:
            with cls.db:
                result = cls.db.execute(statement, kwargs)
            rowid = result.lastrowid
            query = cls.db.execute(select, (rowid,)).fetchone()
            article = cls(**query)
            return article
        except ProgrammingError as exc:
            raise BlogwiseDatabaseError(exc)

    @classmethod
    def get_all(cls) -> list[Self]:
        statement = f'SELECT rowid, * from {cls.table_name}'
        with cls.db:
            results = cls.db.execute(statement).fetchall()
            return [cls(**row) for row in results]

    @classmethod
    def get_by_id(cls, row_id) -> Self:
        statement = f'SELECT rowid, * FROM {cls.table_name} WHERE rowid=?'

        with cls.db:
            result = cls.db.execute(statement, (row_id,)).fetchone()
        if result:
            instance = cls(**result)
            return instance
    
    @classmethod
    def update(cls, obj_id: any, data: dict) -> Self:
        instance = cls.get_by_id(obj_id)

        if instance:
            for k, v in data.items():
                setattr(instance, k, v)
            instance.save()
            return instance

    @classmethod
    def delete(cls, obj_id: any) -> None:
        statement = f'DELETE FROM {cls.table_name} WHERE rowid = ?' 
        with cls.db:
            cls.db.execute(statement, (obj_id,))

    @classmethod
    def filter_by(cls, **kwargs) -> list:
        rows = cls.get_all()
        filtered = []
        for row in rows:
            for prop in kwargs.keys():
                if not prop in cls.columns: 
                    break
                if hasattr(row, prop):
                    if kwargs.get(prop) == getattr(row, prop):
                        filtered.append(row)

        return filtered

    @abstractmethod
    def seed(cls, count:int = 25, repeat: bool = False, drop: bool = False) -> None:
        raise NotImplemented

    @abstractmethod
    def loaddata() -> None:
        """Import stored data into database."""
        raise NotImplemented

    def save(self) -> None:
        vals = []
        for k, v in self.__dict__.items():
            if k in self.columns:  # skip rowid
                if not isinstance(v, str):
                    vals.append(f"{k} = {v}")
                else:
                    vals.append(f"{k} = '{v}'")
        row_data = ', '.join(vals)
        statement = f'UPDATE {self.table_name} SET {row_data} WHERE rowid = ?'
        with self.db:
            self.db.execute(statement, (self.row_id,))
        updated_row = self.get_by_id(self.row_id)
        # TODO: Retest -- need to be careful that querysets are up to date and garbage is removed.
        self.__dict__ = updated_row.__dict__.copy()
        del updated_row


class Article(Model):
    table_name: str = 'articles'
    columns: list = ['title', 'content', 'is_featured', 'is_published']
    db: sqlite3.Connection = None

    def __init__(self, **kwargs):
        self.row_id = kwargs.get('rowid')
        self.title: str = kwargs.get('title')
        self.content: str = kwargs.get('content')
        self.is_featured: bool = kwargs.get('is_featured', False)
        self.is_published: bool = kwargs.get('is_published', True)

    def __eq__(self, other) -> bool:
        return (other.row_id == self.row_id and
                other.title == self.title and
                other.content == self.content)

    def __repr__(self) -> str:
        return f'<Article {self.row_id} | {self.title} (featured: {self.is_featured})>'

    def to_json(self) -> dict:
        return self.__dict__

    @classmethod
    def seed(cls, count:int = 25, repeat: bool = False, drop: bool = False) -> None:
        """Utility for testing."""
        if drop:
            cls.drop_table()
            cls.create_table()
        if not len(cls.get_all()) or repeat:
            from faker import Faker
            fake = Faker()
            # TODO: Change to use ? syntax or pass kwargs to db.execute below instead. Should match.
            statement = f'INSERT INTO articles ({", ".join(cls.columns)}) VALUES (:title, :content, False, True)'
            featured = f'INSERT INTO articles ({", ".join(cls.columns)}) VALUES (:title, :content, True, True)'
            
            with cls.db:
                for i in range(count):
                    cls.db.execute(statement, [' '.join(fake.words()).title(), ipsum_p()])

    @classmethod
    def loaddata() -> None:
        pass 

    @classmethod
    def reset_db(cls, seed: bool = False) -> None:
        cls.drop_table()
        cls.create_table()
        if seed:
            cls.seed()


def article_factory(is_featured=False, is_published=True) -> Article:
    from faker import Faker 
    fake = Faker()
    return Article.create(
        title='My Test Article',
        content=fake.paragraph(10),
        is_featured=is_featured,
        is_published=is_published)



