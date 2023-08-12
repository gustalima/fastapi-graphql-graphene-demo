# flask_sqlalchemy/schema.py
from typing import List

import graphene
from fastapi import Depends
from graphene import ID, Field, Int, ObjectType, String, relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from gql.database import get_db
from gql.models import Department as DepartmentModel
from gql.models import Employee as EmployeeModel
from gql.models import Todo as TodoModel


class Department(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)


class Employee(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node,)


class Todo(SQLAlchemyObjectType):
    class Meta:
        model = TodoModel
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    all_todos = SQLAlchemyConnectionField(Todo.connection)
    all_employees = SQLAlchemyConnectionField(Employee.connection)
    all_departments = SQLAlchemyConnectionField(Department.connection, sort=None)


class CreateTodo(graphene.Mutation, Session=Depends(get_db)):
    todo = graphene.Field(lambda: Todo)

    class Arguments:
        title = String(required=True)
        description = String()

    def mutate(self, info, title, description):
        db = get_db()
        print(db)

        todo = TodoModel(title=title, description=description)
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return CreateTodo(todo=todo)


class UpdateTodo(graphene.Mutation):
    todo = graphene.Field(lambda: Todo)

    class Arguments:
        id = ID(required=True)
        title = String()
        description = String()

    def mutate(self, info, id, title=None, description=None):
        db = get_db()
        todo = db.query(TodoModel).filter(TodoModel.id == id).first()
        if not todo:
            raise Exception("Todo not found")
        if title:
            todo.title = title
        if description:
            todo.description = description
        db.commit()
        db.refresh(todo)
        return UpdateTodo(todo=todo)


class DeleteTodo(graphene.Mutation):
    success = graphene.Field(lambda: String)

    class Arguments:
        id = ID(required=True)

    def mutate(self, info, id):
        db = get_db()
        todo = db.query(TodoModel).filter(TodoModel.id == id).first()
        if not todo:
            raise Exception("Todo not found")
        db.delete(todo)
        db.commit()
        return DeleteTodo(success=f"Todo {id} deleted successfully")


class Mutation(graphene.ObjectType):
    node = relay.Node.Field()

    create_to_do = CreateTodo.Field()
    update_to_do = UpdateTodo.Field()
    delete_to_do = DeleteTodo.Field()


# schema = graphene.Schema(query=Query, mutation=[CreateTodo, UpdateTodo, DeleteTodo])
schema = graphene.Schema(query=Query, mutation=Mutation)
