'''Implementing the regserver.py as specified'''

import argparse
import sys
import flask
import sqlite3

import getcourseoverviews
import getcourseoverviews
import getclassdetails
import getcoursedetails


DATABASE_URL = 'file:reg.sqlite?mode=rw'

#-----------------------------------------------------------------------
# Setting up Flask webpage
#-----------------------------------------------------------------------
app = flask.Flask(__name__, template_folder='.')

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
    
@app.route('/regdetails', methods=['GET'])
def regdetails():
    classid = flask.request.args.get('classid').strip()
    if not classid.isdigit():
        html_code = flask.render_template(
            'nonintclassid.html'
        )
        response = flask.make_response(html_code)
        return response
    try:
        class_details, course_id = getclassdetails.main(classid)
        if class_details is None and course_id is None:
            html_code = flask.render_template(
                'nonexistingclassid.html',
                class_id=classid
            )
            response = flask.make_response(html_code)
            return response


        dept_num, course_details, profs = getcoursedetails.main(classid)
        

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
    
    except sqlite3.Error as db_ex:
        print(sys.argv[0] + ":", db_ex, file=sys.stderr)
        html_code = flask.render_template(
            'dberror.html'
        )
        response = flask.make_response(html_code)
        return response
    except Exception as ex:
        print(ex, file=sys.stderr)


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

