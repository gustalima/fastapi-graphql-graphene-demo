# # flask_sqlalchemy/models.py
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, scoped_session, sessionmaker

from gql.database import Base


class Department(Base):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hired_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey("department.id"))
    department = relationship(Department, backref=backref("employees", uselist=True, cascade="delete,all"))


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
