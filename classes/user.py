from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    passwd = Column(String)
    is_admin = Column(Boolean)

    def __init__(self, login: str, is_admin: bool):
        super().__init__()
        self.login = login
        self.is_admin = is_admin

    def set_conn_info(self, queue: str, discon_id: str):
        self.queue = queue
        self.discon_id = discon_id
