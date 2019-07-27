import mysql.connector
from mysql.connector import errorcode
import random
import math


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
    smaller_list = []
    for i in range(5):
        x = random.randint(1, len(results))
        smaller_list.append(results[x])
    return smaller_list


# Function to recommend an activity
def recommend_activity(cursor: 'mysql.connector.connection',
                       table: str, title: str, kind: str,
                       types: list, features: list, amount: int, budget=None) -> list:
    # Setup the query
    query = ""
    if budget is not None:
        query += "select " + title + ", " + kind + ", rating, budget, description" + \
                " from " + table + " "
    else:
        query += "select " + title + ", " + kind + ", rating, description" + \
                " from " + table + " "
    # Generate the where clause: budget, then types, then features
    # The where clause may or may not be included depending on the user's answers
    where = "where "
    # Data will be a list parameters (%s) for the sql query, convert to tuple before using
    data = []
    # The category may or may not have a budget
    if budget is not None:
        where += "("
        for i in range(len(budget)):
            where += "budget=%s or "
            data.append((i + 1)*'$')
        where = where.rstrip("or ")
        where += ")"
    # Filter by the chosen types
    if len(types) > 0:
        if len(where) > 6:
            where += " and"
        where += " ("
        for t in types:
            where += kind + "=%s or "
            data.append(t)
        where = where.rstrip("or ")
        where += ")"
    # Filter by the chosen features
    if len(features) > 0:
        if len(where) > 6:
            where += " and"
        where += " ("
        for f in features:
            where += "feature_id=%s or "
            data.append(f)
        where = where.rstrip("or ")
        where += ")"
    # Determine whether or not to include the where clause at all
    if len(where) > 6:
        query += where
    # Order by rating and number of reviews
    query += " order by rating desc, num_reviews desc" + \
             " limit %s"
    data.append(amount)
    cursor.execute(query, (tuple(data)))
    results = []
    for info in cursor:
        category_label = [table]
        info = category_label + list(info)
        results.append(info)
    return results


def order_itinerary(itinerary: list) -> list:
    dining = 0
    dining_list = []
    other = 0
    other_list = []
    # Count the number of occurrences
    # Add the entries to the appropriate sublist
    for category in itinerary:
        for entry in category:
            if entry[0] == 'dining':
                dining += 1
                dining_list.append(entry)
            else:
                other += 1
                other_list.append(entry)
    # If there is only dining, return the itinerary
    if other == 0:
        return dining_list
    # Mix up the order of the other activities
    ordered = []
    while len(ordered) < len(other_list):
        choice = other_list[random.randint(0, other - 1)]
        if choice not in ordered:
            ordered.append(choice)
    # If there is no dining, just return the ordered list of other activities
    if dining == 0:
        return ordered
    # Otherwise, try to reasonably place the dining between other activities
    else:
        final_order = []
        ends = math.floor(other / 3)
        middle = math.ceil(other / 3)
        for i in range(ends):
            final_order.append(ordered[i])
        final_order.append(dining_list[0])
        for i in range(middle):
            final_order.append(ordered[i + ends])
        final_order.append(dining_list[1])
        for i in range(ends):
            final_order.append(ordered[i + (2 * ends)])

        return final_order
        # for i in range(0, dining + other):
        #     if i <= ends:
        #         final_order.append(ordered[i])
        #     elif i == ends + 1:
        #         final_order.append(dining_list[1])
        #     elif ends + 2 <= i <= ends + middle + 2:




# Formatting needs work

# def format_itinerary(itinerary: list) -> list:
#     data = []
#     for category in itinerary:
#         for entry in category:
#             cat = ""
#             for i in range(len(entry)):
#                 if i == 0:
#                     cat += str(entry[i]).strip().upper() + ': '
#                 else:
#                     cat += str(entry[i]).strip() + ', '
#             cat = cat.rstrip(', ')
#             data.append(cat)
#     return data
