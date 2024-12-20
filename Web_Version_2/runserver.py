import sys
import sqlite3
import json
import argparse
import flask

import getcourseoverviews
import getclassdetails
import getcoursedetails

DATABASE_URL = 'file:reg.sqlite?mode=rw'

app = flask.Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return flask.render_template('index.html')

#-----------------------------------------------------------------------

@app.route('/regoverviews', methods=['GET'])
def regoverviews():
    try:
        dept = flask.request.args.get('dept', '')
        coursenum = flask.request.args.get('coursenum', '')
        area = flask.request.args.get('area', '')
        title = flask.request.args.get('title', '')

        overviews_result = getcourseoverviews.main(dept,
                                coursenum, area, title)

        json_doc = json.dumps(overviews_result)
        response = flask.make_response(json_doc)
        response.headers['Content-Type'] = 'application/json'
        return response
    except sqlite3.Error as e:
        print(sys.argv[0] + ":", e, file=sys.stderr)
        err_msg = sys.argv[0] + (": A server error occured. "
        "Please contact the system administrator.")
        out_err_json_doc = [False, err_msg]
        out_err_json_str = json.dumps(out_err_json_doc)
        response = flask.make_response(out_err_json_str)
        response.headers['Content-Type'] = 'application/json'
        return response

#-----------------------------------------------------------------------

@app.route('/regdetails', methods=['GET'])
def regdetails():
    classid = flask.request.args.get('classid', None)

    if classid is None:
        message = 'missing classid'
        out_err_json_doc = [False, message]
        out_err_json_str = json.dumps(out_err_json_doc)
        response = flask.make_response(out_err_json_str)
        response.headers['Content-Type'] = 'application/json'
        return response

    if not classid.isdigit():
        message = 'non-integer classid'
        out_err_json_doc = [False, message]
        out_err_json_str = json.dumps(out_err_json_doc)
        response = flask.make_response(out_err_json_str)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        classid = classid.strip()
        query_to_results = {}
        getclassdetails.main(classid, query_to_results)
        getcoursedetails.main(classid, query_to_results)
        if not query_to_results.get('classid'):
            message = 'no class with classid X exists'
            out_err_json_doc = [False, message]
            out_err_json_str = json.dumps(out_err_json_doc)
            response = flask.make_response(out_err_json_str)
            response.headers['Content-Type'] = 'application/json'
            return response

        details_results = [True, query_to_results]

        out_json_doc = json.dumps(details_results)
        response = flask.make_response(out_json_doc)
        response.headers['Content-Type'] = 'application/json'
        return response

    except sqlite3.Error as e:
        print(sys.argv[0] + ":", e, file=sys.stderr)
        err_msg = sys.argv[0] + (": A server error occured. "
        "Please contact the system administrator.")
        out_err_json_doc = [False, err_msg]
        out_err_json_str = json.dumps(out_err_json_doc)
        response = flask.make_response(out_err_json_str)
        response.headers['Content-Type'] = 'application/json'
        return response

#-----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='The registrar application')
    parser.add_argument('port', type=int,
            help='the port at which the server should listen')
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
