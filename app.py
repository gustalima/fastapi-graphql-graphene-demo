# flask_sqlalchemy/app.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp, make_graphiql_handler

from gql.database import get_db
from gql.schema import schema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.mount("/graphql", GraphQLApp(schema=schema, on_get=make_graphiql_handler()))
