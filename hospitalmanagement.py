import mysql.connector
from prettytable import PrettyTable
from mysql.connector import Error
from mysql.connector import errorcode

db = mysql.connector.connect(host="localhost", user="root", password="prathammysqlpassword")
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS HPManagementFinal")
cursor.execute("USE HPManagementFinal")

#Tables
#Users Table
cursor.execute("""CREATE TABLE IF NOT EXISTS users(LoginNumber INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, gender VARCHAR(10), age INT, PhoneNumber VARCHAR(15))""")
db.commit()

#Doctors Table
cursor.execute("""CREATE TABLE IF NOT EXISTS doctors(id VARCHAR(10) PRIMARY KEY, FirstName VARCHAR(255) NOT NULL, LastName VARCHAR(255) NOT NULL, specialization VARCHAR(50) NOT NULL,gender VARCHAR(10), PhoneNumber VARCHAR(15), email VARCHAR(255) NOT NULL)""")
db.commit()

#Bookings Table for Doctors
cursor.execute("""CREATE TABLE IF NOT EXISTS doctor_bookings(BookingID INT AUTO_INCREMENT PRIMARY KEY, DoctorID VARCHAR(10), UserID INT, BookingDate DATE, BookingHour TIME,
FOREIGN KEY (DoctorID) REFERENCES doctors(id),
FOREIGN KEY (UserID) REFERENCES users(LoginNumber))""")
db.commit()

#Bookings Table for Users
cursor.execute("""CREATE TABLE IF NOT EXISTS user_bookings(BookingID INT AUTO_INCREMENT PRIMARY KEY,nUserID INT, DoctorID VARCHAR(10), BookingDate DATE, BookingHour TIME,
FOREIGN KEY (UserID) REFERENCES users(LoginNumber),
FOREIGN KEY (DoctorID) REFERENCES doctors(id))""")
db.commit()

#Appointments Table
cursor.execute("""CREATE TABLE IF NOT EXISTS all_appointments(AppointmentID INT AUTO_INCREMENT PRIMARY KEY, UserID INT, DoctorID VARCHAR(10), BookingDate DATE, BookingHour TIME,
FOREIGN KEY (UserID) REFERENCES users(LoginNumber),
FOREIGN KEY (DoctorID) REFERENCES doctors(id))""")
db.commit()

#Salaries Table
cursor.execute("""CREATE TABLE IF NOT EXISTS salaries(DoctorID VARCHAR(10) PRIMARY KEY, SalaryAmount INT,FOREIGN KEY (DoctorID) REFERENCES doctors(id))""")
db.commit()

##Functions
#Show appts.
def ShowUserAppointments(UserID):
    try:
        cursor.execute("""SELECT a.AppointmentID, d.FirstName, d.LastName, a.BookingDate, a.BookingHour FROM all_appointments a
        INNER JOIN doctors d ON a.DoctorID = d.id
        WHERE a.UserID = %s""", (UserID,))

        appointments = cursor.fetchall()

        if not appointments:
            print("No appointments found for this user.")
        else:
            table = PrettyTable()
            table.field_names = ["Appointment ID", "Doctor", "Date", "Hour"]

            for appointment in appointments:
                table.add_row([appointment[0], appointment[1] + ' ' + appointment[2], appointment[3], appointment[4]])
            print("Your Appointments:")
            print(table)

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#Cancel appointments
def CancelAppointments(UserID):
    try:
        ShowUserAppointments(UserID)
        AppointmentID = input("Enter the Appointment ID you want to cancel (press 0 to go back): ")

        if AppointmentID == "0":
            return

        cursor.execute("SELECT * FROM all_appointments WHERE AppointmentID = %s AND UserID = %s", (AppointmentID, UserID))
        appointment = cursor.fetchone()

        if appointment:

            cursor.execute("DELETE FROM doctor_bookings WHERE BookingID = %s", (AppointmentID,))
            cursor.execute("DELETE FROM user_bookings WHERE BookingID = %s", (AppointmentID,))
            cursor.execute("DELETE FROM all_appointments WHERE AppointmentID = %s", (AppointmentID,))
            db.commit()
            print("Appointment canceled successfully!")
        else:
            print("Invalid Appointment ID or the appointment does not belong to you!")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#Add New Doctor
def AddDoctor(id, FirstName, LastName, specialization, gender, PhoneNumber, email):
    cursor.execute("""INSERT INTO doctors (id, FirstName, LastName, specialization, gender, PhoneNumber, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""", (id, FirstName, LastName, specialization, gender, PhoneNumber, email))
    db.commit()


#Add New User
def AddUser(username, password, gender = None, age = None, PhoneNumber = None):
    cursor.execute("""INSERT INTO users (username, password, gender, age, PhoneNumber)
        VALUES (%s, %s, %s, %s, %s)""",(username, password, gender, age, PhoneNumber))
    db.commit()

