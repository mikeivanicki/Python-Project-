# webadv_audit.py
# Michael Ivanicki (s1321890), Daniel McGarry (s1317786), Dennis Vaccaro (s0984094)
# CS 371
# Spring 2023

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import re
import getpass
import autoit

# Help function
def help():
    print("""This Python script retrieves your academic audit and prints a summary.
It can optionally save a PDF copy of your entire audit.


Usage: python3 webadv_audit.py [--option] [student id, e.g., s1100841]
   where [--option] can be:
      --help:	     Display this help information and exit
      --save-pdf: Save PDF copy of entire audit to the current folder
                  as audit.pdf
""")
    sys.exit(1)

# Checking to see if proper amount of commandline arguments were given
if (len(sys.argv) != 2 and len(sys.argv) != 3):
    help()

# Checking to see if help function is being called by user
if re.search('-h', sys.argv[1]):
    help()

# Checking to see if save function is being called by user, and remembering the option to call the function later when needed in the 'save' boolean variable
if re.search('-s', sys.argv[1]):
    save_pdf = True
else:
    save_pdf = False

# Saving the command line arguments to a variable
userID = re.search('s\d{7}', sys.argv[len(sys.argv) - 1]).group(0)

# Asking user to input their password
password = getpass.getpass(f"Enter the password for {userID}: ")

# Setting up webdriver

driver = webdriver.Chrome()

driver.get('https://webadvisor.monmouth.edu')

# Find and click the login button
time.sleep(3)
login = driver.find_element(By.ID, 'acctLogin')
login.click()

# Finds and clears the username field before entering the email
enter_user = driver.find_element(By.NAME,'UserName')
enter_user.clear()
time.sleep(2)
enter_user.send_keys(userID)
time.sleep(2)
enter_user.send_keys(Keys.RETURN)

# Finds and clears the password field before entering the password
enter_password = driver.find_element(By.NAME,'Password')
enter_password.clear()
time.sleep(2)
enter_password.send_keys(password)
time.sleep(2)
enter_password.send_keys(Keys.RETURN)

# Checks to see if the credentials entered were correct
try:
    assert 'WebAdvisor Main Menu' in driver.title
except AssertionError:
    sys.exit("Incorrect user ID or Password. Exiting.")


# Clicks on the student menu
studentBar = driver.find_element(By.CLASS_NAME,'WBST_Bars')
studentBar.click()

# Clicks the Academic Audit/Program Evaluation link
auditLink = driver.find_element(By.XPATH,"//div[@id='bodyForm']//div[@class='right']/ul[1]/li[4]/a[@alt='@desc']/span[.='Academic Audit/Pgm Eval']")
auditLink.click()

# Selects the first active program
activeProgram = driver.find_element(By.ID, 'LIST_VAR1_1')
activeProgram.click()

# Clicks the submit button
submitButton = driver.find_element(By.NAME, 'SUBMIT2')
submitButton.click()


# Parsing the audit for the required information:
print(""" Audit Summarry:
=================""")

# Finding Name and ID by its XPATH
student = driver.find_element(By.XPATH, '//*[@id="StudentTable"]/tbody/tr[2]/td/strong')
print(student.text)

# Finding Program by its XPATH
program = driver.find_element(By.XPATH, '//*[@id="StudentTable"]/tbody/tr[3]/td/table/tbody/tr[1]/td[2]')
print(f'Program: {program.text}')

# Finding Catalog by its XPATH
catalog = driver.find_element(By.XPATH, '//*[@id="StudentTable"]/tbody/tr[3]/td/table/tbody/tr[2]/td[2]')
print(f'Catalog: {catalog.text}')

# Finding Anticipated Completion Date by its XPATH
completion_date = driver.find_element(By.XPATH, '//*[@id="StudentTable"]/tbody/tr[3]/td/table/tbody/tr[3]/td[2]')
print(f'Anticipated Completion Date: {completion_date.text}')

# Finding advisor within a WebElement that contains a lot of text, since the advisor itself is just text and cannot be found by the driver. It is found by removing the stock text above the information
# and using regex on the remaining text to find the data needed
parsed_text = driver.find_element(By.XPATH, '//*[@id="StudentTable"]/tbody/tr[4]/td')
parsed_text = parsed_text.text

replace_str = """This academic audit *MUST* be used in conjunction with your
curriculum chart, and regular meetings with your academic
advisor(s) to track your progress towards program completion.

The number of required overall credits reflects the minimum number
of credits needed to earn a degree a Monmouth University. Individual
programs may require additional credits to earn your degree.

Courses which receive a transitory grade (i.e. 'S'atisfactory
Progress, 'I'ncomplete) will not reflect in the requirement as
completed until a final grade has been recorded.

Any discrepancies in this audit are not binding."""

parsed_text = parsed_text.replace(replace_str, "")
parsed_text = parsed_text.replace("\n\n", "")

advisor_pattern = r"Advisor.+"
advisor = re.match(advisor_pattern, parsed_text).group(0)

print(advisor)

# Class Level (using same parsed text as above)
parsed_text = parsed_text.replace(f'{advisor}\n', "")

class_level_pattern = r"Class Level.+"
class_level = re.match(class_level_pattern, parsed_text).group(0)

print(class_level)

# Finding Graduation Requirements that are In Progress and Not Started through finding all requirements using the class name "ReqName", and using regex to determine whether or not it has been started
grad_requirements = driver.find_elements(By.CLASS_NAME, 'ReqName')

in_progress_pattern = r".+In progress\)"
not_started_pattern = r".+Not started\)"

in_progress = []
not_started = []

for req in grad_requirements:
    req = req.text

    test = re.match(in_progress_pattern, req)
    if test is not None:
        in_progress.append(test.group(0))


    test2 = re.match(not_started_pattern, req)
    if test2 is not None:
        not_started.append(test2.group(0))

print("Graduation Requirements In Progress: ")
for element in in_progress:
    print(f'{element}')

print("Graduation Requirements Not Started: ")
for element in not_started:
    print(f'{element}')

# Finding Credits at the 200 level in the same way as advisor and class level, but with different text
parsed_data = driver.find_element(By.XPATH, "/html//table[@id='StudentTable']/tbody/tr[8]/td/table[6]//table[@id='ReqTable']/tbody/tr[2]/td")
parsed_data = parsed_data.text

credits_pattern = r"Credits Earned.+"

high_credits = re.match(credits_pattern, parsed_data).group(0)

print(f"{high_credits} (at 200 level)")

# Finding Total Earned Credits by its XPATH
credits = driver.find_element(By.XPATH, '//*[@id="SummaryTable"]/tbody/tr[4]/td[3]')
print(f'Total credits earned: {credits.text}')

# Printing to PDF if the user inputs the option
if save_pdf == True:

    driver.maximize_window()
    autoit.send("^p")
    time.sleep(5)

    autoit.send("{Enter}")
    time.sleep(5)

    autoit.send("audit.pdf")
    time.sleep(5)

    autoit.send("{Enter}")

# Closing driver
driver.close()