#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3

'''Argument formatting for database creation using the commandline.
'''

import argparse

'''ARGUMENTS:
       Create the database and table:

           database = database_name
           -t -table = table_name
           -f -fields = list_of_field_names
'''

PARSE = argparse.ArgumentParser(description='SQL Database Creator')
PARSE.add_argument('filename', metavar='Name of Database', help='Name of Database')
PARSE.add_argument('--table', '-t', metavar='Create Table', help='Name of Table')
PARSE.add_argument('--fields', '-f', metavar='Create Field(s)', nargs='*', help='List of Fields')

Arguments = PARSE.parse_args()
