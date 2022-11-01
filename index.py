# importing the required modules
import sys
import time
import mysql.connector
from prettytable import SINGLE_BORDER, PrettyTable
import maskpass         # doesn't work in Python IDLE 

# getting the mysql password 
password = maskpass.askpass(prompt="\nEnter password for root user : ")

# connecting to MySql
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    # passwd=input("\nEnter password for root user : ")
    passwd=password  
)

print("\nConnecting to the database........")
time.sleep(1)

# checking if connection made successfully or not
if mydb.is_connected():
    print("\nConnection made successfully........")
    time.sleep(1)
else:
    print("\nSomething went wrong.....")
    time.sleep(1)

# making the cursor object
cursor = mydb.cursor()

# creating the database
cursor.execute("CREATE DATABASE IF NOT EXISTS project")
cursor.execute("USE project")

# creating the table
cursor.execute(
    "CREATE TABLE IF NOT EXISTS students"
    "(adm_no INT(4) PRIMARY KEY UNIQUE NOT NULL, "
    "class INT(4) NOT NULL, "
    "roll_no INT(4) NOT NULL, "
    "student_name VARCHAR(40) NOT NULL, "
    "math_marks DOUBLE(4,1) NOT NULL, "
    "phy_marks DOUBLE(4,1) NOT NULL, "
    "chem_marks DOUBLE(4,1) NOT NULL, "
    "eng_marks DOUBLE(4,1) NOT NULL, "
    "comp_marks DOUBLE(4,1) NOT NULL, "
    "total DOUBLE(4,1), "
    "CGPA DOUBLE(4,1))")

# updating the total and CGPA column
total_marks = "UPDATE students SET total = math_marks+phy_marks+" \
              "chem_marks+eng_marks+comp_marks"

cursor.execute(total_marks)
mydb.commit()

CGPA_marks = "UPDATE students SET CGPA = (total/5)/8"

cursor.execute(CGPA_marks)
mydb.commit()

# creating a trigger for updating total value as soon as a new row is inserted
try:
    cursor.execute("CREATE TRIGGER total "
                   "BEFORE INSERT ON students FOR EACH ROW "
                   "SET NEW.total = NEW.math_marks + NEW.phy_marks + "
                   "NEW.chem_marks + NEW.eng_marks + NEW.comp_marks ;")
    mydb.commit()
except Exception as e:
    error_trigger_insert_total = e
    code = e.errno
    if code==1359:
        pass
    else:
        print(e)

# creating a trigger for updating CGPA value as soon as a new row is inserted
try:
    cursor.execute("CREATE TRIGGER cgpa "
                   "BEFORE INSERT ON students FOR EACH ROW "
                   "SET NEW.CGPA = ((NEW.math_marks + NEW.phy_marks + "
                   "NEW.chem_marks + NEW.eng_marks + NEW.comp_marks)/5)/8 ;")
    mydb.commit()
except Exception as e:
    error_trigger_insert_cgpa = e
    code = e.errno
    if code==1359:
        pass
    else:
        print(e)

# trigger for updating total value when any row is updated
try:
    cursor.execute("CREATE TRIGGER after_update_total "
                   "BEFORE UPDATE ON students FOR EACH ROW "
                   "SET NEW.total = NEW.math_marks + NEW.phy_marks + "
                   "NEW.chem_marks + NEW.eng_marks + NEW.comp_marks ;")
    mydb.commit()
except Exception as e:
    error_trigger_update_total = e
    code = e.errno
    if code==1359:
        pass
    else:
        print(e)

# trigger for updating CGPA value when any row is updated
try:
    cursor.execute("CREATE TRIGGER after_update_CGPA "
                   "BEFORE UPDATE ON students FOR EACH ROW "
                   "SET NEW.CGPA = ((NEW.math_marks + NEW.phy_marks + "
                   "NEW.chem_marks + NEW.eng_marks + NEW.comp_marks)/5)/8 ")
    mydb.commit()
except Exception as e:
    error_trigger_update_cgpa = e
    code = e.errno
    if code==1359:
        pass
    else:
        print(e)


# defining all the functions
def execute(qry):
    """
    Executes a query given in form of string.
    """
    cursor.execute(qry)


