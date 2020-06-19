from flask import Flask

app = Flask(__name__)


@app.route('/<file_name>', methods=['POST', 'GET', 'PUT'])
def hello_world(file_name):
    print("Hello : ", file_name)
    return 'Hello World'


if __name__ == '__main__':
    app.run()
