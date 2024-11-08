import contextlib
import sqlite3
import sys


DATABASE_URL = 'file:reg.sqlite?mode=rw'

def get_query_stmt_dept_num(classid, cursor):
    stmt_str_dept = "SELECT dept, coursenum "
    stmt_str_dept += "FROM classes, crosslistings "
    stmt_str_dept += "WHERE classid = ? "
    stmt_str_dept += "AND classes.courseid = crosslistings.courseid "
    stmt_str_dept += "ORDER BY dept ASC, coursenum ASC"

    cursor.execute(stmt_str_dept, [classid])
    row = cursor.fetchone()

    temp_arr = []
    while True:
        if row is None:
            break
        temp_arr.append(row[0] + " " + row[1])
        row = cursor.fetchone()
    return temp_arr

def get_query_stmt_course_details(classid, cursor):
    stmt_str_course = "SELECT area, title, descrip, prereqs "
    stmt_str_course += "FROM classes, courses "
    stmt_str_course += "WHERE classid = ? "
    stmt_str_course += "AND classes.courseid = courses.courseid "

    cursor.execute(stmt_str_course, [classid])
    row = cursor.fetchone()

    details_fields = ['Area', 'Title', 'Description', 'Prerequisites']
    temp_dict = {}
    while True:
        if row is None:
            break
        for field, query_result in zip(details_fields, row):
            temp_dict[field] = query_result
        row = cursor.fetchone()

    return temp_dict

def get_query_stmt_prof(classid, cursor):
    stmt_str_prof = "SELECT profname "
    stmt_str_prof += "FROM classes, coursesprofs, profs "
    stmt_str_prof += "WHERE classid = ? "
    stmt_str_prof += "AND classes.courseid = coursesprofs.courseid "
    stmt_str_prof += "AND coursesprofs.profid = profs.profid "

    cursor.execute(stmt_str_prof, [classid])
    row = cursor.fetchone()

    temp_arr = []
    while True:
        if row is None:
            break
        for query_result in row:
            temp_arr.append(query_result)
        row = cursor.fetchone()
    return temp_arr

def main(classid):
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                dept_num = get_query_stmt_dept_num(classid, cursor)
                course_details = get_query_stmt_course_details(
                    classid, cursor)
                profs = get_query_stmt_prof(classid, cursor)
                return dept_num, course_details, profs


    except sqlite3.OperationalError as op_ex:
        raise op_ex
    except sqlite3.DatabaseError as db_ex:
        raise db_ex
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)