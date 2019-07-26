from Utility import *


# Class to represent a category of activity
# For use in collecting questionnaire data
class Category:

    # Name of the category
    def __init__(self, name: str, kind: str, id: str, tag: str):
        self.name = name
        self.kind = kind
        self.id = id
        self.tag = tag
        self.include = False
        self.types = []
        self.features = []

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
        print("VERIFY >> " + str(self.include))
        if want:
            self.set_types(cursor)
            print('VERIFY >> ' + str(self.types))
            self.set_features(cursor)
            print('VERIFY >> ' + str(self.features))

    # Function to set the chosen types
    #  cursor: the database cursor
    # Interactive list entry
    def set_types(self, cursor: 'mysql.connector.connection') -> None:
        # Choose types
        while True:
            choice = str(input("Select a type, enter 'done' to move on or 'sample' for ideas:\n"))
            if choice == 'done':
                break
            elif choice == 'sample':
                ideas = sample_type(cursor, self.name, self.kind)
                for i in range(len(ideas)):
                    print(ideas[i])
            else:
                pk = get_pk(cursor, self.name, self.kind, choice, self.id)
                if pk is None:
                    print("No " + self.name + " of type " + choice)
                else:
                    self.types.append(choice)

    # Function to set the chosen types
    #  cursor: the database cursor
    # Interactive list entry
    def set_features(self, cursor: 'mysql.connector.connection') -> None:
        # Choose features
        while True:
            choice = str(input("Select a feature or enter 'done' to move on:\n"))
            if choice == 'done':
                break
            elif choice == 'sample':
                ideas = sample_features(cursor, self.name, self.tag, self.id)
                for i in range(len(ideas)):
                    print(ideas[i])
            else:
                pk = get_feature_pk(cursor, self.name, self.tag, self.id,
                                    "feature_name", choice, "feature_id")
                if pk is None:
                    print("No " + self.name + " with feature " + choice)
                else:
                    self.features.append(choice)
