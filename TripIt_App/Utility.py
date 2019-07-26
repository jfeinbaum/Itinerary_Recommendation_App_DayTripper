import mysql.connector
from mysql.connector import errorcode


# Function to establish a connection with the database
def est_connection() -> 'mysql.connector.connection':
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password=' ',
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


# Function to get the pk for a certain entry if it exists
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
    print(result)
    return result


# Function to get the pk of a feature if it exists for this category
#  main_table: name of the table of a category of activity (ex. 'dining')
#  tag_table: name of the join table from category to feature (ex. 'dining_tag')
#  id: name of the id column (ex. 'dining_id')
#  check_col: name of the column to check
#  entry: name of the entry to search for
#  ret_col: name of the column value to return
# Returns the value in ret_col (primary key) or None if it doesn't exist
def get_feature_pk(cursor: 'mysql.connector.connection',
                   main_table: str, tag_table: str, id: str,
                   check_col: str, entry: str or int, ret_col: str) -> int or None:
    # Setup the query using concatenation (%s params are forced to a data type)
    query = "select " + ret_col + \
            " from " + main_table + " join " + tag_table + \
            " using(" + id + ") join feature using(feature_id)" \
            " where " + check_col + "=%s"
    # Single value tuple requires odd format (variable,)
    cursor.execute(query, (entry,))
    # When None is returned, no such entry in the category has the chosen feature
    result = None
    for pk in cursor:
        result = int(str(pk).lstrip('(').rstrip(',)'))
    print(result)
    return result


# Function to get example types to help the user choose
#  cursor: the connection cursor
#  table: name of the category table
#  kind: name of the type attribute (ex. 'dining_type')
# Returns a list of sample types and their frequency
def sample_type(cursor: 'mysql.connector.connection',
                table: str, kind: str) -> list:
    query = "select " + kind + ", count(*)" \
            " from " + table + \
            " group by " + kind + \
            " order by count(*) desc" + \
            " limit 5"
    cursor.execute(query)
    results = []
    for category_type in cursor:
        results.append(category_type)
    return results


# Function to get example features to help the user choose
#  cursor: the connection cursor
#  table: name of the category table
#  tag: name of the join table (ex. 'dining_tag')
#  id: name of the primary key column (ex. 'dining_id')
# Returns a list of sample features and their frequency
def sample_features(cursor: 'mysql.connector.connection',
                    table: str, tag: str, id: str) -> list:
    query = "select feature_name, count(*)" \
            " from " + table + " join " + tag + " using (" + id + ")" + \
            " join feature using(feature_id)" + \
            " group by feature_id" + \
            " order by count(*) desc"
    cursor.execute(query)
    results = []
    for category_type in cursor:
        results.append(category_type)
    # Results list has ALL of the features
    # return smaller_list(results)