def display(table_data, choice):
    """
    Takes in the table data and 
    choice prints a table out of it.
    """
    table = PrettyTable()

    if choice == 1 or choice == 2:
        headings = ["Adm no.", "Roll no.", "Student Name", "Maths Marks", "Physics Marks",
                    "Chemistry Marks", "English Marks", "Computer marks", "Total", "CGPA"]
    elif choice == 3:
        headings = ["Rank", "Roll no.", "Student Name", "Maths Marks", "Physics Marks",
                    "Chemistry Marks", "English Marks", "Computer marks", "Total", "CGPA"]
    table.field_names = headings

    for i in table_data:
        table.add_row(i)

    table.padding_width = 3
    table.border = True
    table.set_style(SINGLE_BORDER)

    print(table)


def view_all(_class):
    """
    Takes in the students' class as an argument
    and views all data in the form of a table.
    """
    flag = 0
    choice = 1
    try:
        qry = "SELECT adm_no, roll_no, student_name, math_marks, phy_marks, " \
              "chem_marks, eng_marks, comp_marks, total, CGPA FROM students " \
              "WHERE class = {} ORDER BY roll_no".format(_class)
        execute(qry)
        data = cursor.fetchall()
    except Exception as e:
        print("\n------ Error : ", e, " ------")
        time.sleep(2)
        flag = 1

    if flag == 0:
        if data == []:
            print("\n---------- Value not found. "
                  "Please check if this is present in database. ----------")
            time.sleep(2)
        else:
            display(data, choice)
    else:
        print("\n--------- Oops!!! Something went wrong. "
              "Please check your input data and try again. ---------")
        time.sleep(2)


def check(_class, _rollno):
    """
    Takes in the class and roll non as arguments
    and views the details of a single student.
    """
    flag = 0
    choice = 2
    try:
        qry = "SELECT adm_no, roll_no, student_name, math_marks, phy_marks, " \
              "chem_marks, eng_marks, comp_marks, total, CGPA FROM students " \
              "WHERE class = {} AND roll_no = {}".format(_class, _rollno)
        execute(qry)
        data = cursor.fetchall()
    except Exception as e:
        print("\n------ Error : ", e, " ------")
        time.sleep(2)
        flag = 1
    if flag == 0:
        if data == []:
            print("\n---------- Value not found. "
                  "Please check if this is present in database. ----------")
            time.sleep(2)
        else:
            display(data, choice)
            print("\n")
    else:
        print("\n--------- Oops!!! Something went wrong. "
              "Please check your input data and try again. ---------")
        time.sleep(2)


def topper(_class):
    """
    Takes in the class as argument and views the
    details of top 3 students in the class.
    """
    flag = 0
    choice = 3
    try:
        qry = "SELECT RANK() over (ORDER BY CGPA DESC) Rankings, roll_no, " \
              "student_name, math_marks, phy_marks, chem_marks, eng_marks, " \
              "comp_marks, total, CGPA FROM students WHERE class = {} " \
              "ORDER BY CGPA DESC LIMIT 3".format(_class)
        execute(qry)
        data = cursor.fetchall()
    except Exception as e:
        print("\n------ Error : ", e, " ------")
        time.sleep(2)
        flag = 1
    if flag == 0:
        if data == []:
            print("\n---------- Value not found. "
                  "Please check if this is present in database. ----------")
            time.sleep(2)
        else:
            display(data, choice)
            print("\n")
    else:
        print("\n--------- Oops!!! Something went wrong. "
              "Please check your input data and try again. ---------")
        time.sleep(2)


