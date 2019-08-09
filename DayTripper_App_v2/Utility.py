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
#  cursor: cursor from the connection to the database
#  table: name of the table to check
#  check_col: name of the column to check
#  entry: name of the entry to search for
#  ret_col: name of the column value to return
#  name: optional, name of the category of place
# Returns the value in ret_col (primary key) or None if it doesn't exist
def get_pk(cursor: 'mysql.connector.connection',
           table: str, check_col: str, entry: str or int, ret_col: str, name=None) -> int or None:
    # Setup the query using concatenation (%s params are forced to a data type)
    query = "select " + ret_col + " from " + table + " where " + check_col + "=%s "
    if name is not None:
        query += "and category =%s"
        cursor.execute(query, (entry, name))
    else:
        # Single value tuple requires odd format (variable,)
        cursor.execute(query, (entry,))
    # When None is returned, no such entry exists
    result = None
    for pk in cursor:
        result = int(str(pk).lstrip('(').rstrip(',)'))
    return result


# Function to get the pk of a feature if it exists for this category
#  name: name of the category of activity (ex. 'dining')
#  entry: name of the entry to search for
# Returns the value in ret_col (primary key) or None if it doesn't exist
def get_feature_pk(cursor: 'mysql.connector.connection', name: str, entry: str) -> int or None:
    # Setup the query using concatenation (%s params are forced to a data type)
    query = "select feature_id " + \
            "from place join tag using(place_id) " + \
            "join feature using(feature_id) " \
            "where category =%s and feature_name =%s"
    data = (name, entry)
    cursor.execute(query, data)
    # When None is returned, no such entry in the category has the chosen feature
    result = None
    for pk in cursor:
        result = int(str(pk).lstrip('(').rstrip(',)'))
    return result


# Function to get example types to help the user choose
#  cursor: the connection cursor
#  name: name of the category
# Returns a list of sample types and their frequency
def sample_types(cursor: 'mysql.connector.connection', name: str) -> list:
    query = "select type, count(*)" \
            " from place" + \
            " where category =%s" + \
            " group by type" + \
            " order by count(*) desc" + \
            " limit 5"
    cursor.execute(query, (name,))
    results = []
    for category_type in cursor:
        results.append(category_type)
    return results


# Function to get example features to help the user choose
#  cursor: the connection cursor
#  category: the category of place to sample features for
# Returns a list of sample features and their frequency
def sample_features(cursor: 'mysql.connector.connection',
                    category: str) -> list:
    query = "select feature_name, count(*)" \
            " from place join tag using (place_id)" + \
            " join feature using(feature_id)" + \
            " where category =%s" + \
            " group by feature_id" + \
            " order by count(*) desc"
    cursor.execute(query, (category,))
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
#  name: name of the category table (ex. 'dining')
#  types: list of chosen types, use Category.types
#  features: the list of chosen features, use Category.features
#  amount: the amount of this type of activity to recommend
#  budget: the chosen budget as 1 - 4 '$' signs in a single string (ex. '$$$')
# Returns a list of recommended activities
def recommend_activity(cursor: 'mysql.connector.connection', name: str,
                       types: list, features: list, amount: int, budget: str) -> list:
    # Generate the where clause: budget, then types, then features
    # The where clause may or may not be included depending on the user's answers
    where = " where "
    # Data will be a list parameters (%s) for the sql query, convert to tuple before using
    data = []
    # Always fill in the category
    where += "(category=%s)"
    data.append(name)
    # Always fill in the budget cap
    where += " and ("
    for i in range(len(budget) + 1):
        where += "budget=%s or "
        data.append(i * '$')
    where = where.rstrip("or ")
    where += ")"
    # Filter by the chosen types
    if len(types) > 0:
        where += " and ("
        for t in types:
            where += "type =%s or "
            data.append(t)
        where = where.rstrip("or ")
        where += ")"
    # Filter by the chosen features
    if len(features) > 0:
        where += " and ("
        for f in features:
            where += "feature_id=%s or "
            data.append(f)
        where = where.rstrip("or ")
        where += ")"
    # Prepare the query
    query = ""
    join = ""
    if len(features) > 0:
        join = " join tag using (place_id) join feature using (feature_id) "
    # Generate the query, accounting for the 4 cases above
    query += "select distinct name, category, type, rating, budget, " + \
             "place.description, latitude, longitude " \
             "from place " + join
    # Append the where clause (will never be empty)
    query += where
    # Order by rating and number of reviews
    query += " order by rating desc, num_reviews desc" + \
             " limit %s"
    # Run the query and gather the results in a list
    data.append(amount)
    cursor.execute(query, (tuple(data)))
    results = []
    for info in cursor:
        category_label = [name]
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
        rating = str(entry[4])
        if entry[0] == 'dining' or entry[0] == 'entertainment':
            description = entry[6].strip()
        else:
            description = entry[5].strip()
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
        description = entry[7]
        formatted_entry = name + '\n\t' + type + '\n\tRating: ' + rating + '\n\t' + str(description).strip() + '\n'
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

 
# Function to insert a new itinerary
#  itinerary: list of recommended activities, in order
#  username: str, the user that created this itinerary
#  description: str, the description to be saved along with this itinerary
# Returns nothing
def insert_itinerary(cnx: 'mysql.connector.connection',
                     itinerary: list, username: str, description: str) -> None:
    cursor = cnx.cursor()
    user_id = str(get_pk(cursor, "user", "user_name", username, "user_id"))
    itinerary_query = "insert into itinerary (user_id, description) value (%s,%s)"
    cursor.execute(itinerary_query, (user_id, description))
    cnx.commit()
    itinerary_id = str(get_pk(cursor, "itinerary", "description", description, "itinerary_id"))
    for i in range(len(itinerary)):
        name = itinerary[i][1]
        ordering = str(i+1)
        place_id = str(get_pk(cursor, "place", "name", name, "place_id"))
        query = "insert into activity value (%s,%s,%s)"
        cursor.execute(query, (itinerary_id, place_id, ordering))
        cnx.commit()
        
        
