import argparse
import contextlib
import os
import sqlite3
import sys
import socket
import json
import regoverviews

DATABASE_URL = 'file:reg.sqlite?mode=rw'

'''
Client sends a list containing a string and a hashmap 
    string: 'get_overviews'
    hashmap: key = dept, coursenum, area, title
             value = user input e.g., COS, 2, qr, intro
             
RETURNS a JSON document list containing a boolean and a hashmap
    boolean: True if successful
    hashmap: key = classid, dept, coursenum, area, title
             value = course details
'''
def handle_client(cursor, sock):
    in_flo = sock.makefile(mode='r', encoding='utf-8')
    json_str = in_flo.readline()
    json_doc = json.loads(json_str)

    action = json_doc[0]
    client_input = json_doc[1]
    if action == 'get_overviews':
        get_overviews(cursor, sock, client_input)
    else:
        get_details(cursor, sock, client_input)

#-----------------------------------------------------------------------

def get_overviews(cursor, sock, client_input):
    stmt_str = ("SELECT classid, dept, coursenum, area,"
                " title ")
    stmt_str += "FROM courses, classes, crosslistings "
    stmt_str += "WHERE courses.courseid = classes.courseid "
    stmt_str += ("AND courses.courseid ="
                 " crosslistings.courseid ")


    stmt_str, parameters = regoverviews.process_arguments(stmt_str,
        client_input.get('dept', None), client_input.get('coursenum', None),
        client_input.get('area', None), client_input.get('title', None))

    cursor.execute(stmt_str, parameters)

    course_fields = ['classid', 'dept', 'coursenum', 'area', 'title']
    # TODO: If server did not handle request successfully return False & error message
    out_json_doc = [True]
    row = cursor.fetchone()
    while True:
        if row is None:
            break
        temp = {}
        for field, value in zip(course_fields, row):
            temp[field] = value
        out_json_doc.append(temp)
        row = cursor.fetchone()

    out_json_str = json.dumps(out_json_doc)
    out_flo = sock.makefile(mode='w', encoding='utf-8')
    out_flo.write(out_json_str + '\n')
    out_flo.flush()


def get_details(cursor, sock, client_input):
    pass


def main():
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                parser = argparse.ArgumentParser(description='Server for the registrar application')
                parser.add_argument('port', type=int, help='the port at which the server should listen')
                args = parser.parse_args()

                server_sock = socket.socket()
                print('Opened server socket')
                if os.name != 'nt':
                    server_sock.setsockopt(
                        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                server_sock.bind(('', args.port))
                print(f'Bound server socket to port number:', args.port)
                server_sock.listen()
                print('Server listening for a connection...')

                while True:
                    try:
                        sock, client_addr = server_sock.accept()
                        with sock:
                            print('Accepted connection from Client IP addr and port:', client_addr)
                            print('Server IP addr and port:', sock.getsockname())
                            handle_client(cursor, sock)

                    except Exception as ex:
                        print(ex, file=sys.stderr)



    except sqlite3.OperationalError as op_ex:
        print(sys.argv[0] + ":", op_ex, file=sys.stderr)
        sys.exit(1)
    except sqlite3.DatabaseError as db_ex:
        print(sys.argv[0] + ":", db_ex, file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()