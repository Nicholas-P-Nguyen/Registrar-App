import contextlib
import sqlite3
import sys

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def main(classid):
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                query_to_result = {}
                class_fields = ['Class Id', 'Days',
                        'Start time', 'End time', 'Building', 'Room']

                stmt_str = ("SELECT classid, "
                            " days, starttime, endtime, bldg, "
                            "roomnum, courseid ")
                stmt_str += "FROM classes WHERE classid = ?"

                cursor.execute(stmt_str, [classid])
                row = cursor.fetchone()

                if row is None:
                    return None, None


                course_id = row[6]

                while True:
                    if row is None:
                        break
                    for field, query_result in zip(class_fields, row):
                        query_to_result[field] = query_result
                    row = cursor.fetchone()

                return query_to_result, course_id

    except sqlite3.OperationalError as op_ex:
        raise op_ex
    except sqlite3.DatabaseError as db_ex:
        raise db_ex
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
