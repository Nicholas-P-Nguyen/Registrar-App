import contextlib
import json
import sqlite3
import argparse
import sys
import textwrap
import socket

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def print_course_details(description):
    description_arr = textwrap.wrap(description, width = 72,
                                    subsequent_indent= f'{' ' * 3}')
    for d in description_arr:
        print(d)

#-----------------------------------------------------------------------

def print_regdetails(query_to_result):
    print('-------------')
    print('Class Details')
    print('-------------')
    class_details = {'Class Id:': 'classid',
                     'Days:' : 'days',
                     'Start time:' : 'starttime',
                     'End time:' : 'endtime',
                     'Building:' : 'bldg',
                     'Room:' : 'roomnum'}

    for column_name, query in class_details.items():
        print(column_name, query_to_result[0][query])

    print('--------------')
    print('Course Details')
    print('--------------')

    print('Course Id:', query_to_result[0]['courseid'])
    print(f'Dept and Number: {query_to_result[0]['dept']} {query_to_result[0]['coursenum']}')

    course_details = {'Area: ' : 'area',
                      'Title: ' : 'title',
                      'Description: ' : 'descrip',
                      'Prerequisites: ' : 'prereqs',
                      'Professor: ' : 'profname'}

    for column_name, query in course_details.items():
        if query_to_result[0][query] == "":
            print(column_name.rstrip())
        elif len(column_name + query_to_result[0][query]) > 72:
            print_course_details(column_name + query_to_result[0][query])
        else:
            print(column_name + query_to_result[0][query])

#-----------------------------------------------------------------------

def fetch_query_stmt_dept_num():
    stmt_str_dept = "SELECT dept, coursenum "
    stmt_str_dept += "FROM classes, crosslistings "
    stmt_str_dept += "WHERE classid = ? "
    stmt_str_dept += "AND classes.courseid = crosslistings.courseid "
    stmt_str_dept += "ORDER BY dept ASC, coursenum ASC"

    return stmt_str_dept

#-----------------------------------------------------------------------

def fetch_query_stmt_course_details():
    stmt_str_course = "SELECT area, title, descrip, prereqs "
    stmt_str_course += "FROM classes, courses "
    stmt_str_course += "WHERE classid = ? "
    stmt_str_course += "AND classes.courseid = courses.courseid "

    return stmt_str_course

#-----------------------------------------------------------------------

def fetch_query_stmt_prof():
    stmt_str_prof = "SELECT profname "
    stmt_str_prof += "FROM classes, coursesprofs, profs "
    stmt_str_prof += "WHERE classid = ? "
    stmt_str_prof += "AND classes.courseid = coursesprofs.courseid "
    stmt_str_prof += "AND coursesprofs.profid = profs.profid "

    return stmt_str_prof

#-----------------------------------------------------------------------

def fetch_query_stmt_class_details():
    stmt_str = ("SELECT classid, days, starttime, endtime, bldg, "
                "roomnum, courseid ")
    stmt_str += "FROM classes WHERE classid = ?"

    return stmt_str

#-----------------------------------------------------------------------

def create_json_doc(classid):
    out_json_doc = ['get_details', classid]
    return out_json_doc

#-----------------------------------------------------------------------

def main():
    try:
        # Help menu
        parser = argparse.ArgumentParser(
            description='Registrar application: show '
                        'details about a class')
        parser.add_argument('host', type=str, help='the computer on which the server is running')
        parser.add_argument('port', type=int, help='the port at which the server is listening')
        parser.add_argument('classid', type=int, help='the id of the class whose details should be shown')
        args = parser.parse_args()

        out_json_doc = create_json_doc(args.classid)
        with socket.socket() as sock:
            sock.connect((args.host, args.port))
            out_flo = sock.makefile(mode='w', encoding='utf-8')
            out_json_str = json.dumps(out_json_doc)
            out_flo.write(out_json_str + '\n')
            out_flo.flush()

            in_flo = sock.makefile(mode='r', encoding='utf-8')
            in_json_str = in_flo.readline()
            in_json_doc = json.loads(in_json_str)
            # Unpacking what the server sent back
            is_success, query_to_result = in_json_doc[0], in_json_doc[1]
            if is_success:
                print_regdetails(query_to_result)

    except sqlite3.OperationalError as op_ex:
        print(sys.argv[0] + ":", op_ex, file=sys.stderr)
        sys.exit(1)
    except sqlite3.DatabaseError as db_ex:
        print(sys.argv[0] + ":", db_ex, file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
