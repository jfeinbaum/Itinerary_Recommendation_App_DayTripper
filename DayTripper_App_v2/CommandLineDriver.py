from Questionnaire import *


# Command Line Program Driver
def main():
    # Prepare a connection for the app
    cnx = est_connection()

    # LOGIN GOES HERE

    while True:
        # LAUNCH SCREEN: Select to answer questions or skip to workspace
        print("------ DayTripper ------")
        response = input("Select an option:\n"
                         " - 1. Recommend a Trip\n"
                         " - 2. View Itineraries\n"
                         " - 3. Workspace\n"
                         " - 4. Quit\n")
        # Open the questionnaire
        if int(response) == 1:
            print("Please answer the following questions.")
            print(LINE)
            # Questionnaire
            quest = Questionnaire(cnx)
            # Complete the survey information
            quest.select_city()
            quest.select_budget()
            quest.run_categories()
            # Output the itinerary
            itinerary = quest.recommend()
            ordered = order_itinerary(itinerary)
            times = get_travel_times(ordered)
            formatted = format_itinerary(ordered, times)
            save(formatted, 'MyItinerary.txt')
            print(formatted)

        # View template itineraries
        elif int(response) == 2:
            # Another object?

            # 1. View My Itineraries
            #   -> List of itineraries with descriptions from that user
            #   -> Select index to: Print, Save, or Open in workspace
            # 2. View All itineraries
            #   -> Same as above, maybe limit to 10 randomly selected
            pass

        # Open the workspace
        elif int(response) == 3:
            # This may need to be another object?

            # Go to workspace (print working itinerary each loop)
            # while working
            # 1. Add
            #      -> Fill out cookie cutter search form
            #      -> Accept or decline top result
            # 2. Remove by referencing index
            # 3. Rearrange by referencing index (simple insert probably makes sense)
            # 4. Save itinerary
            #      -> Insert the itinerary into the database
            #      -> Save to .txt file
            # 5. Discard itinerary and quit
            #      -> End the program (or go back to main menu)
            pass

        # Exit the program
        elif int(response) == 4:
            # Close the connection & exit
            cnx.close()
            break

        # Catch-all for invalid inputs
        else:
            print('Unrecognized command, please select a number from the menu.')


main()