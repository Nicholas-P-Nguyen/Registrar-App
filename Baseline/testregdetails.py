#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregdetails.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import os
import shutil
import sys

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

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

    if len(sys.argv) != 2:
        print('Usage: ' + sys.argv[0] + ' regdetailsprogram',
            file=sys.stderr)
        sys.exit(1)

    program = sys.argv[1]

    exec_command(program, '8321')
    exec_command(program, '9032')
    exec_command(program, '8293')
    exec_command(program, '9977')
    exec_command(program, '10188')
    exec_command(program, '9012')
    # Testing class ID doesn't exist
    exec_command(program, '01010444')
    exec_command(program, '')
    exec_command(program, '8321 9032')
    exec_command(program, 'abc123')
    exec_command(program, '9032')

    # Testing database if reg.sqlite file doesn't exist
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    os.remove('reg.sqlite')
    exec_command(program, '9012')
    shutil.copy('regbackup.sqlite', 'reg.sqlite')

    # Testing database if its flawed
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    shutil.copy('regflawed.sqlite', 'reg.sqlite')
    exec_command(program, '8321')
    shutil.copy('regbackup.sqlite', 'reg.sqlite')


if __name__ == '__main__':
    main()
