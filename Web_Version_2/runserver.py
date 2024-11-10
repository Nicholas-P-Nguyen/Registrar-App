import argparse
import flask
import sys
import sqlite3
import json

import getcourseoverviews

DATABASE_URL = 'file:reg.sqlite?mode=rw'

app = flask.Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return flask.render_template('index.html')


@app.route('/regoverviews', methods=['GET'])
def regoverviews():
    dept = flask.request.args.get('dept', '').strip()
    coursenum = flask.request.args.get('coursenum', '').strip()
    area = flask.request.args.get('area', '').strip()
    title = flask.request.args.get('title', '').strip()

    overviews_result = getcourseoverviews.main(dept, coursenum, area, title)

    json_doc = json.dumps(overviews_result)
    response = flask.make_response(json_doc)
    response.headers['Content-Type'] = 'application/json'
    return response


def main():
    parser = argparse.ArgumentParser(description='The registrar application')
    parser.add_argument('port', type=int, help='the port at which the server should listen')
    args = parser.parse_args()

    app.config['PORT'] = args.port

    try:
        app.run(host='127.0.0.1', port=args.port, debug=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()