import mysql.connector
from mysql.connector import errorcode


# Function to establish a connection with the database
def est_connection() -> 'mysql.connector.connection':
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        # print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        exit(1)
    return cnx


# Function to check if an entry exists in a table
#  table: name of the table to check
#  check_col: name of the column to check
#  entry: name of the entry to search for
#  ret_col: name of the column value to return
# Returns the value in ret_col (primary key) or None if it doesn't exist
def get_pk(cursor: 'mysql.connector.connection',
           table: str, check_col: str, entry: str or int, ret_col: str) -> int or None:
    # Setup the query using concatenation (%s params are forced to a data type)
    query = "select " + ret_col + " from " + table + " where " + check_col + "=%s"
    # Single value tuple requires odd format (variable,)
    cursor.execute(query, (entry,))
    # When None is returned, no such entry exists
    result = None
    for pk in cursor:
        result = int(str(pk).lstrip('(').rstrip(',)'))
    return result
