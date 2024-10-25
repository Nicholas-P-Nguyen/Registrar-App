import contextlib
import sqlite3
import argparse
import sys
import textwrap

DATABASE_URL = 'file:reg.sqlite?mode=rw'
# End of the escape clause -> '\'
ESCAPE = '\'\\\''

def create_overview_dict(row, cursor):
    output = []
    course_fields = ['classid', 'dept', 'coursenum',
                    'area', 'title']
    while True:
        if row is None:
            break
        temp_dict = {}
        for field, query_result in zip(course_fields, row):
            temp_dict[field] = query_result
        output.append(temp_dict)
        row = cursor.fetchone()
    return output

#-----------------------------------------------------------------------

def process_arguments(stmt_str, dept=None, num=None,
                      area=None, title=None):
    parameters = []
    if dept:
        stmt_str += "AND dept LIKE ? "
        parameters.append('%' + dept + '%')

    if area:
        stmt_str += "AND area LIKE ? "
        parameters.append('%' + area + '%')

    if num:
        stmt_str += "AND coursenum LIKE ? "
        parameters.append('%' + num + '%')

    if title:
        stmt_str += f"AND title LIKE ? ESCAPE {ESCAPE} "
        parameters.append('%' + title + '%')

    stmt_str += "ORDER BY dept ASC, coursenum ASC"
    return stmt_str, parameters

#-----------------------------------------------------------------------

def main():
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                stmt_str = ("SELECT classid, dept, coursenum, area,"
                            " title ")
                stmt_str += "FROM courses, classes, crosslistings "
                stmt_str += "WHERE courses.courseid = classes.courseid "
                stmt_str += ("AND courses.courseid ="
                             " crosslistings.courseid ")

                stmt_str, parameters = process_arguments(
                    stmt_str, None, None, None, None)

                cursor.execute(stmt_str, parameters)

                row = cursor.fetchone()
                return create_overview_dict(row, cursor)

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
