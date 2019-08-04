from Utility import *


# Class to represent a category of activity
# For use in collecting questionnaire data
class Category:

    # Name of the category
    def __init__(self, name: str, title: str, kind: str, id: str, tag: str, budget: bool):
        # Name of the table ex. dining
        self.name = name
        # Name of the title column ex. dining_name
        self.title = title
        # Name of the type column ex. dining_type
        self.kind = kind
        # Name of the pk column ex. dining_id
        self.id = id
        # Name of the join table ex. dining_tag
        self.tag = tag
        self.has_budget = budget
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
                ideas = sample_type(cursor, self.name, self.kind)
                for i in range(len(ideas)):
                    print(ideas[i])
                print(LINE)
            else:
                pk = get_pk(cursor, self.name, self.kind, choice, self.id)
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
                ideas = sample_features(cursor, self.name, self.tag, self.id)
                for i in range(len(ideas)):
                    print(ideas[i])
                print(LINE)
            else:
                pk = get_feature_pk(cursor, self.name, self.tag, self.id,
                                    "feature_name", choice, "feature_id")
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
        # The budget column only exists in certain tables!
        if self.has_budget:
            # Fill in optional parameter with budget from the questionnaire
            return recommend_activity(cursor, self.name, self.title, self.kind, self.tag, self.id,
                                      self.types, self.features, self.amount, budget)
        else:
            # Ignore optional parameter since there is np budget for this table
            return recommend_activity(cursor, self.name, self.title, self.kind, self.tag, self.id,
                                      self.types, self.features, self.amount)
