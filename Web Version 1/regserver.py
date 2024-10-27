
'''Implementing the regserver.py as specified'''

import argparse
import contextlib
import os
import sqlite3
import sys
import socket
import json
import threading
import time
import flask

import courseoverviews
import courseoverviews
import classdetails
import coursedetails


#-----------------------------------------------------------------------
# Global Variables
#-----------------------------------------------------------------------
IODELAY = int(os.environ.get('IODELAY', 0))
CDELAY = int(os.environ.get('CDELAY', 0))
DATABASE_URL = 'file:reg.sqlite?mode=rw'

#-----------------------------------------------------------------------
# Setting up Flask webpage
#-----------------------------------------------------------------------
app = flask.Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    dept = flask.request.args.get('dept', '').strip()
    coursenum = flask.request.args.get('coursenum', '').strip()
    area = flask.request.args.get('area', '').strip()
    title = flask.request.args.get('title', '').strip()

    html_code = flask.render_template(
        'index.html',
        table=courseoverviews.main(dept, coursenum, area, title),
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
    response.set_cookie('prev_dept', dept, max_age=60*60*24)
    response.set_cookie('prev_coursenum', coursenum, max_age=60*60*24)
    response.set_cookie('prev_area', area, max_age=60*60*24)
    response.set_cookie('prev_title', title, max_age=60*60*24)
    
    return response


@app.route('/regdetails/<classid>')
def regdetails(classid):
    class_details, course_id = classdetails.main(classid)
    dept_num, course_details, profs = coursedetails.main(classid)
    
    prev_dept = flask.request.cookies.get('prev_dept', '')
    prev_coursenum = flask.request.cookies.get('prev_coursenum', '')
    prev_area = flask.request.cookies.get('prev_area', '')
    prev_title = flask.request.cookies.get('prev_title', '')

    
    html_code = flask.render_template(
        'regdetails.html',
        classdetails=class_details,
        courseid=course_id,
        deptnum=dept_num,
        coursedetails=course_details,
        profs=profs,
        prev_dept=prev_dept,
        prev_coursenum=prev_coursenum,
        prev_area=prev_area,
        prev_title=prev_title
    )
    
    response = flask.make_response(html_code)
    return response


def main():
    parser = argparse.ArgumentParser(description='Server for the '
                                     'registrar application')
    parser.add_argument('port', type=int, help='the port'
                        ' at which the server should listen')
    args = parser.parse_args()

    try:
        app.run(host='127.0.0.1', port=args.port, debug=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
