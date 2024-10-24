#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregoverviews.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import os
import sys
import argparse
import time
import threading
import socket

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH
NUMBER_OF_CLIENTS = 100

#-----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description=
        "Test the Registrar's application's handling of " +
        "class overviews requests")
    parser.add_argument('program', metavar='program', type=str,
        help='the client program to run')
    parser.add_argument('host', metavar='host', type=str,
        help='the host on which the server is running')
    parser.add_argument('port', metavar='port', type=int,
        help='the port at which the server is listening')
    args = parser.parse_args()

    return (args.program, args.host, args.port)

#-----------------------------------------------------------------------

def print_flush(message):
    print(message)
    sys.stdout.flush()

#-----------------------------------------------------------------------

def exec_command(program, args):

    print_flush(UNDERLINE)
    command = 'python ' + program + ' ' + args
    print_flush(command)
    exit_status = os.system(command)
    if os.name == 'nt':  # Running on MS Windows?
        print_flush('Exit status = ' + str(exit_status))
    else:
        print_flush('Exit status = ' + str(os.WEXITSTATUS(exit_status)))

def exec_thread_command(program, args, client):
    print_flush(UNDERLINE)
    command = 'python ' + program + ' ' + args
    print_flush(command)
    exit_status = os.system(command)
    if os.name == 'nt':  # Running on MS Windows?
        print_flush('Exit status = ' + str(exit_status))
    else:
        print_flush('Exit status = ' + str(os.WEXITSTATUS(exit_status)))
        print('Exiting child thread number:', client, time.asctime(time.localtime()))

#-----------------------------------------------------------------------

def main():

    program, host, port = parse_args()

    exec_command(program, '-h')

    prefix = host + ' ' + str(port) + ' '

    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')

    print('Starting to spawn child threads!')

    # Testing thread concurrency
    threads = []

    for client in range(NUMBER_OF_CLIENTS):
        thread = threading.Thread(target=exec_thread_command, args=(program, prefix + '-d COS -a qr -n 2 -t intro', client))
        print('Spawn child thread number:', client)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()



#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
