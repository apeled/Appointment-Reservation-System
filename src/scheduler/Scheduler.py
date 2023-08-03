from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import math


current_patient = None
current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    
    # create the patient
    patient = Patient(username, salt=salt, hash=hash)
    
    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    global current_caregiver
    global current_patient
    
    # check 1: if no one is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return
    
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_caregiver_availability = "SELECT Caregivers_username FROM Availabilities WHERE Time = %s AND Available = 1 ORDER BY Caregivers_username"
    select_vaccine = "SELECT Name, Doses FROM Vaccines"
    vaccine = []
    avail_caregivers = []
    try:
        # Query to extract the vaccine information
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_vaccine)
        for row in cursor:
            vaccine.append("%s: %d" % (row['Name'], row['Doses']))
        vaccine = ' '.join(vaccine)
        
        # Query to exctrat which caregivers are available on "Date"
        d = datetime.datetime(year, month, day)
        cursor.execute(select_caregiver_availability, d)
        for row in cursor:
            avail_caregivers.append("%s" % (row['Caregivers_username']))
        avail_caregivers = ', '.join(avail_caregivers)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
    finally:
        cm.close_connection()
    if len(avail_caregivers) >= 1:
        print("Available caregivers on %s-%s-%s: %s %s" % (str(month), str(day), str(year), avail_caregivers, vaccine))
        return
    else:
        print("There are no available caregivers for this selected date, please try a different one.")
        return


def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a caregiver first!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    # extracting the date information
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    # extracting the vaccine information
    vaccine_name = tokens[2]
    doses = 1
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when getting available doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when  doses")
        print("Error:", e)
        return
    # check 3: the vaccine name exists
    if vaccine is None:
        print("Selected vaccine does not exist at this clinic")
        return
    if vaccine.available_doses == 0:
        print("Not enough available doses!")
        return
    if vaccine.available_doses > 0:
        # Open connection manager to DB
        cm = ConnectionManager()
        conn = cm.create_connection()
        
        select_caregiver = "SELECT TOP 1 Caregivers_username FROM Availabilities WHERE Time = %s AND Available = 1 ORDER BY Caregivers_username"
        d = datetime.datetime(year, month, day)
        reserve_caregiver = []
        # Query to exctrat which caregiver first available
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_caregiver, d)
            for row in cursor:
                reserve_caregiver.append("%s" % (row['Caregivers_username']))
        except pymssql.Error as e:
            print("Upload Availability Failed")
            print("Db-Error:", e)
            quit()
        except ValueError:
            print('Please enter a valid date "mm-dd-yyyy"!')
            return
        except Exception as e:
            print("Error occurred when finding availability")
            print("Error:", e)
        
        # check 4: see if caregiver available
        if len(reserve_caregiver) == 0:
            print("No Caregiver is available that date! Please try again.")
            return
        # if available, create appoinment,remove availability, and decrease vaccine dose
        if len(reserve_caregiver) >= 1:
            # appointment variables gathered
            patient_username = current_patient.username
            vaccine_name = vaccine_name
            caregiver_username = str(reserve_caregiver[0])
            time = str(month)+str(day)+str(year)
            # unique appointment_id integrated
            appointment_id = []
            for letters in range(len(caregiver_username)): 
                appointment_id.append(str(abs(ord(str.lower(caregiver_username[letters]))-96)))
            appointment_id.append(time)
            appointment_id = ''.join(appointment_id)
            # query to make appointment entry
            appointment_entry = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
            try:
                cursor = conn.cursor(as_dict=True)
                cursor.execute(appointment_entry, (appointment_id, patient_username,
                            vaccine_name, caregiver_username, d))
                conn.commit()
            except pymssql.Error as e:
                print("Upload Appointment Failed")
                print("Db-Error:", e)
                quit()
            except Exception as e:
                print("Error occurred when uploading appointment")
                print("Error:", e)
                return
            finally:
                cm.close_connection()
            # query to remove caregier availability and decrease vaccine dose
            remove_caregiver_availability =  "UPDATE Availabilities SET Available = 0 WHERE Caregivers_username = %s AND Time = %s"
            # Re-open connection manager to DB
            cm = ConnectionManager()
            conn = cm.create_connection()
            try:
                cursor = conn.cursor(as_dict=True)
                cursor.execute(remove_caregiver_availability, (caregiver_username, d))
                vaccine.decrease_available_doses(doses)
                conn.commit()
            except pymssql.Error as e:
                print("Remove Availability Failed")
                print("Db-Error:", e)
                start()
            except Exception as e:
                print("Error occurred when updating availability")
                print("Error:", e)
                return
            finally:
                cm.close_connection()
            print("Appointment ID: %s, Caregiver username: %s" % (appointment_id, caregiver_username))
            return
    
    

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print('Please enter a valid date "mm-dd-yyyy"!')
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    # cancel <appointment_id>
    global current_caregiver
    global current_patient
    # check 1: if no one is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return
    # extract appointment_id
    appointment_id = tokens[1]
    appointment_exists = []
    # Open connection manager to DB
    cm = ConnectionManager()
    conn = cm.create_connection()
    # check 3: check if the current logged-in user is a caregiver or patient
    if current_caregiver is not None: 
        # check 4a: if caregiver has appointment with appointment id
        query_appointment_exists = "SELECT * FROM Appointments WHERE appointment_id = %s AND Caregivers_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query_appointment_exists, (appointment_id, current_caregiver.username))
            for row in cursor:
                appointment_exists.append("%s" % (row['appointment_id']))
                appointment_exists.append("%s" % (row['Vaccines_name']))
                appointment_exists.append("%s" % (row['Time']))
                appointment_exists.append("%s" % (row['Caregivers_username']))                        
        except pymssql.Error as e:
            print("Finding Appointment Failed")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when finding appointment")
            print("Error:", e)
        if len(appointment_exists) == 0:
            print("No such appointment combination exists! Please try again.")
            return
        if len(appointment_exists) >= 1:
            doses = 1
            # query to remove appointment
            query_remove_appointment = "DELETE FROM Appointments WHERE appointment_id = %s"
            # query to recover caregier availability and recover vaccine dose
            recover_caregiver_availability =  "UPDATE Availabilities SET Available = 1 WHERE Caregivers_username = %s AND Time = %s"
            try:
                # get vaccine information
                vaccine = Vaccine(appointment_exists[1], doses).get()
                cursor = conn.cursor(as_dict=True)
                cursor.execute(query_remove_appointment, appointment_exists[0])
                vaccine.increase_available_doses(doses)
                cursor.execute(recover_caregiver_availability, (appointment_exists[3], appointment_exists[2]))
                conn.commit()
            except pymssql.Error as e:
                print("Recover Availability Failed")
                print("Db-Error:", e)
                start()
            except Exception as e:
                print("Error occurred when recovering availability")
                print("Error:", e)
                return
            finally:
                cm.close_connection()
            print("Caregiver canceled appointment %s on %s" % (appointment_exists[0], appointment_exists[2]))
    if current_patient is not None: 
        # check 4a: if caregiver has appointment with appointment id
        query_appointment_exists = "SELECT * FROM Appointments WHERE appointment_id = %s AND Patients_username = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query_appointment_exists, (appointment_id, current_patient.username))
            for row in cursor:
                appointment_exists.append("%s" % (row['appointment_id']))
                appointment_exists.append("%s" % (row['Vaccines_name']))
                appointment_exists.append("%s" % (row['Time']))
                appointment_exists.append("%s" % (row['Caregivers_username']))
        except pymssql.Error as e:
            print("Finding Appointment Failed")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when finding appointment")
            print("Error:", e)
        if len(appointment_exists) == 0:
            print("No such appointment combination exists! Please try again.")
            return
        if len(appointment_exists) >= 1:
            doses = 1
            # query to remove appointment
            query_remove_appointment = "DELETE FROM Appointments WHERE appointment_id = %s"
            # query to recover caregier availability and recover vaccine dose
            recover_caregiver_availability =  "UPDATE Availabilities SET Available = 1 WHERE Caregivers_username = %s AND Time = %s"
            try:
                # get vaccine information
                vaccine = Vaccine(appointment_exists[1], doses).get()
                cursor = conn.cursor(as_dict=True)
                cursor.execute(query_remove_appointment, appointment_exists[0])
                vaccine.increase_available_doses(doses)
                cursor.execute(recover_caregiver_availability, (appointment_exists[3], appointment_exists[2]))
                conn.commit()
            except pymssql.Error as e:
                print("Recover Availability Failed")
                print("Db-Error:", e)
                start()
            except Exception as e:
                print("Error occurred when recovering availability")
                print("Error:", e)
                return
            finally:
                cm.close_connection()
            print("Patient canceled appointment %s on %s" % (appointment_exists[0], appointment_exists[2]))

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")
    return

