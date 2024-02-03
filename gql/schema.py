import base64
import os

import graphene
from fastapi import Depends
from graphene import ID, Field, Int, ObjectType, String, relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from gql.database import get_db
from gql.models import Department as DepartmentModel
from gql.models import Employee as EmployeeModel
from gql.models import Todo as TodoModel


class FileItemType(graphene.ObjectType):
    name = graphene.String()
    is_directory = graphene.Boolean()
    full_path = graphene.String()
    depth = graphene.Int()


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


def list_directory_recursive(path, depth, parent_depth=0):
    file_list = []
    add_files_to_list(path, file_list, depth, parent_depth)
    return file_list


def add_files_to_list(path, file_list, depth, parent_depth):
    if depth is None or depth >= 0:
        files = os.listdir(path)
        for file in files:
            full_path = os.path.join(path, file)
            is_directory = os.path.isdir(full_path)
            file_list.append(
                FileItemType(name=file, is_directory=is_directory, full_path=full_path, depth=parent_depth)
            )
            if is_directory:
                add_files_to_list(full_path, file_list, None if depth is None else depth - 1, parent_depth + 1)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    all_todos = SQLAlchemyConnectionField(Todo.connection)
    all_employees = SQLAlchemyConnectionField(Employee.connection)
    all_departments = SQLAlchemyConnectionField(Department.connection, sort=None)
    list_directory = graphene.List(FileItemType, path=graphene.String(), depth=graphene.Int(default_value=None))

    def resolve_list_directory(self, info, path, depth):
        try:
            return list_directory_recursive(path, depth)
        except Exception as e:
            return [FileItemType(name=str(e), is_directory=False, full_path="", depth=0)]


class CreateTodo(graphene.Mutation, Session=Depends(get_db)):
    todo = graphene.Field(lambda: Todo)

    class Arguments:
        title = String(required=True)
        description = String()

    def mutate(self, info, title, description):
        db = get_db()

        todo = TodoModel(title=title, description=description)
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return CreateTodo(todo=todo)


class UpdateTodo(graphene.Mutation, Session=Depends(get_db)):
    todo = graphene.Field(lambda: Todo)

    class Arguments:
        id = ID(required=True)
        title = String()
        description = String()

    def mutate(self, info, id, title=None, description=None):
        db = get_db()
        todo = db.query(TodoModel).filter(TodoModel.id == atob_id(id)).first()
        if not todo:
            raise Exception("Todo not found")
        if title:
            todo.title = title
        if description:
            todo.description = description
        db.commit()
        db.refresh(todo)
        return UpdateTodo(todo=todo)


class DeleteTodo(graphene.Mutation, Session=Depends(get_db)):
    success = graphene.Field(lambda: String)

    class Arguments:
        id = ID(required=True)

    def mutate(self, info, id):
        db = get_db()
        todo = db.query(TodoModel).filter(TodoModel.id == atob_id(id)).first()
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


def atob_id(encoded_string):

    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode("utf-8")
    return decoded_string.split(":")[-1]


def btoa(type, id):
    encoded_bytes = base64.b64encode(f"{type}:{id}".encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string