def add(list_of_data):
    """
    Takes in the list of all the data of a student 
    as argument and adds the details to the table.
    """
    flag = 0
    try:
        qry = "INSERT INTO students (adm_no, class, roll_no, student_name, " \
              "math_marks, phy_marks, chem_marks, eng_marks, comp_marks) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        dat = list_of_data
        cursor.executemany(qry, dat)
        mydb.commit()
        if cursor.rowcount == 0:
            print("\n---------- Value not found. "
                  "Please check if this is present in database. ----------")
            time.sleep(2)
        else:
            print("\n------ ", cursor.rowcount, " row(s) added successfully. ------\n")
    except Exception as e:
        code = e.errno
        if code == 1366:
            print("\n-------- Please fill all the details correctly. " 
                  "Filling every detail is mandatory. --------\n")
            print("------- This value was not inserted ------")
            time.sleep(2)
        else:
            print("\n------ Error : ", e, " ------")
            time.sleep(2)
            flag = 1
    if flag != 0:
        print("\n--------- Oops!!! Something went wrong. "
              "This value was not inserted. ---------")
        time.sleep(2)


def update(_class, _rollno, adm_no):
    """
    Takes in the class, roll no. amd adm no. as 
    arguments and updates the details of a single student.
    """
    print(
        "\n-----Enter what you want to update-----\n"
        "\n1) Class"
        "\n2) Roll no."
        "\n3) Name"
        "\n4) Maths Marks"
        "\n5) Physics Marks"
        "\n6) Chemistry Marks"
        "\n7) English Marks"
        "\n8) Computer science Marks"
        "\n9) Exit the update section"
    )
    choice = input('\nEnter your choice - ')

    if not choice.isnumeric():
        print("\nPlz check your input and try again.....")
        update(_class, _rollno, adm_no)
        time.sleep(1)

    elif int(choice) == 1:
        nclass = input("\nEnter the new class of the student = ")
        _update(nclass, "class", _class, _rollno, adm_no)
        update(nclass, _rollno, adm_no)

    elif int(choice) == 2:
        nrollno = input("\nEnter the new rollno of the student = ")
        _update(nrollno, "roll_no", _class, _rollno, adm_no)
        update(_class, nrollno, adm_no)

    elif int(choice) == 3:
        nname = input("\nEnter the new name of the student = ")
        _update(nname, "student_name", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 4:
        nmaths = input("\nEnter the new math marks of the student = ")
        _update(nmaths, "math_marks", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 5:
        nphy = input("\nEnter the new phy marks of the student = ")
        _update(nphy, "phy_marks", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 6:
        nchem = input("\nEnter the new chem marks of the student = ")
        _update(nchem, "chem_marks", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 7:
        neng = input("\nEnter the new eng marks of the student = ")
        _update(neng, "eng_marks", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 8:
        ncs = input("\nEnter the new cs marks of the student = ")
        _update(ncs, "comp_marks", _class, _rollno, adm_no)
        update(_class, _rollno, adm_no)

    elif int(choice) == 9:
        start()

    elif int(choice) > 9:
        print("\nPlz choose from the given options and try again.")
        update(_class, _rollno, adm_no)
        time.sleep(1)


def _update(new, value, _class, _rollno, adm_no):
    """
    Takes in the updated value, name of value, class, roll no. 
    and adm no. of the students and updates the value.
    """
    flag = 0
    try:
        if value == "student_name":
            qry = "UPDATE students SET {} = '{}' WHERE class = {} " \
                  "AND roll_no = {} AND adm_no = {}".format(
                value, new, _class, _rollno, adm_no
                )
        else:
            qry = "UPDATE students SET {} = '{}' WHERE class = {} " \
                  "AND roll_no = {} AND adm_no = {}".format(
                value, new, _class, _rollno, adm_no
                )
        execute(qry)
        mydb.commit()
        if cursor.rowcount == 1:
            print("\n------- Data updated successfully. ------")
            time.sleep(1)
        else:
            print("\n------ Either you've entered the same value as the previous "
                  "value or there is no such value present in the database. "
                  "Plz try again. ------")
            time.sleep(3)
    except Exception as e:
        print("\n------ Error : ", e, " ------")
        time.sleep(2)
        flag = 1
    if flag != 0:
        print("\n--------- Oops!!! Something went wrong. "
              "Please check your input data and try again. ---------")
        time.sleep(2)


def delete(_class, _rollno):
    """
    Takes in the class and roll non as arguments
    and deletes the details of a single student.
    """
    flag = 0
    try:
        qry = "DELETE FROM students WHERE class = {} AND " \
              "roll_no = {}".format(_class, _rollno)
        execute(qry)
        mydb.commit()
        if cursor.rowcount == 1:
            print("\n--------- Data deleted successfully. ---------")
            time.sleep(0.5)
        else:
            print("\n---------- Value not found. "
                  "Please check if this is present in database. ----------")
            time.sleep(2)
    except Exception as e:
        print("\n------ Error : ", e, " ------")
        time.sleep(2)
        flag = 1
    if flag != 0:
        print("\n--------- Oops!!! Something went wrong. "
              "Please check your input data and try again. ---------")
        time.sleep(2)
        start()


def exit():
    """
    Commits all changes, disconnects the connection and exits.
    """
    print("\nThank you, and visit again.....")
    time.sleep(2)
    mydb.commit()
    mydb.close()
    sys.exit()


def start():
    """
    This is the main choice window.
    """
    print('\n')
    print(
        "##########  WELCOME TO STUDENT REPORT MANAGEMENT SYSTEM  ##########\n"
        "\n          Enter 1 : To view details of all Students"
        "\n          Enter 2 : To check details of a particular Student"
        "\n          Enter 3 : To view the Toppers' list"
        "\n          Enter 4 : To add new Students"
        "\n          Enter 5 : To update data of a Student"
        "\n          Enter 6 : To delete the data of a Student"
        "\n          Enter 7 : To commit all changes and exit\n"
    )

    choice = input('Enter your choice - ')

    if not choice.isnumeric():
        print("\nPlz check your input and try again.....")
        time.sleep(1)
        start()

    elif int(choice) == 1:
        print("\nWhich class data you wanna see : ", end="")
        _class = input()
        view_all(_class)
        start()

    elif int(choice) == 2:
        _class = input("\nEnter the class the student belongs to : ")
        rollno = input("\nEnter the roll no. of the student : ")
        check(_class, rollno)
        start()

    elif int(choice) == 3:
        _class = input("\nEnter the class of which you wanna see toppers' list : ")
        topper(_class)
        start()

    elif int(choice) == 4:
        n = int(input("\nEnter the number of students you wanna add = "))
        i = 0
        while i < n:
            try:
                print("\nEnter the name of student ", i + 1, " = ", end="")
                name = input()
                print("\nEnter the class of student ", i + 1, " = ", end="")
                _class = input()
                print("\nEnter the roll no. of student ", i + 1, " = ", end="")
                rollno = input()
                print("\nEnter the maths marks of student ", i + 1, " = ", end="")
                math_marks = input()
                print("\nEnter the physics marks of student ", i + 1, " = ", end="")
                phy_marks = input()
                print("\nEnter the chemistry marks of student ", i + 1, " = ", end="")
                chem_marks = input()
                print("\nEnter the english marks of student ", i + 1, " = ", end="")
                eng_marks = input()
                print("\nEnter the computer sc. marks of student ", i + 1, " = ", end="")
                comp_marks = input()
                print("\nEnter the admission number of student ", i + 1, " = ", end="")
                adm_no = input()

                lst = [(adm_no, int(_class), int(rollno), name, float(math_marks), 
                        float(phy_marks), float(chem_marks), float(eng_marks), float(comp_marks))]
                add(lst)
            except ValueError:
                print("\n-------- Please fill all the details correctly. " 
                  "Filling every detail is mandatory. --------\n")
                print("------- This value was not inserted ------\n")
                time.sleep(2)
            except Exception:
                print("\n--------- Oops!!! Something went wrong. "
                      "Please check your input data and try again. ---------")
                time.sleep(2)
            i += 1

        start()

    elif int(choice) == 5:
        _class = input("\nEnter the class the student belongs to : ")
        _rollno = input("\nEnter the roll no. of the student : ")
        adm_no = input("\nEnter the admission no. of the student : ")
        update(_class, _rollno, adm_no)
        start()

    elif int(choice) == 6:
        _class = input("\nEnter the class the student belongs to : ")
        rollno = input("\nEnter the roll no. of the student : ")
        delete(_class, rollno)
        start()

    elif int(choice) == 7:
        exit()

    else:
        print("\n----------Please enter from the given choices.----------")
        time.sleep(1)
        start()


# calling the start function
start()