def show_appointments(tokens):
    # show_appointments
    global current_caregiver
    global current_patient
    # check 1: check if the current logged-in user is a caregiver, patient or none
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return
    if current_caregiver is not None: 
        # Open connection manager to DB
        cm = ConnectionManager()
        conn = cm.create_connection()
        appointments = []
        # Query to exctrat which caregiver first available
        select_appointments = "SELECT appointment_id, Vaccines_name, Time, Patients_username FROM Appointments WHERE Caregivers_username = %s ORDER BY appointment_id"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, current_caregiver.username)
            for row in cursor:
                appointments.append("%s %s %s %s" % (row['appointment_id'],row['Vaccines_name'],row['Time'],row['Patients_username']))
        except pymssql.Error as e:
            print("Download Appointments Failed")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when finding appointments")
            print("Error:", e)
        finally:
            cm.close_connection()
        if len(appointments) == 0:
            print("No appointments for caregiver! Please try again.")
            return
        if len(appointments) >= 1:    
            print(' '.join(appointments))
        return
    if current_patient is not None:
        # Open connection manager to DB
        cm = ConnectionManager()
        conn = cm.create_connection()
        appointments = []
        # Query to exctrat which caregiver first available
        select_appointments = "SELECT appointment_id, Vaccines_name, Time, Caregivers_username FROM Appointments WHERE Patients_username = %s ORDER BY appointment_id"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, current_patient.username)
            for row in cursor:
                appointments.append("%s %s %s %s" % (row['appointment_id'],row['Vaccines_name'],row['Time'],row['Caregivers_username']))
        except pymssql.Error as e:
            print("Download Appointments Failed")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when finding appointments")
            print("Error:", e)
        finally:
            cm.close_connection()
        if len(appointments) == 0:
            print("No appointments for patient! Please try again.")
            return
        if len(appointments) >= 1:    
            print(' '.join(appointments))
        return

def logout(tokens):
    # logout
    global current_caregiver
    global current_patient
    
    # check 1: if no one is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return
    
    # check 2: if someone's already logged-in
    if current_caregiver is not None or current_patient is not None:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out!")
        start()
        return
    else:
        print("Please try again!")
        return



def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")
    print("> logout")
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
            return
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
