#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregoverviews.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import os
import shutil
import sys
import argparse

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

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


#-----------------------------------------------------------------------

def main():

    program, host, port = parse_args()

    exec_command(program, '-h')

    prefix = host + ' ' + str(port) + ' '

    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')
    # Testing subsets of 4
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')

    # Testing subsets of 3
    exec_command(program, prefix + '-d COS -n 2 -a qr')
    exec_command(program, prefix + '-d COS -n 2 -t intro')
    exec_command(program, prefix + '-d COS -a qr -t intro')
    exec_command(program, prefix + '-n 2 -a qr -t intro')

    # Testing subsets of 2
    exec_command(program, prefix + '-d COS -n 2')
    exec_command(program, prefix + '-d COS -a qr')
    exec_command(program, prefix + '-d COS -t intro')
    exec_command(program, prefix + '-n 2 -a qr')
    exec_command(program, prefix + '-n 2 -t intro')
    exec_command(program, prefix + '-a qr -t intro')

    # Testing subsets of 1
    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-a qr')
    exec_command(program, prefix + '-t intro')
    exec_command(program, prefix + '-n 2')

    # Testing wildcard characters
    exec_command(program, prefix + '-t c%S')
    exec_command(program, prefix + '-t C_S')

    exec_command(program, prefix + 'a qr')
    exec_command(program, prefix + '-A qr')
    exec_command(program, prefix + '"-a " qr')
    exec_command(program, prefix + '-a qr st')
    exec_command(program, prefix + '-a')
    exec_command(program, prefix + '-a qr -d')
    exec_command(program, prefix + '-a -d cos')
    exec_command(program, prefix + '-x')

    # Testing database if reg.sqlite file doesn't exist
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    os.remove('reg.sqlite')

    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')

    shutil.copy('regbackup.sqlite', 'reg.sqlite')

    # Testing database if its flawed
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    shutil.copy('regflawed.sqlite', 'reg.sqlite')

    exec_command(program, prefix + '-d COS')
    exec_command(program, prefix + '-d COS -a qr -n 2 -t intro')

    shutil.copy('regbackup.sqlite', 'reg.sqlite')
    print('finished testing')



#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
