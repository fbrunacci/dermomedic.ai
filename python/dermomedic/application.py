"""Application module."""
from dependency_injector.wiring import Provide
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_executor import Executor
from dermomedic.containers import Container
from dermomedic import views


def create_app() -> Flask:
    app = Flask(__name__)
    container = Container()
    container.config.from_yaml('config.yml')
    container.config.github.auth_token.from_env('GITHUB_TOKEN')
    Container.executor = Executor(app)
    container.wire(modules=[views])

    app.container = container
    app.add_url_rule('/analyse/json/<id>', 'analyse', views.analyse_json)
    app.add_url_rule('/upload', 'upload', views.file_upload, methods=['POST'])

    bootstrap = Bootstrap()
    bootstrap.init_app(app)

    # preload neural_net
    app.container.neural_net()

    return app
