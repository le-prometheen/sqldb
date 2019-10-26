# sqldb

SqlDb is a lightweight, robust class wrapper designed to simplify SQL syntax and the sqlite3 
database interface. 

Soon to be ported to Postgres.

## Getting Started:

1. Download or clone this repository

## Create a database using the Commandline:
           
      Merely a convenience to quickly generate a simple table template via the command line. 
      
      The syntax is as follows:
      
      python3 SQldb.py DATABASE_NAME -t TABLE_NAME -f LIST OF FIELDS
      
      ARGUMENTS:
      
          Required:
              Database_Name: Name of Database to be created.
              
          And Example:
              Database.db
              
          Optional:
              -t: The name of the first table to be in the database.
              -f: a list of field names. 
                  
          !!The field/column names must include the column datatypes!!
              
          An Example of the proper column creation syntax:
          
              -f 'FirstName TEXT', Address Text UNIQUE', 'Age Integer'


## Using the Class Wrapper:
     
      from sqldb import SqlDb
      
## Create or connect to an existing database:

      db = SqlDb('database_name.db')

## Create a new table in the database:
      
      db.create_table(table)
      
      ARGUMENTS:
               table: dict:
                      Pass in a specially formatted dictionary containing two keys:

                      'name': str: 
                          is the name of the table that is being created.

                      'fields': list: 
                          is a list of string formatted values representing fields'.

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
           
## Write data into database:

        db.write(table, columns, *data)
        
        USAGE:
            write('My_Table', 'Field_1, Field_2', data1, data2)

           ARGUMENTS:
           
               table: str: 
                   the table name in string format
                   
               fields: str: 
                   a string of comma separated field names 
                   
               *data: args: 
                   the data objects being passed to each corresponding field.
                   
## Query the database:

        db.select(table, *columns, **opts):
        
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
                The name of the table upon which the query is being made.
                
            columns: str:
                The name of each column in string format.

           Optional keyword arguments for join formatting:

              target: str: 
                  the name of the table to be joined.

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

               join: str: 
                   the type of join
                   
               key: str: 
                   the foreign or common key between tables used for joins
                   
               where: str: 
                   condition determining row selection
               
## Make various changes to an existing table:

        db.alter_table(table, alter, *altered_data)
        
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
  
  ## Delete column from a table:
  
          db.drop_column(table, column)
          
           SQLite does not support ALTER TABLE DROP COLUMN statement.

           Therefore the workaround is to create a temporary table without the
           column that is to be deleted and copy the data from the old table into
           the corresponding columns of the new table, then delete the old table
           and assign it's name to the new table.

           USAGE:
               This method merely formats and returns the SQL script needed to
               execute the change. It is set up to be executed via the
               alter_table method.
              
## Rename acolumn/field within a table:

        db.rename_column(table, column, new_name)
        
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
               
For more information @help(SqlDb)
