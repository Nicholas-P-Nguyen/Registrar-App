import contextlib
import sqlite3
import argparse
import sys
import textwrap

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def print_course_details(description):
    description_arr = textwrap.wrap(description, width = 72,
                                    subsequent_indent= f'{' ' * 3}')
    for d in description_arr:
        print(d)

#-----------------------------------------------------------------------

def get_course_dept_and_num(class_id, cursor):
    stmt_str_dept = "SELECT dept, coursenum "
    stmt_str_dept += "FROM classes, crosslistings "
    stmt_str_dept += "WHERE classid = ? "
    stmt_str_dept += "AND classes.courseid = crosslistings.courseid "
    stmt_str_dept += "ORDER BY dept ASC, coursenum ASC"

    cursor.execute(stmt_str_dept, [class_id])
    table = cursor.fetchall()
    for row in table:
        print(f'Dept and Number: {row[0]} {row[1]}')

#-----------------------------------------------------------------------

def get_course_details(class_id, cursor):
    stmt_str_course = "SELECT area, title, descrip, prereqs "
    stmt_str_course += "FROM classes, courses "
    stmt_str_course += "WHERE classid = ? "
    stmt_str_course += "AND classes.courseid = courses.courseid "

    course_fields = ['Area: ', 'Title: ', 'Description: ',
                     'Prerequisites: ']
    course_fields_no_space = ['Area:', 'Title:', 'Description:',
                              'Prerequisites:']
    cursor.execute(stmt_str_course, [class_id])
    row = cursor.fetchone()

    for i, _ in enumerate(row):
        if row[i] == "":
            print(course_fields_no_space[i])
        elif len(course_fields[i] + row[i]) > 72:
            print_course_details(course_fields[i] + row[i])
        else:
            print(course_fields[i] + row[i])

#-----------------------------------------------------------------------

def get_course_profs(class_id, cursor):
    stmt_str_prof = "SELECT profname "
    stmt_str_prof += "FROM classes, coursesprofs, profs "
    stmt_str_prof += "WHERE classid = ? "
    stmt_str_prof += "AND classes.courseid = coursesprofs.courseid "
    stmt_str_prof += "AND coursesprofs.profid = profs.profid "

    cursor.execute(stmt_str_prof, [class_id])
    table = cursor.fetchall()

    for row in table:
        print(f'Professor: {row[0]}')

#-----------------------------------------------------------------------

def get_class_details(class_id, cursor):
    stmt_str = ("SELECT classid, days, starttime, endtime, bldg, "
                "roomnum, courseid ")
    stmt_str += "FROM classes WHERE classid = ?"

    cursor.execute(stmt_str, [class_id])
    row = cursor.fetchone()

    if row is None:
        print(f"{sys.argv[0]}: no class with classid "
              f"{class_id} exists", file=sys.stderr)
        sys.exit(1)

    print('-------------')
    print('Class Details')
    print('-------------')

    class_fields = ['Class Id:', 'Days:', 'Start time:', 'End time:',
                    'Building:', 'Room:']

    for field, value in zip(class_fields, row):
        print(field, value)

    print('--------------')
    print('Course Details')
    print('--------------')
    print('Course Id:', row[6])

#-----------------------------------------------------------------------

def main():
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                # Help menu
                parser = argparse.ArgumentParser(
                    description='Registrar application: show '
                                'details about a class')
                parser.add_argument('classid', type=int,
                                    help='the id of the class whose '
                                         'details should be shown')
                args = parser.parse_args()

                get_class_details(args.classid, cursor)
                get_course_dept_and_num(args.classid, cursor)
                get_course_details(args.classid, cursor)
                get_course_profs(args.classid, cursor)

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
