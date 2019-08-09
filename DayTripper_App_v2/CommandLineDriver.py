from Questionnaire import *


# Command Line Program Driver
def main():
    # Prepare a connection for the app
    cnx = est_connection()

    # LOGIN GOES HERE
    while True:
        print("------ DayTripper ------")
        response = input("Select an option:\n"
                     " - 1. Login\n"
                     " - 2. Register\n")
        if int(response) == 1:
            while True:
                username = input("Username: ")
                password = input("Password: ")
                if verify_login(cnx, username, password):
                    print("Logged in as " + username + "\n")
                    break
                else:
                    print("Invalid username or password\n")

        elif int(response) == 2:
            while True:
                username = input("Enter a new username: ")
                password = input("Enter a new password: ")
                if register_user(cnx, username, password):
                    print("Successfully registered " + username+"\n")
                    break
                else:
                    print("Username taken\n")

        break

    while True:
        # LAUNCH SCREEN: Select to answer questions or skip to workspace
        print("------ DayTripper ------")
        response = input("Select an option:\n"
                         " - 1. Recommend a Trip\n"
                         " - 2. View Itineraries\n"
                         " - 3. Workspace\n"
                         " - 4. Logout\n")
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
            print_itinerary(ordered, times)
            print(LINE)
            desc = input("Enter a description to save this itinerary: ")
            save(formatted, 'MyItinerary.txt')
            insert_itinerary(cnx, ordered, username, desc)
            print()


        # View template itineraries
        elif int(response) == 2:
            # Another object?

                        # 1. View My Itineraries
            #   -> List of itineraries with descriptions from that user
            #   -> Select index to: Print, Save, or Open in workspace
            # 2. View All itineraries
            #   -> Same as above, maybe limit to 10 randomly selected
            while True:
                response = input("Select an option:\n"
                                 " - 1. View My Itineraries\n"
                                 " - 2. View All Itineraries\n")
                if int(response) == 1:
                    my_itineraries = get_my_itineraries(cnx, username)
                    if len(my_itineraries) == 0:
                        print("You don't have any itineraries\n")
                        break
                    print("My Itineraries:\n")
                    for i in range(len(my_itineraries)):
                        print(str(i+1)+". "+ my_itineraries[i][1])
                    print()
                    itin_id = input("Select an itinerary to view: ")

                    itin_to_view = get_an_itinerary(cnx, itin_id)
                    print(itin_to_view)
                    print(LINE)

                elif int(response) == 2:
                    all_itineraries = get_random_itineraries(cnx)
                    if len(all_itineraries) == 0:
                        print("There are no itineraries\n")
                        break
                    print("Random Itineraries (up to 10):\n")
                    for i in range(len(all_itineraries)):
                        print(str(i+1)+". "+all_itineraries[i][1]+" -- by user: "+all_itineraries[i][2])
                    print()
                    itin_id = input("Select an itinerary to view: ")
                    itin_to_view = get_an_itinerary(cnx, itin_id)
                    print(itin_to_view)
                    print(LINE)



                break

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
