from flask import Flask, abort, request
import main

app = Flask(__name__)


@app.route('/', methods=['POST'])
def elastic_search():
    app.logger.info("{} request received from: {}".format(
        request.method, request.remote_addr))
    if not request.json or 'data' not in request.json:
        app.logger.error("Request has no data or request is not json, aborting")
        abort(400)

        return main(request.json['data'])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)