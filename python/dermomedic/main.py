from dermomedic import application
from dermomedic.containers import Container

print('run create app')
app = application.create_app()

if __name__ == '__main__':
    print('main start')
    app.run(host="0.0.0.0", port=int("8080"), debug=True, use_reloader=False)
