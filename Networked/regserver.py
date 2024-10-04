import argparse
import contextlib
import os
import sqlite3
import sys
import socket
import json
import regoverviews
import regdetails
import threading

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def handle_client(sock):
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                with sock:
                    in_flo = sock.makefile(mode='r', encoding='utf-8')
                    json_str = in_flo.readline()
                    json_doc = json.loads(json_str)
                    print('Received request from client:', json_doc)

                    request, client_input = json_doc[0], json_doc[1]
                    if request == 'get_overviews':
                        get_overviews(cursor, sock, client_input)
                    elif request == 'get_details':
                        get_details(cursor, sock, client_input)

                print('Close socket in child thread')
                print('Exiting child thread')

    except sqlite3.OperationalError as op_ex:
        print(sys.argv[0] + ":", op_ex, file=sys.stderr)
        sys.exit(1)
    except sqlite3.DatabaseError as db_ex:
        print(sys.argv[0] + ":", db_ex, file=sys.stderr)
        sys.exit(1)
    except socket.error as sock_ex:
        out_err_json_doc = [False, str(sock_ex)]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

def create_class_dictionary(out_json_doc, fetched_data, class_fields, cursor):
    while True:
        if fetched_data is None:
            break
        for field, query_result in zip(class_fields, fetched_data):
            out_json_doc[1][0][field] = query_result
        fetched_data = cursor.fetchone()

#-----------------------------------------------------------------------

def get_overviews(cursor, sock, client_input):
    try:
        stmt_str, parameters = regoverviews.process_arguments(client_input.get('dept'), client_input.get('coursenum'), client_input.get('area'), client_input.get('title'))
        cursor.execute(stmt_str, parameters)

        out_json_doc = [True, [{}]]
        fetched_data = cursor.fetchone()
        course_fields = ['classid', 'dept', 'coursenum', 'area', 'title']
        create_class_dictionary(out_json_doc, fetched_data, course_fields, cursor)

        out_json_str = json.dumps(out_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_json_str + '\n')
        out_flo.flush()
        print('Server successfully handled request and sent JSON doc back to client')

    except socket.error as sock_ex:
        out_err_json_doc = [False, str(sock_ex)]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()

#-----------------------------------------------------------------------

def get_details(cursor, sock, classid):
    try:
        out_json_doc = [True, [{}]]

        details_fields = ['classid', 'days', 'starttime', 'endtime', 'bldg', 'roomnum', 'courseid']
        stmt_str_details = regdetails.fetch_query_stmt_class_details()
        cursor.execute(stmt_str_details, [classid])
        row = cursor.fetchone()
        create_class_dictionary(out_json_doc, row, details_fields, cursor)

        details_fields = ['dept', 'coursenum']
        stmt_str_dept = regdetails.fetch_query_stmt_dept_num()
        cursor.execute(stmt_str_dept, [classid])
        row = cursor.fetchone()
        create_class_dictionary(out_json_doc, row, details_fields, cursor)

        details_fields = ['area', 'title', 'descrip', 'prereqs']
        stmt_str_course = regdetails.fetch_query_stmt_course_details()
        cursor.execute(stmt_str_course, [classid])
        row = cursor.fetchone()
        create_class_dictionary(out_json_doc, row, details_fields, cursor)

        details_fields = ['profname']
        stmt_str_prof = regdetails.fetch_query_stmt_prof()
        cursor.execute(stmt_str_prof, [classid])
        row = cursor.fetchone()
        create_class_dictionary(out_json_doc, row, details_fields, cursor)

        out_json_str = json.dumps(out_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_json_str + '\n')
        out_flo.flush()
        print('Server successfully handled request and sent JSON doc back to client')

    except socket.error as sock_ex:
        out_err_json_doc = [False, str(sock_ex)]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()

#-----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Server for the registrar application')
    parser.add_argument('port', type=int, help='the port at which the server should listen')
    args = parser.parse_args()

    server_sock = socket.socket()
    print('Opened server socket')
    if os.name != 'nt':
        server_sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind(('', args.port))
    print('Bound server socket to port number:', args.port)
    server_sock.listen()
    print('Server listening for a connection...')

    while True:
        try:
            sock, client_addr = server_sock.accept()
            print('Accepted connection from Client IP addr and port:', client_addr)
            handle_client_thread = threading.Thread(target=handle_client, args=(sock,))
            print('Spawned child thread')
            handle_client_thread.start()


        except Exception as ex:
            print(ex, file=sys.stderr)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()