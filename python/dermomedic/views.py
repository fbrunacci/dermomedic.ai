"""Views module."""

from flask import request, render_template, abort
from dependency_injector.wiring import Provide
from dermomedic.containers import Container
from dermomedic.encoder import DictEncoder
import json


def analyse_json(id, service=Provide[Container.service]):
    idx = int(id)
    data = service.read_analyse(idx)
    print(f'analyse_json: {data.__dict__}')
    return json.dumps(data.__dict__)


def file_upload(service=Provide[Container.service],
                analyser=Provide[Container.analyser]
                ):
    print(f'file_upload start')
    print(request.files)
    uploaded_file = request.files['image']
    print(f'uploaded filename : {uploaded_file.filename}')
    if uploaded_file.filename != '':
        new_analyse = service.process_analyse(uploaded_file)
        print(f'new_analyse: {new_analyse.__dict__}')
        Container.executor.submit(launch_analyse_thread, new_analyse, analyser)
        return json.dumps(new_analyse.__dict__, cls=DictEncoder)
    else:
        abort(400, description="No image file")


def launch_analyse_thread(analyse, analyser):
    analyser.launch_analyse(analyse)