def DeleteDoctorByID(DoctorID):
    try:
        cursor.execute("SELECT * FROM doctors WHERE id = %s", (DoctorID,))
        doctor = cursor.fetchone()

        if doctor:
            cursor.execute("SELECT * FROM all_appointments WHERE DoctorID = %s", (DoctorID,))
            appointments = cursor.fetchall()

            if appointments:
                print("Cannot delete doctor! There are some appointments with this doctor.")
            else:
                cursor.execute("DELETE FROM doctors WHERE id = %s", (DoctorID,))
                db.commit()
                print("Doctor with ID {} deleted successfully.".format(DoctorID))
        else:
            print("Doctor not found.")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#Show all doctors
def DisplayDoctors():
    try:
        cursor.execute("SELECT * FROM doctors ORDER BY ID")
        doctors = cursor.fetchall()

        if not doctors:
            print("No doctors available!")
        else:
            table = PrettyTable()
            table.field_names = ["Doctor ID", "Name", "Specialization", "Gender"]

            for doctor in doctors:
                table.add_row([doctor[0], doctor[1] + ' ' + doctor[2], doctor[3], doctor[4]])

            print("Doctors available for booking:")
            print(table)
    
    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#Book appts.
def BookAppointment(UserID):
    try:
        DisplayDoctors()
        DoctorID = input("Enter the Doctor ID you want to book: ")
        BookingDate = input("Enter the booking date (YYYY-MM-DD): ")
        BookingHour = input("Enter the booking hour (HH:MM): ")

        cursor.execute(
            """INSERT INTO doctor_bookings (DoctorID, UserID, BookingDate, BookingHour) VALUES (%s, %s, %s, %s)""",
            (DoctorID, UserID, BookingDate, BookingHour)
        )
        db.commit()

        cursor.execute(
            """INSERT INTO user_bookings (UserID, DoctorID, BookingDate, BookingHour) VALUES (%s, %s, %s, %s)""",
            (UserID, DoctorID, BookingDate, BookingHour)
        )
        db.commit()

        cursor.execute(
            """INSERT INTO all_appointments (UserID, DoctorID, BookingDate, BookingHour) VALUES (%s, %s, %s, %s)""",
            (UserID, DoctorID, BookingDate, BookingHour)
        )
        db.commit()

        print("Appointment booked successfully!")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

def DisplayAllAppointments():
    try:
        cursor.execute("""SELECT a.AppointmentID, u.username, d.FirstName, d.LastName, a.BookingDate, a.BookingHour FROM all_appointments a
        LEFT JOIN users u ON a.UserID = u.LoginNumber
        LEFT JOIN doctors d ON a.DoctorID = d.id""")
        appointments = cursor.fetchall()

        if not appointments:
            print("No appointments found.")
        else:
            table = PrettyTable()
            table.field_names = ["Appointment ID", "User", "Doctor", "Date", "Hour"]

            for appointment in appointments:
                table.add_row([appointment[0], appointment[1], f"{appointment[2]} {appointment[3]}", appointment[4], appointment[5]])

            print("All Appointments:")
            print(table)
    
    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#Delete appts for a user
def DeleteUserAppointment():
    try:
        user_username = input("Enter the username of the user: ")
        cursor.execute("SELECT * FROM users WHERE username = %s", (user_username,))
        user = cursor.fetchone()

        if user:
            UserID = user[0]
            ShowUserAppointments(UserID)

            AppointmentID = input("Enter the Appointment ID you want to delete (0 to go back): ")
            if AppointmentID == "0":
                return

            cursor.execute("SELECT * FROM all_appointments WHERE AppointmentID = %s AND UserID = %s", (AppointmentID, UserID))
            appointment = cursor.fetchone()

            if appointment:
                table = PrettyTable()
                table.field_names = ["Appointment ID", "User", "Doctor", "Date", "Hour"]
                if len(appointment) >= 6:
                    table.add_row([appointment[0], user_username, "{} {}".format(appointment[2], appointment[3]), appointment[4], appointment[5]])
                    print("Deleted Appointment Details:")
                    print(table)

                cursor.execute("DELETE FROM doctor_bookings WHERE BookingID = %s", (AppointmentID,))
                cursor.execute("DELETE FROM user_bookings WHERE BookingID = %s", (AppointmentID,))
                cursor.execute("DELETE FROM all_appointments WHERE AppointmentID = %s AND UserID = %s", (AppointmentID, UserID))
                db.commit()

                print("Appointment deleted successfully!")

            else:
                print("Invalid Appointment ID or the appointment does not belong to the user.")
        else:
            print("User not found.")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))
        db.rollback()
        
#Default Salary
def SetDefaultSalary():
    cursor.execute("""UPDATE salaries SET SalaryAmount = COALESCE(SalaryAmount, 25000)""")
    db.commit()
    print("Default salary set for existing records!")

