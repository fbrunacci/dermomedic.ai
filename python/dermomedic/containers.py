"""Containers module."""

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from dermomedic import service, database, analyser, neuralnet


class Container(containers.DeclarativeContainer):
    executor = None

    print('Container init')
    config = providers.Configuration()
    print(config.github.request_timeout())

    database = providers.Singleton(
        database.FSDatabase,
        upload_dir=config.database.dir
    )

    service = providers.Singleton(
        service.DermomedicService,
        db=database
    )

    neural_net = providers.Singleton(
        neuralnet.Masdevallia,
        model_file=config.neuralnet.model
    )

    analyser = providers.Singleton(
        analyser.Analyser,
        db=database,
        neural_net=neural_net
    )
