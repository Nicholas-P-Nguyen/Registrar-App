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
# import dotenv
import time

DATABASE_URL = 'file:reg.sqlite?mode=rw'

def handle_client(sock):
    # dotenv.load_dotenv()
    #
    # IODELAY = os.environ.get('IODELAY', 0)
    # CDELAY = os.environ.get('CDELAY', 0)
    #
    # print("DELAY = ", IODELAY)
    #
    # time.sleep(IODELAY)
    # time.sleep(CDELAY)

    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
                             uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                with sock:
                    in_flo = sock.makefile(mode='r', encoding='utf-8')
                    in_json_str = in_flo.readline()
                    in_json_doc = json.loads(in_json_str)
                    print('Received request from client:', in_json_doc)

                    request, client_input = in_json_doc[0], in_json_doc[1]
                    if request == 'get_overviews':
                        get_overviews(cursor, sock, client_input)
                    elif request == 'get_details':
                        get_details(cursor, sock, client_input)

                print('Close socket in child thread')
                print('Exiting child thread')

    except sqlite3.Error as e:
        err_msg = sys.argv[0] + ": A server error occurred. Please contact the system administrator."
        out_err_json_doc = [False, err_msg]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()
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
# get_overviews(): Processes clients request and sends back a json doc
# create_overviews_dictionary(): Helper function to format dictionary to
#                                return to client
#-----------------------------------------------------------------------
def create_overviews_dictionary(out_json_doc, fetched_data, class_fields, cursor):
    while True:
        if fetched_data is None:
            break
        temp_dict = {}
        for field, query_result in zip(class_fields, fetched_data):
            temp_dict[field] = query_result
        out_json_doc[1].append(temp_dict)
        fetched_data = cursor.fetchone()

def get_overviews(cursor, sock, client_input):
    try:
        stmt_str, parameters = regoverviews.get_query_stmt(
            client_input.get('dept'), client_input.get('coursenum'),
            client_input.get('area'), client_input.get('title'))

        cursor.execute(stmt_str, parameters)

        out_json_doc = [True, []]
        fetched_data = cursor.fetchone()
        course_fields = ['classid', 'dept', 'coursenum', 'area', 'title']
        create_overviews_dictionary(out_json_doc, fetched_data,
                                     course_fields, cursor)
        print(out_json_doc)
        out_json_str = json.dumps(out_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_json_str + '\n')
        out_flo.flush()
        print('Server successfully handled request and sent JSON doc '
              'back to client')

    except socket.error as sock_ex:
        out_err_json_doc = [False, str(sock_ex)]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()

#-----------------------------------------------------------------------
# get_details(): Processes clients request and sends back a json doc
# put_details(): Helper to puts class details into hashmap
# put_dept_coursenum(): Helper to puts dept and coursenum into a list
#                       and append to hashmap
# put_prof_name(): Helper to put profs name into a list and append
#                  to hashmap
#-----------------------------------------------------------------------
def put_details(query_to_result, row, details_fields, cursor):
    while True:
        if row is None:
            break
        for field, query_result in zip(details_fields, row):
            query_to_result[field] = query_result
        row = cursor.fetchone()

def put_dept_coursenum(query_to_result, row, cursor):
    temp_arr = []
    while True:
        if row is None:
            break
        temp_dict = {'dept': row[0], 'coursenum': row[1]}
        temp_arr.append(temp_dict)
        row = cursor.fetchone()

    query_to_result['deptcoursenums'] = temp_arr

def put_prof_name(query_to_result, row, cursor):
    temp_arr = []
    while True:
        if row is None:
            break
        for query_result in row:
            temp_arr.append(query_result)
        row = cursor.fetchone()
    query_to_result['profnames'] = temp_arr

#-----------------------------------------------------------------------

def get_details(cursor, sock, classid):
    try:
        out_json_doc = [True]
        query_to_result = {}

        details_fields = ['classid', 'days', 'starttime', 'endtime', 'bldg', 'roomnum', 'courseid']
        stmt_str_details = regdetails.get_query_stmt_class_details()
        cursor.execute(stmt_str_details, [classid])
        row = cursor.fetchone()
        put_details(query_to_result, row, details_fields, cursor)

        stmt_str_dept = regdetails.get_query_stmt_dept_num()
        cursor.execute(stmt_str_dept, [classid])
        row = cursor.fetchone()
        put_dept_coursenum(query_to_result, row, cursor)

        details_fields = ['area', 'title', 'descrip', 'prereqs']
        stmt_str_course = regdetails.get_query_stmt_course_details()
        cursor.execute(stmt_str_course, [classid])
        row = cursor.fetchone()
        put_details(query_to_result, row, details_fields, cursor)

        stmt_str_prof = regdetails.get_query_stmt_prof()
        cursor.execute(stmt_str_prof, [classid])
        row = cursor.fetchone()
        put_prof_name(query_to_result, row, cursor)

        out_json_doc.append(query_to_result)

        out_json_str = json.dumps(out_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_json_str + '\n')
        out_flo.flush()
        print(out_json_doc)
        print('Server successfully handled request and sent JSON doc back to client')

    except socket.error as sock_ex:
        out_err_json_doc = [False, str(sock_ex)]
        out_err_json_str = json.dumps(out_err_json_doc)
        out_flo = sock.makefile(mode='w', encoding='utf-8')
        out_flo.write(out_err_json_str + '\n')
        out_flo.flush()

#-----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Server for the '
                                     'registrar application')
    parser.add_argument('port', type=int, help='the port'
                        ' at which the server should listen')
    args = parser.parse_args()

    server_sock = socket.socket()
    print('Opened server socket')
    if os.name != 'nt':
        server_sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_sock.bind(('', args.port))
        print('Bound server socket to port number:', args.port)
        server_sock.listen()
        print('Server listening for a connection...')
    except OSError as e:
        print(sys.argv[0] + ":", e, file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            sock, client_addr = server_sock.accept()
            print('Accepted connection from Client IP addr and port:',
                  client_addr)

            handle_client_thread = threading.Thread(
                target=handle_client, args=(sock,))

            print('Spawned child thread')
            handle_client_thread.start()


        except Exception as ex:
            print(ex, file=sys.stderr)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()