import mysql.connector
from mysql.connector import errorcode
import random
import math
from geopy.distance import geodesic

LINE = "---------------------------"


# Function to establish a connection with the database
def est_connection() -> 'mysql.connector.connection':
    # Initialize to reference outside of try-catch block
    cnx = None
    try:
        cnx = mysql.connector.connect(user='daytripper_demo',
                                      password=' ',
                                      database='daytripper')
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
        x = random.randint(0, len(results) - 1)
        smaller_list.append(results[x])
    return smaller_list


# Function to recommend an activity
#  cursor: the connection cursor
#  table: name of the category table (ex. 'dining')
#  title: name of the x_name attribute (ex. 'dining_name')
#  kind: name of the x_type attribute (ex. 'dining_type')
#  tag: name of the x_tag table (ex. 'dining_tag')
#  id: name of the x_id attribute (ex. 'dining_id')
#  types: list of chosen types, use Category.types
#  features: the list of chosen features, use Category.features
#  budget: the chosen budget as 1 - 4 '$' signs in a single string (ex. '$$$')
# Returns a list of recommended activities
def recommend_activity(cursor: 'mysql.connector.connection',
                       table: str, title: str, kind: str, tag: str, id: str,
                       types: list, features: list, amount: int, budget=None) -> list:
    # Generate the where clause: budget, then types, then features
    # The where clause may or may not be included depending on the user's answers
    where = " where "
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
        if len(where) > 7:
            where += " and"
        where += " ("
        for t in types:
            where += kind + "=%s or "
            data.append(t)
        where = where.rstrip("or ")
        where += ")"
    # Filter by the chosen features
    if len(features) > 0:
        if len(where) > 7:
            where += " and"
        where += " ("
        for f in features:
            where += "feature_id=%s or "
            data.append(f)
        where = where.rstrip("or ")
        where += ")"
    # Prepare the query
    query = ""
    # 4 Cases: (Budget or no Budget) * (Features or no features)
    # Set the placeholder variables in the query string
    price_column = ""
    join = ""
    if budget is not None:
        price_column = "budget, "
    if len(features) > 0:
        join = " join " + tag + " using (" + id + ") join feature using (feature_id) "
    # Generate the query, accounting for the 4 cases above
    query += "select distinct " + title + ", " + kind + ", rating, " + price_column + table + \
             ".description, latitude, longitude" + " from " + table + join
    # Determine whether or not to include the where clause at all
    if len(where) > 7:
        query += where
    # Order by rating and number of reviews
    query += " order by rating desc, num_reviews desc" + \
             " limit %s"
    # Run the query and gather the results in a list
    data.append(amount)
    cursor.execute(query, (tuple(data)))
    results = []
    for info in cursor:
        category_label = [table]
        info = category_label + list(info)
        results.append(info)
    return results


# Function to order the recommended activities
#  itinerary: list of recommended activities, use the output from recommend_activity())
# Returns a list of activities in a new order (partially random)
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
        num = random.randint(0, other - 1)
        choice = other_list[num]
        if choice not in ordered:
            ordered.append(choice)
    # If there is no dining, just return the ordered list of other activities
    if dining == 0:
        return ordered
    # Otherwise, try to reasonably place the dining between other activities
    final_order = []
    # For this case, every other seems reasonable
    if dining == other:
        total = dining + other
        for i in range(total):
            if i % 2 == 0:
                final_order.append(ordered.pop())
            else:
                final_order.append(dining_list.pop())
        return final_order
    # When there are more 'other' activities, spread the dining out
    else:
        # Reserve times for dining
        reserved = []
        total = dining + other
        # Chunk is a block of time to wait between meals
        chunk = math.floor(total / (dining + 1))
        for i in range(dining):
            slot = ((i + 1) * chunk) + (i % 2)
            # Make sure the reservation doesn't go out of bounds
            if slot > total - 1:
                slot = total - 1
                # Move it back if there is somehow a collision
                # (there shouldn't be but don't want to lose the activity just in case)
                while slot in reserved:
                    slot -= 1
            reserved.append(slot)
        # Add activities to the itinerary, using reserved list to place dining
        for i in range(total):
            if i in reserved:
                final_order.append(dining_list.pop())
            else:
                final_order.append(ordered.pop())
        return final_order


# Function to calculate the travel times between activities
#  itinerary: list of recommended activities, use the output from recommend_activity())
# Returns a list of travel times
def get_travel_times(itinerary: list) -> list:
    while True:
        mode = str(input("Select mode of transportation (walk, bike, or car):\n"))
        if mode == "walk":
            mph = 3
            break
        elif mode == "bike":
            mph = 7
            break
        elif mode == "car":
            mph = 15
            break
    travel_times = []
    for i in range(len(itinerary)-1):
        coord_1 = (itinerary[i][-2], itinerary[i][-1])
        coord_2 = (itinerary[i+1][-2], itinerary[i+1][-1])
        miles = geodesic(coord_1, coord_2).miles
        miles = miles * 1.25  # "city" distance to account for traffic
        minutes = int((miles/mph)*60)
        travel_times.append(minutes)
    return travel_times


# Function to print the itinerary in a readable format
#  itinerary: list of recommended activities, use the output from recommend_activity())
#  times: list of travel times, use output from get_travel_times()
# Returns nothing, prints the itinerary to terminal
def print_itinerary(itinerary: list, times: list) -> None:
    formatted_itinerary = []
    for i in range(len(itinerary)):
        entry = itinerary[i]
        name = entry[1]
        type = entry[2]
        rating = str(entry[3])
        if entry[0] == 'dining' or entry[0] == 'entertainment':
            description = entry[5]
        else:
            description = entry[4]
        formatted_entry = name+'\n\t'+type+'\n\tRating: '+rating+'\n\t'+description

        formatted_itinerary.append(formatted_entry)
    for i in range(len(formatted_itinerary) - 1):
        print(formatted_itinerary[i])
        print('\t\t|\n\t\t|\t' + str(times[i]) + ' minutes' + '\n\t\t|\n\t\tv')
    print(formatted_itinerary[-1])


# Function to generate a string of the itinerary in a readable format
#  itinerary: list of recommended activities, use the output from recommend_activity())
#  times: list of travel times, use output from get_travel_times()
# Returns string of the itinerary in readable format
def format_itinerary(itinerary: list, times: list) -> str:
    cat = ""
    formatted_itinerary = []
    for i in range(len(itinerary)):
        entry = itinerary[i]
        name = entry[1]
        type = entry[2]
        rating = str(entry[3])
        if entry[0] == 'dining' or entry[0] == 'entertainment':
            description = entry[5]
        else:
            description = entry[4]
        formatted_entry = name + '\n\t' + type + '\n\tRating: ' + rating + '\n\t' + description.strip() + '\n'

        formatted_itinerary.append(formatted_entry)
    for i in range(len(formatted_itinerary) - 1):
        cat += formatted_itinerary[i]
        cat += '\t\t|\n\t\t|\t' + str(times[i]) + ' minutes' + '\n\t\t|\n\t\tv\n'
    cat += formatted_itinerary[-1]
    return cat


# Function to save the itinerary to a file
# Note: this function will overwrite a previous file with the same name
#  formatted_itinerary: str, the output from format_itinerary is recommended
#  filename: str, the name of the file
# Returns nothing, writes the itinerary to a .txt file
def save(formatted_itinerary: str, filename: str) -> None:
    # Ensure the written file is of the expected type
    if not filename.endswith('.txt'):
        filename += '.txt'
    file = open(filename, 'w')
    file.write(formatted_itinerary)
    file.close()

