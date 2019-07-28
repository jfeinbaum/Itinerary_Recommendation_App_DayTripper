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
        # Complete the survey information
        quest.select_city()
        quest.select_budget()
        quest.run_categories()
        # Output the itinerary
        itinerary = quest.recommend()
        ordered = order_itinerary(itinerary)
        times = get_travel_times(ordered)
        print_itinerary(ordered, times)
        # Close the connection
        quest.cnx.close()
    else:
        # Straight to workspace
        pass


main()
