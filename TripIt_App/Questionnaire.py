from Utility import *
from Category import *


# Class to represent a Questionnaire
class Questionnaire:

    # Variables will be used to generate an itinerary
    def __init__(self):
        self.cnx = est_connection()
        # Location and budget are always included in query
        self.city = 1
        self.budget = "$"
        self.categories = [Category('dining'),
                           Category('museum'),
                           Category('park'),
                           Category('landmark'),
                           Category('entertainment')]


    # Function to select a city
    # Sets the city attribute
    def select_city(self) -> None:
        city = input("Select a city:\n")
        cursor = self.cnx.cursor()
        result = None
        while result is None:
            result = get_pk(cursor, "city", "city_name", city, "city_id")
        self.city = result
        cursor.close()

    # Function to select a
    # Sets the budget attribute
    def select_budget(self) -> None:
        budget = ''
        while budget == '':
            spend = input("Describe budget on scale $ (cheap) to $$$$ (expensive):\n")
            for i in spend:
                if i != '$':
                    budget = ''
                    break
                else:
                    budget += '$'
        self.budget = budget

    # Function to set info attributes for the categories
    # inc_x, x_types, x_features attributes for all in CATEGORY list
    def run_categories(self) -> None:
        for i in range(len(self.categories)):
            self.category_options(i)

    # Function to walk the user through category questions
    #  num: integer, index of the list CATEGORY to set attributes for
    def category_options(self, num: int):
        # Include the category at all?
        want = None
        while want is None:
            choice = input("Include " + str(self.categories[num]) + " activities? (y/n)\n")
            if choice == 'y':
                want = True
            elif choice == 'n':
                want = False
        self.categories[num].include = want
        print('VERIFY >> ' + str(self.categories[num].include))


