
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
    html_code = flask.render_template('index.html', 
                                      table = courseoverviews.main(None, None, None, None),
                                      classid='classid',
                                      dept='dept',
                                      coursenum='coursenum',
                                      area='area',
                                      title='title')
    
    response = flask.make_response(html_code)
    return response

@app.route('/regdetails/<classid>')
def regdetails(classid):
    class_details, course_id = classdetails.main(classid)
    dept_num, course_details, profs = coursedetails.main(classid)


    html_code = flask.render_template('regdetails.html',
                                      classdetails=class_details,
                                      courseid=course_id,
                                      deptnum=dept_num,
                                      coursedetails=course_details,
                                      profs=profs)
    response = flask.make_response(html_code)
    return response

@app.route('/searchform', methods=['GET'])
def search_form():
    prev_dept = flask.request.cookies.get('prev_dept')
 
    prev_num = flask.request.cookies.get('prev_coursenum')

    prev_area = flask.request.cookies.get('prev_area')

    prev_title = flask.request.cookies.get('prev_title')

    html_code = flask.render_template('searchform.html',
                                      prev_dept=prev_dept,
                                      prev_num=prev_num,
                                      prev_area=prev_area,
                                      prev_title=prev_title)
    response = flask.make_response(html_code)
    return response

@app.route('/searchresults', methods=['GET'])
def searchresults():
    dept = flask.request.args.get('dept')
    if dept is None:
        dept = ''
    dept = dept.strip()

    if dept == '':
        prev_dept = ''
    else:
        prev_dept = dept

    coursenum = flask.request.args.get('coursenum')
    if coursenum is None:
        coursenum = ''
    coursenum = coursenum.strip()

    if coursenum == '':
        prev_num = ''
    else:
        prev_num = coursenum

    area = flask.request.args.get('area')
    if area is None:
        prev_area = ''
    area = area.strip()

    if area == '':
        prev_area = ''
    else:
        prev_area = area

    title = flask.request.args.get('title')
    if title is None:
        prev_title = ''
    title = title.strip()

    if title == '':
        prev_title = ''
    else:
        prev_title = title

    html_code = flask.render_template('searchresults.html',
                                      table = courseoverviews.main(prev_dept, prev_num, prev_area, prev_title),
                                      classid='classid',
                                      dept=prev_dept,
                                      coursenum=prev_num,
                                      area=prev_area,
                                      title=prev_title)
    response = flask.make_response(html_code)
    response.set_cookie('prev_dept', prev_dept, max_age=60*60*24)
    response.set_cookie('prev_coursenum', prev_num, max_age=60*60*24)
    response.set_cookie('prev_area', prev_area, max_age=60*60*24)
    response.set_cookie('prev_title', prev_title, max_age=60*60*24)

    print(f"Setting Cookies: dept={prev_dept}, coursenum={prev_num}, area={prev_area}, title={prev_title}")

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
