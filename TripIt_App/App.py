from Questionnaire import *


# Program Driver
def main():
    # LAUNCH SCREEN: Select to answer questions or skip to workspace
    response = input("Select an option:\n"
                     " - 1. Recommend a Trip\n"
                     " - 2. Plan Custom Trip\n")
    if int(response) == 1:
        # Questionnaire
        quest = Questionnaire()

        quest.select_city()
        quest.select_budget()
        quest.run_categories()

        print(quest)

        quest.cnx.close()
    else:
        # Straight to workspace
        pass


main()