#Doctor salaries
def DisplayDoctorSalaries():
    try:
        cursor.execute("""
            SELECT d.id, d.FirstName, d.LastName, d.specialization, COALESCE(s.SalaryAmount, 25000) AS SalaryAmount
            FROM doctors d
            LEFT JOIN salaries s ON d.id = s.DoctorID""")
        salaries = cursor.fetchall()

        if not salaries:
            print("No doctor salaries found.")
        else:
            table = PrettyTable()
            table.field_names = ["Doctor ID", "Name", "Specialization", "Salary (AED)"]

            for salary in salaries:
                table.add_row([salary[0], salary[1] + ' ' + salary[2], salary[3], salary[4]])

            print("Doctor Salaries:")
            print(table)
    
    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

#update salary
def UpdateDoctorSalary():
    try:
        DisplayDoctorSalaries()
        DoctorID = input("Enter the Doctor ID for whom you want to update the salary: ")

        cursor.execute("SELECT * FROM doctors WHERE id = %s", (DoctorID,))
        doctor = cursor.fetchone()

        if doctor:
            cursor.execute("SELECT * FROM salaries WHERE DoctorID = %s", (DoctorID,))
            SalaryInfo = cursor.fetchone()
            if SalaryInfo:
                current_salary = SalaryInfo[1]
            else:
                current_salary = 25000

            NewSalary = input("Enter the new salary for " + doctor[1] + " " + doctor[2] + " (press Enter to keep it unchanged): ")

            if not NewSalary:
                NewSalary = CurrentSalary

            cursor.execute("""
                INSERT INTO salaries (DoctorID, SalaryAmount) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE SalaryAmount = %s""", (DoctorID, NewSalary, NewSalary))

            db.commit()
            print("Salary updated successfully!")
        else:
            print("Doctor not found.")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))
        db.rollback()

def GetAppointmentCounts():
    db = ConnectToDatabase()
    cursor = db.cursor()

    try:
        cursor.execute("""SELECT d.id, d.FirstName, d.LastName, COUNT(a.AppointmentID) as appointment_count FROM doctors d
        LEFT JOIN all_appointments a ON d.id = a.DoctorID
        GROUP BY d.id, d.FirstName, d.LastName""")
        appointment_counts = cursor.fetchall()

        return appointment_counts

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

    cursor.close()
    db.close()

#appts
def DisplayAppointmentsPerDoctor():
    def ConnectToDatabase():
        return mysql.connector.connect(host="localhost", user="root", password="Pr@tham06", database="HPManagementFinal")

    db = ConnectToDatabase()
    cursor = db.cursor()

    try:
        cursor.execute("""SELECT d.id, d.FirstName, d.LastName, COUNT(a.AppointmentID) as appointment_count FROM doctors d
        LEFT JOIN all_appointments a ON d.id = a.DoctorID
        GROUP BY d.id, d.FirstName, d.LastName""")
        appointment_counts = cursor.fetchall()

        if not appointment_counts:
            print("No appointment counts available.")
        else:
            table = PrettyTable()
            table.field_names = ["Doctor ID", "First Name", "Last Name", "Appointment Count"]

            for count in appointment_counts:
                table.add_row([count[0], count[1], count[2], count[3]])

            print("Appointment Counts per Doctor:")
            print(table)

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))

    cursor.close()
    db.close()


def UserExists(username, password):
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s and password = %s", (username, password))
        user = cursor.fetchone()

        if user == []:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone() is not None:
                return None
        return user

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))
        return None

def ConnectToDatabase():
    return mysql.connector.connect(host="localhost", user="root", password="Pr@tham06", database="hp")

