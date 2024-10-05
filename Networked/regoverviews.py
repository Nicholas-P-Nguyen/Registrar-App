import json
import argparse
import sys
import textwrap
import socket

DATABASE_URL = 'file:reg.sqlite?mode=rw'
# End of the escape clause -> '\'
ESCAPE = '\'\\\''

WILDCARD_CHARACTERS = {'%', '_'}

def print_table(course_overview_maps):
    print(f"{'ClsId':<5} {'Dept':<4} {'CrsNum':<6} "
          f"{'Area':<4} {'Title':<5}")
    print(f"{'-' * 5} {'-' * 4} {'-' * 6} "
          f"{'-' * 4} {'-' * 5}")
    for overview_map in course_overview_maps:
        line = (f"{overview_map.get('classid'):>5} {overview_map.get('dept'):>4} {overview_map.get('coursenum'):>6} "
                f"{overview_map.get('area'):>4} {overview_map.get('title'):<}")
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

def get_query_stmt(dept=None, num=None, area=None, title=None):
    stmt_str = ("SELECT classid, dept, coursenum, area,"
                " title ")
    stmt_str += "FROM courses, classes, crosslistings "
    stmt_str += "WHERE courses.courseid = classes.courseid "
    stmt_str += ("AND courses.courseid ="
                 " crosslistings.courseid ")

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

def create_jsondoc(dept, coursenum, area, title):
    class_fields = ['dept', 'coursenum', 'area', 'title']
    user_inputs = [dept, coursenum, area, title]
    out_json_doc = ['get_overviews']

    course_query_map = {}
    for field, user_input in zip(class_fields, user_inputs):
        course_query_map[field] = user_input

    out_json_doc.append(course_query_map)

    return out_json_doc

def main():
    try:
        # Help menu
        parser = argparse.ArgumentParser(
            description='Registrar application: '
                        'show overviews of classes')
        parser.add_argument('host', type=str, help='the computer on which the server is running')
        parser.add_argument('port', type=int, help='the port at which the server is listening')
        parser.add_argument('-d', type=str, metavar='dept', help='show only those classes whose department contains dept')
        parser.add_argument('-n', type=str, metavar='num', help='show only those classes whose course number contains num')
        parser.add_argument('-a', type=str, metavar='area', help='show only those classes whose distrib area contains area')
        parser.add_argument('-t', type=str, metavar='title', help='show only those classes whose course title contains title')

        args = parser.parse_args()

        out_json_doc = create_jsondoc(args.d, args.n, args.a, args.t)
        with socket.socket() as sock:
            try:
                sock.connect((args.host, args.port))
            except Exception as e:
                print(sys.argv[0] + ':', e)
                sys.exit(1)

            out_flo = sock.makefile(mode='w', encoding='utf-8')
            out_json_str = json.dumps(out_json_doc)
            out_flo.write(out_json_str + '\n')
            out_flo.flush()

            in_flo = sock.makefile(mode='r', encoding='utf-8')
            in_json_str = in_flo.readline()
            in_json_doc = json.loads(in_json_str)
            # Unpacking what the server sent back
            is_success, course_overview_maps = in_json_doc[0], in_json_doc[1]

            if is_success:
                print_table(course_overview_maps)
            else:
                print(sys.argv[0] + ":", course_overview_maps)
                sys.exit(1)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()