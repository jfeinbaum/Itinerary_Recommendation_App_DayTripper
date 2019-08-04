from Category import *


# Class to represent a Questionnaire
class Questionnaire:

    # Variables will be used to generate an itinerary
    def __init__(self, cnx: 'mysql.connector.connection'):
        self.cnx = cnx
        # Location and budget are always included in query
        self.city = 1
        self.budget = "$"
        self.categories = []
        # Generate all possible categories automatically
        cursor = cnx.cursor()
        setup = "select distinct category from place"
        cursor.execute(setup)
        for category in cursor:
            name = str(category).lstrip('(\'').rstrip('\',)')
            self.categories.append(Category(name))
        cursor.close()

    # Defines the string representation of a Questionnaire
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
        city = ""
        while result is None:
            city = input("Select a city:\n")
            result = get_pk(cursor, "city", "city_name", city, "city_id")
        self.city = result
        print("Selected city: " + str(city))
        print(LINE)
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
        print("Selected budget: " + str(budget))
        print(LINE)
        self.budget = budget

    # Function to set info attributes for the categories
    # Include a category, select types, select features
    def run_categories(self) -> None:
        cursor = self.cnx.cursor()
        for i in range(len(self.categories)):
            self.categories[i].set_options(cursor)
        cursor.close()

    # Function to get a list of the category names
    # Returns a list of category names
    def category_names(self) -> list:
        names = []
        for c in self.categories:
            names.append(c.name)
        return names

    # Function to recommend a itinerary
    # Returns a list containing recommended activities
    # Note: Itinerary sorted by category in the order they were added to
    # the Questionnaire. Reorder them using order_itinerary()
    def recommend(self) -> list:
        # Arbitrary for now
        for activity in self.categories:
            activity.amount = 2

        # Create a list of activities based on choices
        itinerary = []
        cursor = self.cnx.cursor()
        for activity in self.categories:
            if activity.include:
                itinerary.append(activity.recommend_category(cursor, self.budget))
        cursor.close()
        return itinerary
