from getpass import getpass

from pymongo import MongoClient
import traceback
from datetime import datetime
import re
import pdfs
import secret
from prettytable import PrettyTable
import colorama
import emails
import certifi


def log_exception_to_file(file_name, exception):
    with open(file_name, 'a') as f:
        f.write(str(exception) + '\n')
        traceback.print_exc(file=f)
        f.close()


def reserve_guitar(sn, name, reset=False):
    colorama.init()
    client = MongoClient(secret.mongo_host_connection("user", "blank", True),tlsCAFile=certifi.where())
    db = client["inventory"]
    collection = db["inventory"]

    query = {"S/N": int(sn)}

    document = list(collection.find(query))

    if document[0]["RENTED"] == "F":
        print(colorama.Fore.GREEN +
              "Guitar is confirmed available for rent!" + colorama.Style.RESET_ALL)
        print("\033[3mWould you like to rent it?\033[0m")
        while True:
            ask = input("[Y/n (to exit app)] ")
            if ask.lower() == "y":
                update_operation = {"$set": {"RENTED": "T"}}

                result = collection.update_one(query, update_operation)

                if result.matched_count > 0:
                    print("Successfully blocked guitar!")
                    # Loan forms items after this
                    clas = input("What is your form class? ")

                    while True:
                        email = input("What is your email? ")
                        if pdfs.verify_email(email):
                            break
                        else:
                            print("Invalid email. Please enter again.")

                    pdfs.create_loan_pdf(name=name, email=email, clas=clas,
                                         guitar_model=document[0]["Brand"], serial_num=document[0]["Code"])
                    print("Thank you for using SPSGE App!")
                    print("Exiting app...")
                    exit(0)
                else:
                    print("Failed to block guitar.")
                    break

            elif ask.lower() == "n":
                print("Thank you for using SPSGE App!")
                print("Exiting app...")
                exit(0)
            else:
                print(colorama.Fore.LIGHTRED_EX +
                      "\033[3mInvalid input. Please try again.\033[0m" + colorama.Style.RESET_ALL)
    elif reset:
        print("\033[3mWould you like to reset it?\033[0m")
        while True:
            ask = input("[Y/n (to exit app)] ")
            if ask.lower() == "y":
                update_operation = {"$set": {"RENTED": "F"}}

                result = collection.update_one(query, update_operation)

                if result.matched_count > 0:
                    print("Thank you for using SPSGE App!")
                    print("Exiting app...")
                    exit(0)
                else:
                    print("Failed to block guitar.")
                    break

            elif ask.lower() == "n":
                print("Thank you for using SPSGE App!")
                print("Exiting app...")
                exit(0)
            else:
                print(colorama.Fore.LIGHTRED_EX +
                      "\033[3mInvalid input. Please try again.\033[0m" + colorama.Style.RESET_ALL)
    else:
        print(
            colorama.Back.LIGHTBLUE_EX + colorama.Fore.WHITE + "Sorry, guitar not available. Please try again." + colorama.Style.RESET_ALL)
        return False

    return True


def view_guitars(name, reset=False):
    colorama.init()
    client = MongoClient(secret.mongo_host_connection("user", "blank", True),tlsCAFile=certifi.where())
    db = client["inventory"]
    collection = db["inventory"]

    documents = list(collection.find())

    table = PrettyTable(["S/N", "Code", "Brand", "Allocation",
                         "Level", "BC", "MOE Code", "Remarks", "Rented"])

    largest_sn = 0

    for document in documents:
        rows = []
        for key in document:
            if key != "_id":
                if str(document[key]) != "nan" and key != "S/N":
                    if document["RENTED"] == "T" and key == "RENTED":
                        rows.append(colorama.Fore.LIGHTRED_EX + "Not available for rent" + colorama.Style.RESET_ALL)
                    elif document["RENTED"] == "F" and key == "RENTED":
                        rows.append(colorama.Fore.LIGHTGREEN_EX + "Available for rent" + colorama.Style.RESET_ALL)
                    else:
                        rows.append(document[key])
                elif key == "S/N":
                    rows.append(str(document[key]))
                    if largest_sn < int(document["S/N"]):
                        largest_sn = int(document["S/N"])
                else:
                    rows.append("-")

        table.add_row(rows)

    print(table)

    print(colorama.Back.LIGHTBLACK_EX +
          "\x1B[3mAll data available on the guitars has been shown.\x1B[0m")

    if not reset:
        print("To enter which guitar to loan," + colorama.Fore.LIGHTGREEN_EX + " enter the S/N " + colorama.Fore.RESET +
          "of it. Else," + colorama.Fore.LIGHTRED_EX + " enter q to exit." + colorama.Style.RESET_ALL)
        while True:
            num = input(
            "Enter the S/N of the guitar you would like to rent (or q to quit): ")
            try:
                if int(num) < 1 or int(num) > largest_sn:
                    print(
                    colorama.Fore.LIGHTRED_EX + "Number not within range. Please try again." + colorama.Style.RESET_ALL)
                else:
                    if reserve_guitar(sn=num, name=name):
                        break
            except Exception:
                if num.lower() == "q":
                    print("Thank you for using SPSGE App!")
                    print("Exiting app...")
                    exit(0)
                else:
                    print(colorama.Fore.LIGHTRED_EX + "Invalid input. Please try again." + colorama.Style.RESET_ALL)
    else:
        print("To enter which guitar to reset," + colorama.Fore.LIGHTGREEN_EX + " enter the S/N " + colorama.Fore.RESET +
          "of it. Else," + colorama.Fore.LIGHTRED_EX + " enter q to exit." + colorama.Style.RESET_ALL)
        while True:
            num = input(
            "Enter the S/N of the guitar you would like to reset (or q to quit): ")
            try:
                if int(num) < 1 or int(num) > largest_sn:
                    print(
                    colorama.Fore.LIGHTRED_EX + "Number not within range. Please try again." + colorama.Style.RESET_ALL)
                else:
                    if reserve_guitar(sn=num, name=name, reset=True):
                        break
            except Exception:
                if num.lower() == "q":
                    print("Thank you for using SPSGE App!")
                    print("Exiting app...")
                    exit(0)
                else:
                    print(colorama.Fore.LIGHTRED_EX + "Invalid input. Please try again." + colorama.Style.RESET_ALL)

