from Utility import *


# Class to represent a category of activity
# For use in collecting questionnaire data
class Category:

    # Name of the category
    def __init__(self, category_name: str):
        # Name of the table ex. dining
        self.name = category_name
        self.amount = 0
        self.include = False
        self.types = []
        self.features = []

    # String representation of a category's information
    def __str__(self) -> str:
        cat = "\tCategory: " + self.name + '\n'
        cat += "\tInclude: " + str(self.include) + '\n'
        cat += "\tTypes: " + str(self.types) + '\n'
        cat += "\tFeatures: " + str(self.features) + '\n'
        return cat

    # Function to walk the user through category questions
    #  cursor: the database cursor
    # Decide to include category, and if so, set types & features
    def set_options(self, cursor: 'mysql.connector.connection') -> None:
        # Include the category at all?
        want = None
        while want is None:
            choice = input("Include " + str(self.name) + " activities? (y/n)\n")
            if choice == 'y':
                want = True
            elif choice == 'n':
                want = False
        self.include = want
        if want:
            print("Including " + str(self.name) + " activities.")
            print(LINE)
            self.set_types(cursor)
            self.set_features(cursor)

    # Function to set the chosen types
    #  cursor: the database cursor
    # Interactive list entry
    def set_types(self, cursor: 'mysql.connector.connection') -> None:
        # Choose types
        while True:
            choice = str(input("Select a type, enter 'done' to move on or 'sample' for ideas:\n"))
            if choice == 'done':
                print("Types: " + str(self.types))
                print(LINE)
                break
            elif choice == 'sample':
                ideas = sample_types(cursor, self.name)
                for i in range(len(ideas)):
                    print(ideas[i])
                print(LINE)
            else:
                pk = get_pk(cursor, 'place', 'type', choice, 'place_id', self.name)
                if pk is None:
                    print("No " + self.name + " of type " + choice)
                    print(LINE)
                else:
                    self.types.append(choice)
                    print("Types: " + str(self.types))
                    print(LINE)

    # Function to set the chosen types
    #  cursor: the database cursor
    # Interactive list entry
    def set_features(self, cursor: 'mysql.connector.connection') -> None:
        # Choose features
        while True:
            choice = str(input("Select a feature, enter 'done' to move on or 'sample' for ideas:\n"))
            if choice == 'done':
                print("Features: " + str(self.features))
                print(LINE)
                break
            elif choice == 'sample':
                ideas = sample_features(cursor, self.name)
                for i in range(len(ideas)):
                    print(ideas[i])
                print(LINE)
            else:
                pk = get_feature_pk(cursor, self.name, choice)
                if pk is None:
                    print("No " + self.name + " with feature " + choice)
                    print(LINE)
                else:
                    self.features.append(choice)
                    print("Features: " + str(self.features))
                    print(LINE)

    # Function to recommend activities from the category
    #  cursor: the mysql connector cursor to the database
    #  budget: string of 1 to 4 '$' signs (ex. '$$$')
    # Returns a list of the recommended activities
    def recommend_category(self, cursor: 'mysql.connector.connection', budget: str) -> list:
        # Fill in optional parameter with budget from the questionnaire
        return recommend_activity(cursor, self.name, self.types, self.features, self.amount, budget)
