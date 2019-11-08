from sqlalchemy import Column, Integer, String, Sequence, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import connector


class User(connector.Manager.Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('chat_user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))
    username = Column(String(12))


class Message(connector.Manager.Base):
    __tablename__ = 'messages'
    id = Column(Integer, Sequence('chat_message_id_seq'), primary_key=True)
    content = Column(String(500))
    sent_on = Column(DateTime(), default=datetime.datetime.utcnow, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


    user_from_id = Column(Integer, ForeignKey('users.id'))
    user_to_id = Column(Integer, ForeignKey('users.id'))
    user_from = relationship(User, foreign_keys=[user_from_id])
    user_to = relationship(User, foreign_keys=[user_to_id])

class Group(connector.Manager.Base):
    __tablename__ = "groups"
    id = Column(Integer, Sequence('groups_id_seq'), primary_key=True)
    name = Column(String(500))