def login(username, password):
    try:
        client = MongoClient(secret.mongo_host_connection(username, password),tlsCAFile=certifi.where())
        client.admin.command('ping')
        client.close()
        return True

    except Exception as e:
        print("We have run into an error while trying to log you on.")
        if input("Do you think this is a mistake? ").upper() == "Y":
            now = datetime.now()
            log_exception_to_file(now.strftime("%d.%m.%Y.errorlog"), e)
            print("A file has been created with the corresponding error.")
            print(
                "Please email Advait or Ryan with the file attached to report this issue.")

        return False


def make_user(new_user, new_pass, client, username):
    emails.send_email("SPSGE: New User Creation",
                      f"Dear DB admins, {username} has requsted to create a new user. The user is:\n{new_user}\nPassword:{new_pass}",
                      [client, "advait_contractor@outlook.sg", "ryanlim2009@gmail.com"],
                      "something",
                      False)


def is_plain_text_no_spaces_or_special_chars(s):
    # Define the pattern for alphanumeric characters only
    pattern = r'^[a-zA-Z0-9]+$'

    # Use re.match to check if the entire string matches the pattern
    return re.match(pattern, s) is not None

def add_guitar(client):
    db = client["inventory"]
    collection = db["inventory"]

    documents = list(collection.find())

    # table = PrettyTable(["S/N", "Code", "Brand", "Allocation",
    #                      "Level", "BC", "MOE Code", "Remarks", "Rented"])

    largest_sn = 0

    for document in documents:
        rows = []
        for key in document:
            if key == "S/N":
                if largest_sn < int(document["S/N"]):
                    largest_sn = int(document["S/N"])

    new_guitar = {"S/N": largest_sn + 1}

    while True:
        code = input("Please enter the code of the guitar: ")
        if code == "":
            print("Invalid input entered. Please try again.")
        else:
            break

    new_guitar["Code"] = code

    while True:
        brand = input("Please enter the brand of the guitar: ")
        if brand == "":
            print("Invalid input entered. Please try again.")
        else:
            break

    new_guitar["Brand"] = brand
    new_guitar["Allocation"] = "-"
    new_guitar["Level"] = "-"

    while True:
        bc = input("Please enter the BC: ")
        if bc.upper() == "Y" or bc.upper() == "N":
            break
        else:
            print("Invalid input entered. Please try again. BC should be Y or N.")

    new_guitar["BC"] = bc

    pattern = re.compile(r'^[A-Z][a-z]{11}$')

    while True:
        moe = input("Please enter the MOE code (enter dash for no MOE code): ")
        if bool(pattern.match(moe.upper())):
            break
        elif moe == "-":
            print("Leaving MOE Code blank...")
            moe = "-"
            break
        else:
            print("Invalid input. Please try again.")

    if moe != None:
        new_guitar["MOE CODE"] = moe.upper()
    else:
        new_guitar["MOE CODE"] = "-"

    while True:
        remarks = input("Any remarks (press enter without pressing anything for blank remarks): ")
        if remarks == "":
            print("Leaving remarks blank...")
            remarks = "-"
            break
        else:
            break

    new_guitar["REMARKS"] = remarks
    new_guitar["RENTED"] = "F"

    collection.insert_one(new_guitar)
    print("Successfully inserted!")
    print("Thank you for using SPSGE App!")
    exit(0)

