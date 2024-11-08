import argparse
import flask
import sys
import sqlite3

import getcourseoverviews

DATABASE_URL = 'file:reg.sqlite?mode=rw'

# TODO: Change template_folder='templates' to '.' when we submit A4.
# Have a template now, so the HTML pages isn't in the way of the .py files
app = flask.Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    try:
        dept = flask.request.args.get('dept', '').strip()
        coursenum = flask.request.args.get('coursenum', '').strip()
        area = flask.request.args.get('area', '').strip()
        title = flask.request.args.get('title', '').strip()

        html_code = flask.render_template(
            'index.html',
            table=getcourseoverviews.main(dept, coursenum, area, title),
            classid='classid',
            dept='dept',
            coursenum='coursenum',
            area='area',
            title='title',
            prev_dept=dept,
            prev_num=coursenum,
            prev_area=area,
            prev_title=title
        )

        response = flask.make_response(html_code)
        response.set_cookie('prev_dept', dept)
        response.set_cookie('prev_coursenum')
        response.set_cookie('prev_area', area)
        response.set_cookie('prev_title', title)

        return response

    except sqlite3.Error as db_ex:
        print(sys.argv[0] + ":", db_ex, file=sys.stderr)
        html_code = flask.render_template(
            'dberror.html'
        )
        response = flask.make_response(html_code)
        return response
    except Exception as ex:
        print(ex, file=sys.stderr)

# @app.route('regoverviews', methods=['GET'])
# def regoverviews():


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