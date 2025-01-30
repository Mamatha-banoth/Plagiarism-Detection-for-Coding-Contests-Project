# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import mysql.connector

#  Set up the Selenium WebDriver
driver = webdriver.Chrome()
driver.maximize_window()  # Maximize browser window for better visibility

#  Define login credentials
username = "ajaykumarkoduri11@gmail.com"
password = "Batch@06"

#  Open the HackerRank login page
driver.get("https://www.hackerrank.com/auth/login/google")

#  Locate username and password input fields and enter credentials
username_field = driver.find_element(By.NAME, value="username")
password_field = driver.find_element(By.NAME, value="password")
username_field.send_keys(username)  # Enter the username
password_field.send_keys(password)  # Enter the password

#  Click the login button to sign in
login_button = driver.find_element(By.XPATH, value="/html/body/div[4]/div/div/div/div[2]/div[2]/div/div/div/div/div[1]/div/form/div[3]/button").click()

#  Wait for the profile menu to appear and click it
wait = WebDriverWait(driver, 10)  # Set up an explicit wait for elements to load
profile_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='profile-menu']")))
profile_menu.click()
time.sleep(2)  # Wait for the profile menu to fully load

#  Click on the Administration and Contest sections to reach the target contest page
Admin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Administration']")))
Admin_btn.click()
time.sleep(2)  # Allow time for the Administration page to load
Contest_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='True Coders Challenge2']")))
Contest_btn.click()
time.sleep(2)  # Allow time for the Contest page to load

#  Go to the Statistics section of the contest
Statistics_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Statistics']")))
Statistics_btn.click()
time.sleep(2)  # Wait for the Statistics page to load

#  Adjust browser zoom level for better visibility of all elements
driver.execute_script("document.body.style.zoom='80%'")
time.sleep(5)  # Pause for the zoom effect to apply

#  Click on the "View All" submissions button
View_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[2]/div[10]/div[1]/section[1]/div[1]/div[1]/a[1]")))
View_all_btn.click()
time.sleep(8)  # Allow time for the submissions list to load

#  Locate all submission items on the page
submissions = driver.find_elements(By.CLASS_NAME, "submissions_item")
driver.execute_script("document.body.style.zoom='75%'")  # Adjust zoom level for better visibility
time.sleep(5)

#  Set up a connection to the MySQL database
mydb = mysql.connector.connect(host="localhost", user="root", password="Password@123", database="hackerrankdata1")
cursor = mydb.cursor()

#  Create a table to store code submissions if it doesn't already exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS CodeSubmissions (
        problem_title VARCHAR(255),
        username VARCHAR(255),
        contest_name VARCHAR(255),
        id VARCHAR(255),
        language VARCHAR(255),
        time INT,
        result VARCHAR(255),
        score INT,
        srclink VARCHAR(255),
        source_code TEXT,
        PRIMARY KEY (id) )   
""")
cursor.execute("show tables;")
res = cursor.fetchall()

#  Set up lists to store submission IDs and source code links
links = []
ids = []

#  Find and click the last page button to determine total number of pages
last_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='content']/div/section/div/div/div/div[2]/div[1]/ul/li[7]/a/span[1]")))
last_btn.click()

#  Retrieve the total number of pages from the last page button
last_num_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[2]/div[10]/div[1]/section[1]/div[1]/div[1]/div[1]/div[2]/div[1]/ul[1]/li[5]/a[1]"))).text
print(int(last_num_btn))  # Display the number of pages

#  Loop through each submission page to gather data
base_url = "https://www.hackerrank.com/contests/true-coders-challenge2/judge/submissions/"
for i in range(1, int(last_num_btn)+1):
    url = f"{base_url}{i}"
    driver.get(url)  # Go to each page of submissions
    driver.execute_script("document.body.style.zoom='75%'")
    time.sleep(5)

    #  Collect details of each submission on the page
    submissions = driver.find_elements(By.CLASS_NAME, "submissions_item")
    for sub in submissions:
        try:   
            # Extract submission details
            problem_title = sub.find_element(By.XPATH, ".//div[@class='span2 submissions-title']/p/a").text
            username = sub.find_element(By.XPATH, ".//div[@class='span2 submissions-title'][2]/p/a").text
            submission_id = sub.find_element(By.XPATH, ".//div[@class='span1 submissions-title']/p").text
            ids.append(submission_id)  # Store submission ID for future reference
            language = sub.find_element(By.XPATH, ".//div[@class='span2 submissions-title'][3]/p").text
            time_taken = sub.find_element(By.XPATH, ".//div[@class='span2 submissions-title'][4]/p").text
            time_taken = int(time_taken)
            score = sub.find_element(By.XPATH, ".//div[@class='span1 submissions-title'][2]/p").text
            score = int(score)
            result = sub.find_element(By.XPATH, ".//div[@class='span3 submissions-title']/p").text

            # Insert or update submission data in the database
            cursor.execute("""
                INSERT INTO CodeSubmissions 
                (problem_title, username, contest_name, id, language, time, result, score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE source_code = VALUES(source_code), score = VALUES(score), time = VALUES(time)
            """, (problem_title, username, "True Coders Challenge2", submission_id, language, time_taken, result, score))
            mydb.commit()

            # Fetch source code link for later retrieval
            link = sub.find_element(By.XPATH, ".//div[@class='span1']/p/a").get_attribute("href")
            links.append(link)
            print("Link Found: ", link)

        except (StaleElementReferenceException, TimeoutException) as e:
            print("Error processing submission: ", e)  

print(len(links), "source code links are extracted")  # Show the number of source code links found

#  Retrieve source code from each link and update it in the database
codes = []
for link in links:
    driver.get(link)
    driver.execute_script("document.body.style.zoom='35%'")
    time.sleep(5)

    # Locate container for submission code and collect all lines of code
    submission_code_container = wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, "submission-code")))
    lines_of_code = submission_code_container.find_elements(By.TAG_NAME, 'pre')
    source_code = '\n'.join(line.text for line in lines_of_code)
    codes.append(source_code)

#  Update each submission in the database with the collected source code
print(len(ids) == len(codes))
for i in range(len(ids)):
    cursor.execute(""" 
        UPDATE CodeSubmissions 
        SET source_code = %s
        WHERE id = %s
    """, (codes[i], ids[i]))

    mydb.commit()  # Commit each update to the database

input("Press enter to exit: ")  