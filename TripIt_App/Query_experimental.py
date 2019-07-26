# This file is just scratch work
# Figuring out how the connector works
import mysql.connector
from mysql.connector import errorcode


# Try to connect to the database
# Need to create new user according to those credentials below
def test_connect():
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


# Attempt to query some data
def test_query_one_col():
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    # Prepare cursor for query
    cursor = cnx.cursor()
    # Setup the query as SQL syntax in string
    query = "select feature_name from feature"
    # Send the query to the database
    cursor.execute(query)
    # Grab the data using a loop
    for feature_name in cursor:
        print(feature_name)
    # Close the cursor when finished with this one query
    cursor.close()
    # Close the connection when finished with db (i.e. quit app)
    cnx.close()


# Try multicolumn query
def test_query_many_columns():
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    # Prepare cursor for query
    cursor = cnx.cursor()
    # Setup the query as SQL syntax in string
    # LACK OF SPACES WILL CAUSE SQL SYNTAX ERRORS
    query = "select " \
            "dining_name," \
            "dining_type," \
            "rating," \
            "budget " \
            "from dining"
    # Send the query to the database
    cursor.execute(query)
    # Grab the data using a loop: tuple in cursor
    # Opportunity to store this as a list, or create a list of objects
    for dining_name, dining_type, rating, budget in cursor:
        data = str(dining_name).strip() + ' ' + str(dining_type).strip() + ' ' + str(rating) + ' ' + str(budget)
        print(data)
    # Close the cursor when finished with this one query
    cursor.close()
    # Close the connection when finished with db (i.e. quit app)
    cnx.close()


# Try multicolumn query with joins
def test_query_join():
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    # Prepare cursor for query
    cursor = cnx.cursor()
    # Setup the query as SQL syntax in string
    # LACK OF SPACES WILL CAUSE SQL SYNTAX ERRORS
    query = "select " \
            "dining_name," \
            "dining_type," \
            "rating," \
            "budget," \
            "feature_name " \
            "from dining join dining_tag using(dining_id) " \
            "join feature using(feature_id)"
    # Send the query to the database
    cursor.execute(query)
    # Grab the data using a loop: tuple in cursor
    # Opportunity to store this as a list, or create a list of objects
    for dining_name, dining_type, rating, budget, feature_name in cursor:
        data = str(dining_name).strip() + ' ' + str(dining_type).strip() \
               + ' ' + str(rating) + ' ' + str(budget) + ' ' + str(feature_name).strip()
        print(data)
    # Close the cursor when finished with this one query
    cursor.close()
    # Close the connection when finished with db (i.e. quit app)
    cnx.close()


# Attempt to query some data
def test_exist():
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='tripit_demo',
                                      password='',
                                      database='tripit')
        print("Successful connection!")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    # Prepare cursor for query
    cursor = cnx.cursor()
    # Setup the query as SQL syntax in string
    # PROBLEM: cannot set feature_name or feature using the %s method because
    # they are interpreted as having quotes in SQL, which causes error.
    # Must concatenate this information into the query string directly.
    # Parameter method %s only works for things that WOULD HAVE A DATATYPE!
    query = "select feature_name from feature " \
            "where feature_name like %s"
    # Send the query to the database
    cursor.execute(query, ("casual",))
    # Grab the data using a loop
    for feature_name in cursor:
        print(feature_name)
    # Close the cursor when finished with this one query
    cursor.close()
    # Close the connection when finished with db (i.e. quit app)
    cnx.close()

# Try the functions
def main():
    #test_connect()
    #test_query_one_col()
    #test_query_many_columns()
    #test_query_join()
    test_exist()


main()
