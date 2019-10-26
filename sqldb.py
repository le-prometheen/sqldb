#!/usr/bin/env python3

'''A thin wrapper for basic sqlite3 database interface.

SQLdb is a lightweight, robust class wrapper for simplified SQL syntax and
sqlite3 database interface. Soon to be ported to Postgres.


    BASIC USAGE:

        from sqldb import SqlDb

        CREATE A DATABASE:

            db = SqlDb('DATABASE_NAME.db')

        CREATE A TABLE IN THE DATABASE:

            db.create_table('TABLE_NAME')

        WRITE TO A TABLE:

            db.write(TABLE_NAME, FIELD_NAME(s), *DATA)

        SAVE THE DATA TO THE TABLE:

            db.save_data()

        RETRIEVE DATA:

            result = db.select(TABLE_NAME, FIELD(s) where='ID')

        MAKE CHANGES TO AN EXISTING TABLE:

            db.alter_table(TABLE, ALTER, *ALTERED_DATA):
'''
import json
import sqlite3
from sqlite3 import Error


def flatten(iterable):
    '''Compress a list of nested lists into a single list.
    '''
    for item in iterable:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


class SqlDb:

    """A class wrapper for simplified SQL syntax and database interface.

    METHODS:

        create_table(table_name, columns)

            Creates a table in the database.


        write(table, column, data)

            Writes user data to the specified table in the apporpiate column.


        save_data(self)

            A thin wrapper for sqlite3.commit(). Calling this function
            commits the data and saves the current state of the database.
            Must be called before closing the database.


        query(self, column, table, row_id)

            Retrieves and returns data from the specified table, column and row.


        update_row(self, table, field, primaryID, data)

            Insert into or Update data in a specified field in a specified row and table.


        get_max_id(self, table)

            Returns the highest row ID of the specified table.


        delete_null(self, table, field):

            Removes empty fields from the specified table


        get_tables(self):

            Returns a list of the tables contained within the database
    """
    with open('scripts.json') as file:
        SCRIPTS = json.load(file)

    SCRIPT = '\n'.join(SCRIPTS['dropscript'])


    def __init__(self, filename):

        try:
            self.filename = filename
            self.konnect = sqlite3.connect(filename)
            self.kursor = self.konnect.cursor()

            print(f'\n\tConnected to {self.filename}')
            print('\tSQLite Version:', sqlite3.version)

        except Error as error:
            print(error)


    def create_table(self, table):
        '''Create a new table in the database.

           ARGUMENTS:
               table: dict:
                      Pass in a specially formatted dictionary containing two keys:

                      'name': str: is the name of the table that is being created.

                      'fields': list: is a list of string formatted values representing fields'.

               Example:
                      MY_TABLE = {
                        'name': 'WebPages',
                        'fields': [
                            'URLS TEXT UNIQUE',
                            'HTML TEXT',
                            'TITLE TEXT UNIQUE'
                        ]
                      }

           USAGE:
               Pass in the user created dictionary MY_TABLE:

               create_table(MY_TABLE)

           This method automatically adds an INTEGER PRIMARY KEY ID
           to each table row.
        '''
        try:
            fields = ', '.join(table['fields'])
            self.kursor.execute(f"CREATE TABLE IF NOT EXISTS {table['name']} (id INTEGER PRIMARY KEY, {fields})")

            print(f"\n\tCreated Table: {table['name']}\n")

        except Error as error:
            print(error)


    def get_info(self, table):
        '''Returns a list of tuples containing information
           about each column.
        '''
        self.kursor.execute(f"PRAGMA table_info({table});")
        return self.kursor.fetchall()


    def write(self, table, fields, *data):

        '''Write data to the table into the specified field(s).

           USAGE:
               write('My_Table', 'Field_1, Field_2', data1, data2)

           ARGUMENTS:
                table: str: the table name in string format
                fields: str: a string of comma separated field names
                *data: args: the data objects being passed to each corresponding field.
        '''
        values = ('?, ' * len(data)).strip(', ')
        self.kursor.execute(f'INSERT OR IGNORE INTO {table} ({fields}) VALUES ({values})', tuple(data))


    def update_row(self, table, field, primary_id, data):
        '''Insert into or update data in the specified field
           within the specified row and table.
        '''
        self.kursor.execute(f"UPDATE {table} SET {field}=? WHERE Id={primary_id}", (data,))


    def save_data(self):
        '''Save the data to the datatable.
        '''
        print('\tSaving Data to Table...')
        self.konnect.commit()


    def select(self, table, *columns, **opts):
        '''Query a table or tables and retrieve specified data.

        USAGE:
            Standard Query:
                select('artists', '*', where='ArtistId bewtween 1 and 10')

            Inner Join:
                select('artists', 'Name', 'Title', target='albums', join='inner', key='ArtistId')

            Left Join:
                select('artists', 'Title', 'Name' target='albums', join='left', key='ArtistId')

            Natural Join:
                select('artists', '*', target='albums', join='natural')

            Cross Join:
                select('artists', '*', target='albums', join='cross')

            select('artists', 'Name', 'Title', target='albums', join='inner', key='id', where='id between 1 and 5')

        ARGUMENTS:

            table: str:
            columns: str:

           Optional keyword arguments for join formatting:

               target: str: the name of the table to be joined.

                            Explicit is better than implicit, but if the target table
                            is not specified, the method searches for and retrieves
                            the first table containing the columns declared for joining.

                            That is to say, any column name passed that is not contained
                            within the first table.

                            This may or may not be the appropiate table,
                            so caution is advised, but this fallback is there to
                            shorten the syntax of calling the method by ommiting the
                            target table argument if possible, desired or its declaration
                            forgotten.

               join: str: the type of join
               key: str: the foreign or common key between tables used for joins
               where: str: condition determining row selection
        '''
        prefix = f"SELECT {', '.join(columns)} FROM {table}"
        to_be_joined = [col for col in columns if col not in self.get_columns(table)]

        join_table = opts.get('target', self.select_table(*to_be_joined))
        join_class = opts.get('join', 'null')
        foreign_key = opts.get('key')
        condition = opts.get('where')

        ops = {
            'null': prefix,
            'left': f"{prefix} LEFT JOIN {join_table} USING({foreign_key})",
            'inner': f"{prefix} INNER JOIN {join_table} USING({foreign_key})",
            'cross': f"{prefix} CROSS JOIN {join_table}",
            'natural': f"{prefix} NATURAL JOIN {join_table}",
        }

        if condition:
            selection = ops[join_class] + f' WHERE {condition}'

        else:
            selection = ops[join_class]

        try:
            print(selection)
            self.kursor.execute(selection)
            return  self.kursor.fetchall()

        except Error as error:
            print(error)


    def get_max_id(self, table):
        '''Returns the maximum ID of the table
        '''
        self.kursor.execute(f'SELECT id FROM {table} ORDER BY id DESC LIMIT 1')
        return self.kursor.fetchone()[0]


    def delete_null(self, table, field):
        '''Removes empty fields from the table
        '''
        self.kursor.execute(f'DELETE FROM {table} WHERE {field} IS NULL')


    def get_tables(self):
        '''Returns a list of all tables in the database
        '''
        self.kursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        result = self.kursor.fetchall()
        return list(flatten(result))


    def get_columns(self, table):
        '''Returns a list of column names
        '''
        self.kursor.execute(f'SELECT * FROM {table}')
        columns = [description[0] for description in self.kursor.description]
        return columns


    def select_table(self, *columns):
        '''Find the first table containing all of the specified columns
        '''
        for table in self.get_tables():
            if all(item in self.get_columns(table) for item in columns):
                result = table
                break

        return result


    def drop_column(self, table, column):
        '''Deletes specified column from the specified table.

           SQLite does not support ALTER TABLE DROP COLUMN statement.

           Therefore the workaround is to create a temporary table without the
           column that is to be deleted and copy the data from the old table into
           the corresponding columns of the new table, then delete the old table
           and assign it's name to the new table.

           USAGE:
               This method merely formats and returns the SQL script needed to
               execute the change. It is set up to be executed via the
               alter_table method.
        '''
        info = self.get_info(table)
        columns = ', '.join([item[1] for item in info if item[1] != column])
        syntax = ', '.join([' '.join(item[1:3]) for item in info if item[1] != column])

        return self.SCRIPT.format(syntax, columns, columns, table)



    def rename_column(self, table, column, new_name):
        '''Renames specified column/field within the specified table.

           Different from other database systems, SQLite does not directly
           support the ALTER TABLE RENAME COLUMN statement that allows you
           to rename an existing column of a table.

           Therefore the workaround is to create a new table with the new column
           name and copy the data from the old table into the corresponding columns
           of the new table, then delete the old table and assign it's name to the
           new table.

           USAGE:
               This method merely formats and returns the SQL script needed to
               execute the change. It is set up to be executed via the
               alter_table method.
        '''
        altered_info = []
        info = self.get_info(table)

        for item in self.get_info(table):
            if item[1] == column:
                item = (item[0], new_name) + item[2:]
            altered_info.append(item)

        old_columns = ', '.join([item[1] for item in info])
        new_columns = ', '.join([item[1] for item in altered_info])
        syntax = ', '.join([' '.join(item[1:3]) for item in altered_info])

        return self.SCRIPT.format(syntax, new_columns, old_columns, table)


    def alter_table(self, table, alter, *altered_data):
        '''Make various changes to an existing table.

           ARGUMENTS:
               table: str: the name of the table to be altered.
               alter: str: the method to be executed:

                           alter options:

                           1. rename_table
                           2. add_column
                           3. drop_column
                           4. rename_column

                data: str: the data to be passed to each method of change.
                           the format of each depends upon which method is
                           called. (see usage examples)

            USAGE:
                THE TABLE Customers IS RENAMED Subscribers:

                    alter_table('Customers', 'rename_table', 'Subscribers')

                THE COLUMN OR FIELD zip_code IS ADDED TO THE TABLE Customers:

                    alter_table('Customer', 'add_column', 'zip_code')

                THE COLUMN OR FIELD gender IS DELETED FROM THE TABLE Customers:

                    alter_table('Customer', 'drop_column', 'gender')

                THE COLUMN OR FIELD zip_code IN THE TABLE Customers IS RENAMED postal_code:

                    alter_table('Customer', 'rename_column', 'zip_code', 'postal_code')
        '''

        options = {
            'rename_table': lambda x, y: f"ALTER TABLE {x} RENAME TO {y}",
            'add_column': lambda x, y: f"ALTER TABLE {x} ADD COLUMN {y}",
            'drop_column': self.drop_column,
            'rename_column': self.rename_column
        }

        data = (table,) + altered_data
        self.kursor.executescript(options[alter](*data))


if __name__ == "__main__":

    '''Command Line Syntax:

       python3 SQldb.py DATABASE_NAME -t TABLE_NAME -f LIST OF FIELDS
    '''
    from sqlcmdline import Arguments

    TABLE = {
        'name': Arguments.table,
        'fields': Arguments.fields
    }

    DATABASE = SqlDb(f'{Arguments.filename}.db')
    DATABASE.create_table(TABLE)
