import contextlib
import sqlite3
import argparse
import sys
import textwrap

DATABASE_URL = 'file:reg.sqlite?mode=rw'
# End of the escape clause -> '\'
ESCAPE = '\'\\\''

WILDCARD_CHARACTERS = {'%', '_'}

def print_table(table):
    for row in table:
        line = (f"{row[0]:>5} {row[1]:>4} {row[2]:>6} "
                f"{row[3]:>4} {row[4]:<}")
        line_arr = textwrap.wrap(line, width = 72,
                                 subsequent_indent= f'{' ' * 23}')
        for l in line_arr:
            print(l)

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

def main():
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                # Help menu
                parser = argparse.ArgumentParser(
                    description='Registrar application: '
                                'show overviews of classes')
                parser.add_argument('-d', type=str,
                                    metavar='dept',
                                    help='show only those classes whose'
                                         ' department contains dept')
                parser.add_argument('-n', type=str,
                                    metavar='num',
                                    help='show only those classes whose'
                                         ' course number contains num')
                parser.add_argument('-a', type=str,
                                    metavar='area',
                                    help='show only those classes whose'
                                         ' distrib area contains area')
                parser.add_argument('-t', type=str,
                                    metavar='title',
                                    help='show only those classes whose'
                                         ' course title contains title')
                args = parser.parse_args()


                stmt_str = ("SELECT classid, dept, coursenum, area,"
                            " title ")
                stmt_str += "FROM courses, classes, crosslistings "
                stmt_str += "WHERE courses.courseid = classes.courseid "
                stmt_str += ("AND courses.courseid ="
                             " crosslistings.courseid ")

                stmt_str, parameters = process_arguments(
                    stmt_str, args.d, args.n, args.a, args.t)

                cursor.execute(stmt_str, parameters)

                print(f"{'ClsId':<5} {'Dept':<4} {'CrsNum':<6} "
                      f"{'Area':<4} {'Title':<5}")
                print(f"{'-' * 5} {'-' * 4} {'-' * 6} "
                      f"{'-' * 4} {'-' * 5}")
                table = cursor.fetchall()
                print_table(table)

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
