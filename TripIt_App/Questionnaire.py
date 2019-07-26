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
        self.categories = [Category('dining', 'dining_name', 'dining_type', 'dining_id', 'dining_tag', True),
                           Category('museum', 'museum_name', 'museum_type', 'museum_id', 'museum_tag', False),
                           Category('park', 'park_name', 'park_type', 'park_id', 'park_tag', False),
                           Category('landmark', 'landmark_name', 'landmark_type', 'landmark_id', 'landmark_tag', False),
                           Category('entertainment', 'ent_name', 'ent_type', 'ent_id', 'entertainment_tag', True)]

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

    # Function to recommend a itinerary
    def recommend(self) -> list:
        # 2 Restaurants, Assign 4 other activities
        # Or pick 6 activities
        total_act = 6
        # Set the number of times to run each activity
        # Pick 2 Restaurants & evenly distribute remaining activities
        if self.categories[0].include:
            self.categories[0].amount = 2
            total_act -= 2
        skips = 0
        max_skips = len(self.categories[1:])
        while total_act > 0:
            for activity in self.categories[1:]:
                if activity.include:
                    activity.amount += 1
                    skips -= 1
                    total_act -= 1
                else:
                    skips += 1
                    if skips > max_skips:
                        break
        # Create a list of activities based on choices
        itinerary = []
        cursor = self.cnx.cursor()
        for activity in self.categories:
            if activity.include:
                itinerary.append(activity.recommend_category(cursor, self.budget))
        cursor.close()
        return itinerary
