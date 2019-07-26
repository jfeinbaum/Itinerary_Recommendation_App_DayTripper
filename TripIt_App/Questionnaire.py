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
        self.categories = [Category('dining', 'dining_type', 'dining_id', 'dining_tag'),
                           Category('museum', 'museum_type', 'museum_id', 'museum_tag'),
                           Category('park', 'park_type', 'park_id', 'park_tag'),
                           Category('landmark', 'landmark_type', 'landmark_id', 'landmark_tag'),
                           Category('entertainment', 'ent_type', 'ent_id', 'entertainment_tag')]

    def __str__(self) -> str:
        cat = "City: " + str(self.city) + '\n'
        cat += "Budget: " + self.budget + '\n'
        for i in range(len(self.categories)):
            cat += "---------------\n"
            cat += str(self.categories[i])
        return cat

    # Function to select a city
    # Sets the city attribute
    def select_city(self) -> None:
        cursor = self.cnx.cursor()
        result = None
        while result is None:
            city = input("Select a city:\n")
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
    # Include a category, select types, select features
    def run_categories(self) -> None:
        cursor = self.cnx.cursor()
        for i in range(len(self.categories)):
            self.categories[i].set_options(cursor)
        cursor.close()
