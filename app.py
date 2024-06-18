"""
Flask app
"""

from gql_models.schema import my_schema

import logging
import sys
from flask import Flask
from flask_cors import CORS
from graphql_server.flask import GraphQLView


logging.basicConfig(
    stream=sys.stderr,
    format="[%(asctime)s %(name)s:%(levelname)s] %(message)s",
    datefmt="%y/%b/%d %H:%M:%S",
    level=logging.DEBUG,
)

logger = logging.getLogger(name=__name__)
app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return "Hello from my graphql server"


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=my_schema,
        graphiql=True,
    ),
)