#Search Doctors
def SearchDoctors():
    print("Search Doctors: ")
    print("1. Search by ID")
    print("2. Search by Name")
    print("3. Search by Specialization")
    print("4. Search by Gender")
    print("5. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        DoctorID = input("Enter Doctor ID: ")
        DisplayDoctorsByID(DoctorID)
    elif choice == "2":
        NameQuery = input("Enter Doctor Name (First or Last): ")
        DisplayDoctorsByName(NameQuery)
    elif choice == "3":
        specialization_query = input("Enter Specialization: ")
        DisplayDoctorsBySpecialization(specialization_query)
    elif choice == "4":
        GenderQuery = input("Enter Gender: ")
        DisplayDoctorsByGender(GenderQuery)
    elif choice == "5":
        return
    else:
        print("Invalid choice. Please try again.")

def DisplayDoctorsByID(DoctorID):
    cursor.execute("SELECT * FROM doctors WHERE id = %s", (DoctorID,))
    doctors = cursor.fetchall()
    DisplayDoctorTable(doctors)

def DisplayDoctorsByName(NameQuery):
    cursor.execute("SELECT * FROM doctors WHERE FirstName LIKE %s OR LastName LIKE %s OR (FirstName + ' ' + LastName) LIKE %s",
                   ('%' + NameQuery + '%', '%' + NameQuery + '%', '%' + NameQuery + '%'))
    doctors = cursor.fetchall()
    DisplayDoctorTable(doctors)

def DisplayDoctorsBySpecialization(specialization_query):
    cursor.execute("SELECT * FROM doctors WHERE specialization LIKE %s",('%' + specialization_query + '%',))
    doctors = cursor.fetchall()
    DisplayDoctorTable(doctors)

def DisplayDoctorsByGender(GenderQuery):
    cursor.execute("SELECT * FROM doctors WHERE gender LIKE %s", (GenderQuery,))
    doctors = cursor.fetchall()
    count = 0
    for doctor in doctors:
        count = count + 1
    DisplayDoctorTable(doctors)
    print("Number of doctors with this Gender '{}': {}".format(GenderQuery, count))

def DisplayDoctorTable(doctors):
    if not doctors:
        print("No matching doctors found.")
    else:
        table = PrettyTable()
        table.field_names = ["Doctor ID", "Name", "Specialization", "Gender"]

        for doctor in doctors:
            table.add_row([doctor[0], doctor[1] + ' ' + doctor[2], doctor[3], doctor[4]])

        print("Matching Doctors:")
        print(table)

#ADMIN
def AdminMenu():
    while True:
        print()
        print("===============================================")
        print("Welcome to the Admin Menu!")
        print("===============================================")
        print("1. Display All Doctors")
        print("2. Display All Appointments")
        print("3. Delete User Appointment")
        print("4. Display Doctor Salaries")
        print("5. Update Doctor Salaries")
        print("6. Appointment count per doctor")
        print("7. Delete Doctor")
        print("8. Search Doctors")
        print("9. Insert Doctors")
        print("10. Exit")

        print("===============================================")
        print()
        choice = str(input("Enter Choice: "))

        if choice == str(1):
            DisplayDoctors()
        elif choice == str(2):
            DisplayAllAppointments()
        elif choice == str(3):
            DeleteUserAppointment()
        elif choice == str(4):
            SetDefaultSalary()
            DisplayDoctorSalaries()
        elif choice == str(5):
            UpdateDoctorSalary()
        elif choice == "6":
            DisplayAppointmentsPerDoctor()
        elif choice == "7":
            DoctorID = input("Enter the Doctor ID you want to delete: ")
            DeleteDoctorByID(DoctorID)
        elif choice == "8":
            SearchDoctors()
        elif choice == "9":
            insertDoctor()
        elif choice == "10":
            break
        else:
            print("Invalid")

def insertDoctor():
    try:
        doctorId = input("Enter Doctor ID: ")
        firstName = input("Enter First Name: ")
        lastName = input("Enter Last Name: ")
        specialization = input("Enter Specialization: ")
        gender = input("Enter Gender: ")
        phoneNumber = input("Enter Phone Number: ")
        email = input("Enter Email: ")

        cursor.execute("""
            INSERT INTO doctors (id, FirstName, LastName, specialization, gender, PhoneNumber, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (doctorId, firstName, lastName, specialization, gender, phoneNumber, email))

        db.commit()
        print("Doctor inserted successfully!")

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))
        db.rollback()


#USER
def UserMenu(username, password):
    print("Welcome " + username + " to the User Menu!")

    try:
        UserInfo = UserExists(username, password)

        if UserInfo is not None:
            UserID = UserInfo[0]
        else:
            print("User not found. Please check your credentials.")
            return

    except mysql.connector.Error as error:
        print("Database Error: {}".format(error))


    while True:
        print()
        print("===============================================")
        print("Welcome to the User Menu!")
        print("===============================================")
        print("1. View All Doctors")
        print("2. Book an Appointment")
        print("3. View Your Appointments")
        print("4. Cancel an Appointment")
        print("5. Exit")

        print("===============================================")
        choice = input("Enter your choice: ")

        if choice == "1":
            DisplayDoctors()
        elif choice == "2":
            BookAppointment(UserID)
        elif choice == "3":
            ShowUserAppointments(UserID)
        elif choice == "4":
            CancelAppointments(UserID)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

#MAIN
while True:
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    if username == "admin" and password == "admin":
        AdminMenu()
        break
    elif UserExists(username, password) != None and UserExists(username, password):
        UserMenu(username, password)
        break
    elif UserExists(username, password) == None:
        print("Wrong username or password")
    else:
        print("User not found. Adding to the database...")
        gender = input("Enter your gender: ")
        age = int(input("Enter your age: "))
        PhoneNumber = input("Enter your phone number: ")

        AddUser(username, password, gender, age, PhoneNumber)
        print("User added to the database. Please log in again.")