# Function to check if a user exists in the database
#  cursor: cursor connection to the database
#  username: string, the username of the user
# Returns true if the user exists, otherwise false
def check_user_exists(cursor: 'mysql.connector.connection', username: str) -> bool:
    query = "select count(*) from user where user_name =%s"
    cursor.execute(query, (username,))
    for row in cursor:
        if int(row[0]) == 1:
            return True
    return False


# Function to check if the username and password are valid
#  cnx: connection to the database
#  username: string, the username of the user
#  password: string, the user password
# Returns true if the credentials are valid, otherwise false
def verify_login(cnx: 'mysql.connector.connection',
                 username: str, password: str, ) -> bool:
    cursor = cnx.cursor()
    exists = check_user_exists(cursor, username)
    if exists:
        query = "select password from user where user_name =%s"
        cursor.execute(query, (username,))
        for row in cursor:
            if row[0] == password:
                return True
            return False
    return False


# Function to register a new user into the database
#  cnx: cursor connection to the database
#  username: string, the username of the user
#  password: string, the user password
# Returns true if the registration succeeded, otherwise false
def register_user(cnx: 'mysql.connector.connection',
                  username: str, password: str, ) -> bool:
    cursor = cnx.cursor()
    if not check_user_exists(cursor, username):
        query = "insert into user (user_name, password) value (%s,%s)"
        data = (username, password)
        cursor.execute(query, data)
        cnx.commit()
        return True
    else:
        return False
    

# Function to find the itineraries associated with a user
#  cnx: connection to the database
#  username: string, the username of the user
# Returns a list of itinerary descriptions
def get_my_itineraries(cnx: 'mysql.connector.connection', username: str) -> list:
    itineraries = []
    cursor = cnx.cursor()
    user_id = str(get_pk(cursor, "user", "user_name", username, "user_id"))
    query = "select itinerary_id, description from itinerary where user_id =%s"
    cursor.execute(query, (user_id,))
    for row in cursor:
        itineraries.append(row)
    return itineraries


# Function to get an itinerary using its id
#  cnx: connection to the database
#  itin_id: primary key for an itinerary
# Returns a list of places in a specific order that corresponds to the itinerary
def get_an_itinerary(cnx: 'mysql.connector.connection', itin_id: str) -> list:
    itinerary = []
    cursor = cnx.cursor()
    query = "select * from place join activity using (place_id) where itinerary_id =%s order by ordering"
    cursor.execute(query, (itin_id,))
    for row in cursor:
        row = row[:-2]
        itinerary.append(row)
    times = get_travel_times(itinerary)
    formatted = format_itinerary(itinerary, times)
    return formatted


# Function to randomly select itineraries from the database
#  cnx: connection to the database
# Returns a list of itineraries (id, description, user who created it)
def get_random_itineraries(cnx: 'mysql.connector.connection') -> list:
    itineraries = []
    cursor = cnx.cursor()
    query = "select itinerary_id, description, user_name from itinerary join user using (user_id)"
    cursor.execute(query, ())
    for row in cursor:
        itineraries.append(row)
    smaller_list = []
    for i in range(10):
        x = random.randint(0, len(itineraries) - 1)
        if itineraries[x] not in smaller_list:
            smaller_list.append(itineraries[x])
    return smaller_list



