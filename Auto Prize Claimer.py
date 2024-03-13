from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import threading

def login_and_claim(username, pw, claim_key):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu") # Disable GPU acceleration
    chrome_options.add_argument("--window-size=1920x1080")  # Set the window size
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://live.hackmerced.com')

    badge_code_xpath = '//*[@id="uid"]'
    password_xpath = '//*[@id="password"]'
    login_button_xpath = '//*[@id="login-form"]/div/center/form/input[2]'
    login_button2_xpath = '//*[@id="login-form"]/div/center/form/input[3]'
    error_message_xpath = '//*[@id="login-form"]/div/center/p'
    prizes_xpath = '//*[@id="navbar"]/div[3]/a'
    claim_xpath = claim_paths[claim_key]

    try:
        # Fill in the badge code and attempt to login
        badge_code = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, badge_code_xpath)))
        badge_code.send_keys(username)
        login_button = driver.find_element(By.XPATH, login_button_xpath)
        login_button.click()

        # Check for an error message explicitly
        try:
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, error_message_xpath)))
            error_message = driver.find_element(By.XPATH, error_message_xpath).text
            print(f"Login failed for {username}. Error message: {error_message}")
            driver.quit()
            return
        except TimeoutException:
            print(f"Login successful for {username}!\n")
    except Exception as e:
        print(f"An error occurred while logging in for {username}: {str(e)}")
        driver.quit()
        return

    # Password entry
    password = driver.find_element(By.XPATH, password_xpath)
    login_button2 = driver.find_element(By.XPATH, login_button2_xpath)
    password.send_keys(pw)
    login_button2.click()

    # Navigate to the prizes page
    prizes = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.XPATH, prizes_xpath)))
    prizes.click()

    # Wait for the prizes page to load properly
    time.sleep(1.5)
    
    # Loop for claiming the prize
    success = False
    while not success:
        try:
            # Attempt to claim the prize
            claim = driver.find_element(By.XPATH, claim_xpath)
            claim.click()

            # Wait for the first alert and handle it
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            confirmation_alert = Alert(driver)
            confirmation_alert_text = confirmation_alert.text  # Capture the text of the first alert
            confirmation_alert.accept()  # Accept the first alert to proceed with the claim

            # Wait for the second alert and handle it
            try:
                WebDriverWait(driver, 1).until(EC.alert_is_present())
                result_alert = Alert(driver)
                result_alert_text = result_alert.text  # Capture the text of the second alert
                result_alert.accept()  # Accept the second alert

                # Now check the text that was captured from the second alert
                if "success" in result_alert_text.lower():
                    print(f"Claim successful for {username}! Redeemed: {confirmation_alert_text}")
                    success = True
                else:
                    print(f"Claim failed for {username}. Reason: {result_alert_text}\n")
                    time.sleep(1)  # Wait before trying again
            except TimeoutException:
                # If there is no second alert, then the claim was successful
                print(f"Claim successful for {username}! Redeemed: {claim_paths}")
                success = True
        except Exception as e:
                # If there is any other exception, print the error and continue
                print(f"An error occurred while claiming for {username}: {str(e)}")
                time.sleep(1)  # Wait before trying again

    # Finish and close the driver
    driver.quit()

# Claim Paths ("Name of Prize": "XPath of Claim Button")

claim_paths = {
    "arduino_robotics_arm_kit": '//*[@id="1"]/td[5]/button',
    "pcb_ruler": '//*[@id="2"]/td[5]/button',
    "attiny88_boards": '//*[@id="3"]/td[5]/button',
    "full_dive_sticker": '//*[@id="4"]/td[5]/button',
    "raccoon_sticker": '//*[@id="5"]/td[5]/button',
    "sticker_page": '//*[@id="6"]/td[5]/button',
    "arduino_uno_r3": '//*[@id="7"]/td[5]/button',
    "microsd_card_breakout": '//*[@id="8"]/td[5]/button',
    "nothing": '//*[@id="12"]/td[5]/button',
}

# Login Credentials ("Badge Code", "Password", "Name of Prize")

login_info = [
    ("BADGE CODE", "PASSWORD", "Name from claim_paths"),
]


# Create threads for each set of credentials
threads = []
for username, pw, claim_key in login_info:
    thread = threading.Thread(target=login_and_claim, args=(username, pw, claim_key))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()