def remove_guitar(client):
    colorama.init()
    db = client["inventory"]
    collection = db["inventory"]

    documents = list(collection.find())

    table = PrettyTable(["S/N", "Code", "Brand", "Allocation",
                         "Level", "BC", "MOE Code", "Remarks", "Rented"])

    available_num = []

    for document in documents:
        rows = []
        for key in document:
            if key != "_id":
                if str(document[key]) != "nan" and key != "S/N":
                    if document["RENTED"] == "T" and key == "RENTED":
                        rows.append(colorama.Fore.LIGHTRED_EX + "Not available for rent" + colorama.Style.RESET_ALL)
                    elif document["RENTED"] == "F" and key == "RENTED":
                        rows.append(colorama.Fore.LIGHTGREEN_EX + "Available for rent" + colorama.Style.RESET_ALL)
                    else:
                        rows.append(document[key])
                elif key == "S/N":
                    rows.append(str(document[key]))
                    available_num.append(str(document[key]))
                else:
                    rows.append("-")

        table.add_row(rows)

    print(table)

    print(colorama.Back.LIGHTBLACK_EX +
          "\x1B[3mAll data available on the guitars has been shown.\x1B[0m")

    while True:
        index = input("Please enter the index of the guitar to remove: ")
        if index not in available_num:
            print("Invalid input entered. Please try again.")
        else:
            break

    query = {"S/N": int(index)}
    try:
        result = collection.delete_one(query)
        if result.deleted_count < 1:
            raise Exception("Failed to delete")
    except Exception as e:
        print("We have run into an issue")
        print(e)

    print("Thank you for using SPSGE App!")
    exit(0)

def qm_mode(username, password):
    client = MongoClient(secret.mongo_host_connection(username, password),tlsCAFile=certifi.where())

    print("Hello QM!")
    while True:
        print("What would you like to do today?")
        print("[1] Register new user")
        print("[2] Change details about guitar")
        print("[3] Add guitar")
        print("[4] Remove guitar")
        print("[5] Change loan status")
        print("[6] Quit")

        action = input("What would you like to do: ")

        try:
            if int(action) < 1 or int(action) > 6:
                print("Invalid input. Please try again")

            if action == "1":
                while True:
                    new_user = input("Enter your username (no special characters, no spaces): ")

                    if is_plain_text_no_spaces_or_special_chars(new_user):
                        break
                    else:
                        print(colorama.Fore.LIGHTRED_EX + "Invalid input. Please try again." + colorama.Style.RESET_ALL)

                while True:
                    new_password = getpass("Enter your password (no special characters, no spaces): ")

                    if is_plain_text_no_spaces_or_special_chars(new_user):
                        break
                    else:
                        print(colorama.Fore.LIGHTRED_EX + "Invalid input. Please try again." + colorama.Style.RESET_ALL)

                print("Due to issues in the code previously, we will be sending an email to add the admins to add you ASAP. Please except an email ASAP from them once its done (within 3 days).")
                print("We are sorry for the inconvenience caused")

                while True:
                    print("Please enter your email below (required for the database admins to contact you about the completion of it")
                    email = input("Email: ")

                    if pdfs.verify_email(email):
                        break
                    else:
                        print(colorama.Fore.LIGHTRED_EX + "Error: " + colorama.Style.RESET_ALL + "Email incorrect. Please enter again")

                make_user(new_user, new_password, email, username)

                del new_user, new_password
            elif action == "2":
                print("Not available yet. Coming soon!")
                # client = MongoClient(secrets.mongo_host_connection("user", "blank", True))
                # db = client["inventory"]
                # collection = db["inventory"]
                #
                # documents = list(collection.find())
                #
                # table = PrettyTable(["S/N", "Code", "Brand", "Allocation",
                #                      "Level", "BC", "MOE Code", "Remarks", "Rented"])
                #
                # largest_sn = 0
                #
                # for document in documents:
                #     rows = []
                #     for key in document:
                #         if key != "_id":
                #             if str(document[key]) != "nan" and key != "S/N":
                #                 rows.append(document[key])
                #             elif key == "S/N":
                #                 rows.append(str(document[key]))
                #                 if largest_sn < int(document["S/N"]):
                #                     largest_sn = int(document["S/N"])
                #             else:
                #                 rows.append("-")
                #
                #     table.add_row(rows)
                #
                # print(table)
                #
                # print(colorama.Back.LIGHTBLACK_EX +
                #       "\x1B[3mAll data available on the guitars has been shown.\x1B[0m")
                #
                # while True:
                #     ans = input("What guitar would you like to modify? ")
                #     try:
                #         if int(ans) <= 1 or int(ans) >= largest_sn:
                #             break
                #         else:
                #             print(colorama.Fore.LIGHTRED_EX + "Value out of range. Please try again." + colorama.Style.RESET_ALL)
                #     except Exception as e:
                #         print(colorama.Fore.LIGHTRED_EX + "Error!")
                #         print("Invalid input, please try again." + colorama.Style.RESET_ALL)
                #
                #
            elif action == "3":
                add_guitar(client)
            elif action == "4":
                remove_guitar(client)
            elif action == "5":
                view_guitars(username, reset=True)
            elif action == "6":
                print("Thank you for using SPSGE App!")
                exit(0)
        except Exception as e:
            print(e)
            print("Invalid input. Please try again")



if __name__ == "__main__":
    qm_mode("advaitconty", "SooteFlap")
