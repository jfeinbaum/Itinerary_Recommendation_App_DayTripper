

# Class to represent a category of activity
# For use in collecting questionnaire data
class Category:

    # Name of the category
    def __init__(self, name: str):
        self.name = name
        self.include = False
        self.types = []
        self.features = []

    def __str__(self):
        return str(self.name)