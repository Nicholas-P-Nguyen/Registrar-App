import contextlib
import sqlite3
import sys

DATABASE_URL = 'file:reg.sqlite?mode=rw'
# End of the escape clause -> '\'
ESCAPE = '\'\\\''
WILDCARD_CHARACTERS = {'%', '_'}

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

def get_escaped_title(title):
    new_title = ''
    for char in title:
        if char in WILDCARD_CHARACTERS:
            new_title += f'\\{char}'
        else:
            new_title += char
    return new_title

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
        if '_' in title or '%' in title:
            new_title = get_escaped_title(title)
            parameters.append('%' + new_title + '%')
        else:
            parameters.append('%' + title + '%')

    stmt_str += "ORDER BY dept ASC, coursenum ASC"
    return stmt_str, parameters

#-----------------------------------------------------------------------

def main(dept, num, area, title):
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
                    stmt_str, dept, num, area, title)

                cursor.execute(stmt_str, parameters)

                row = cursor.fetchone()  
                return create_overview_dict(row, cursor)

    except sqlite3.OperationalError as op_ex:
        raise op_ex
    except sqlite3.DatabaseError as db_ex:
        raise db_ex
    except Exception as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
