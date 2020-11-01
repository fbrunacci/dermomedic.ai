from flask import Flask, request, abort
from flask_injector import FlaskInjector
from flask_executor import Executor
from injector import inject, Module, singleton, provider
from flaskd.dependencies import configure
from dermomedic.service import IService
from dermomedic.analyser import IAnalyser
from dermomedic.encoder import DictEncoder
import json


def create_app():
    app = Flask(__name__)
    with app.app_context():
        print(f"app_context start")
    return app


app = create_app()
executor = Executor(app)
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 1


@inject
@app.route('/analyse/json/<id>')
def analyse_json(id, service: IService):
    idx = int(id)
    data = service.read_analyse(idx)
    response = app.response_class(
        response=json.dumps(data.__dict__),
        status=200,
        mimetype='application/json'
    )
    return response


@inject
@app.route('/upload', methods=['POST'])
def file_upload(service: IService, analyser: IAnalyser):
    print(f'file_upload start')
    print(request.files)
    uploaded_file = request.files['image']
    print(f'uploaded filename : {uploaded_file.filename}')
    if uploaded_file.filename != '':
        new_analyse = service.process_analyse(uploaded_file)
        executor.submit(launch_analyse_thread, analyser)
        response = app.response_class(
            response=json.dumps(new_analyse, cls=DictEncoder),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        abort(400, description="No image file")


def launch_analyse_thread(analyser: IAnalyser):
    analyser.launch_analyse(analyser)


flask_injector = FlaskInjector(app=app, modules=[configure])

if __name__ == '__main__':
    analyser = flask_injector.injector.get(IAnalyser)
    app.run(host="0.0.0.0", port=int("8080"), debug=True, use_reloader=False)
