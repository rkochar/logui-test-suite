import fileinput
import json
import os
import shutil
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.opera import OperaDriverManager

"""
LogUI did not have an API at the time of my thesis and hence I simulated API calls with Selenium (like an user would manually do it).
This file contains many of those user simulations and some other helper methods for Selenium.
"""


def has_xpath(driver, xpath):
    """
    Check if xpath exists.

    :param driver: of browser
    :param xpath: to check
    :return: boolean
    """
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except:
        return False


def element_loaded(driver, xpath, name):
    """
    Check if an element has been loaded.

    :param driver: of browser
    :param xpath: to check
    :param name: of element
    :return: boolean
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        return True
    except:
        print("Element not loaded: ", name)


def has_xpath_loaded(driver, xpath, name):
    """
    Waits for xpath of element in html page to be loaded.

    :param driver: of browser
    :param xpath: to be loaded
    :param name: of element
    :return: boolean
    """
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.XPATH, xpath))
        return driver.find_element_by_xpath(xpath=xpath)
    except:
        print('xpath getter failed: ', name)


def click_xpath(driver, xpath, name):
    """
    Click on an element in html page.

    :param driver: of browser
    :param xpath: of element
    :param name: of element
    :return: None
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

        # Clicking directly does not always work.
        element = driver.find_element_by_xpath(xpath=xpath)
        # ActionChains(driver=driver).move_to_element(element).click().perform()
        driver.execute_script("arguments[0].click();", element)
    except:
        print("Can not click: ", name)


def rightclick_xpath(driver, xpath, name):
    """
    Perform right click on element of DOM.

    :param driver: of browser
    :param xpath: of element
    :param name: of element
    :return: None
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

        # Clicking directly does not always work.
        element = driver.find_element_by_xpath(xpath=xpath)
        ActionChains(driver=driver).move_to_element(element).context_click().perform()
        # driver.execute_script("arguments[0].context_click();", element)
    except:
        print("Can not click: ", name)


def doubleclick_xpath(driver, xpath, name):
    """
    Perform double click on element of DOM>

    :param driver: of browser
    :param xpath: of element
    :param name: of element
    :return: None
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

        # Clicking directly does not always work.
        element = driver.find_element_by_xpath(xpath=xpath)
        ActionChains(driver=driver).move_to_element(element).double_click().perform()
        # driver.execute_script("arguments[0].context_click();", element)
    except:
        print("Can not click: ", name)


def login(driver):
    """
    Login to LogUI using selenium. Test password and login credentials are listed below. LogUI runs locally.

    :param driver: of browser
    :return: driver
    """
    # driver.fullscreen_window()
    driver.get("http://localhost:8000/#/user/login")
    driver.find_element_by_name("username").send_keys("test_rahul3")
    driver.find_element_by_name("password").send_keys("logui")

    # driver.find_element_by_name("password").send_keys(Keys.ENTER)
    element = driver.find_element_by_xpath("/html/body/div[1]/main/section/div[2]/form/div/button[1]")
    driver.execute_script("arguments[0].click();", element)

    return driver


def goto_application(application_index):
    """
    Login, click on Manage Application and goto application at index.

    :param application_index: in LogUI
    :return: driver
    """
    driver = get_headless_driver()
    login(driver=driver)
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[1]/a",
                name="Manage Application")
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/div[" + str(application_index) + "]/a",
                name="Click application at index")

    return driver


def get_headless_driver():
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    return webdriver.Chrome(chrome_options=chrome_options)


def make_application(application_index):
    """
    Login, click "Manage Application" and "Add new application".

    :param application_index: in LogUI.
    :return: None
    """
    driver = get_headless_driver()

    driver = login(driver=driver)
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[1]/a", name="Manage Application")
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[1]/ul/li/a", name="Add new application")

    # Make new application with datetime as name
    application_name = datetime.now().strftime("%d%m%yY%H%M%S")
    driver.find_element_by_name("name").send_keys(application_name)
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/form/div/button[1]",
                name="Add New Application (after entering details)")

    # Go to application
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/div[" + str(application_index) + "]/a",
                name="Click on application at index: " + str(application_index))
    driver.quit()


def add_new_flight(application_index, flight_name, domain):
    """
    Create flight in Selenium.

    :param application_index: in LogUI
    :param flight_name: in LogUI
    :param domain: to visit
    :return: driver
    """
    driver = goto_application(application_index=application_index)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/p[1]")))
    assert driver.find_element_by_xpath(
        "/html/body/div[1]/main/section/p[1]").text == 'Flights are the variants for each application. For example, if you are running an experiment with four conditions, your system may be run over four different variants in different locations. For this, you\'d set up a flight for each experimental variant.'

    # Add new flight
    try:
        # Open add new flight dialogue
        click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[1]/ul/li/a", name="Add New Flight")

        # Enter flight name
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/div[2]/form/label[1]/input")))
        element.find_element_by_xpath("/html/body/div[1]/main/section/div[2]/form/label[1]/input") \
            .send_keys(flight_name)

        # Enter domain
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/div[2]/form/label[1]/input")))
        element.find_element_by_xpath("/html/body/div[1]/main/section/div[2]/form/label[2]/input") \
            .send_keys(domain)

        # CLick Add New Flight button
        click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/form/div/button[1]",
                    name="Add New Flight (after filling in details)")
    except:
        print("Failed to make new flight")
    finally:
        return driver


def clear_logs(logs_directory):
    """
    Clear logs.

    :param logs_directory: directory of logs
    :return: None
    """
    for filename in os.listdir(logs_directory):
        file_path = os.path.join(logs_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def download_test_logs(application_index, flight_index, logs_directory, wait_time):
    """
    Download test logs from LogUI.

    :param application_index: of LogUI
    :param flight_index: flight whose logs will be downloaded
    :param logs_directory: directory of logs
    :param wait_time: timeout
    :return: None
    """
    chrome_options_chain = webdriver.ChromeOptions()
    chrome_options_chain.headless = True
    param = {"download.default_directory": logs_directory}
    chrome_options_chain.add_experimental_option("prefs", param)
    driver = webdriver.Chrome(chrome_options=chrome_options_chain)

    # Login, click on Manage Application and goto application at index
    login(driver=driver)
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[1]/a", name="Manage Application")
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/div[" + str(application_index) + "]/a",
                name="Click application at index")

    # CLick on download and wait to complete
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/div[" + str(flight_index) + "]/span[6]/a",
                name="Download flight log")
    time.sleep(wait_time)


def rename_logfile(flight_index, logs_directory):
    """
    Rename log file according to test suite convention.

    :param flight_index: flight whose log file will be renamed
    :param logs_directory: directory of logs
    :return:
    """
    for f in os.listdir(logs_directory):
        if f.startswith("logui-"):
            print("Renaming: ", f, "==============================")
            os.rename(logs_directory + f, logs_directory + str(flight_index) + '.log')


def disable_flight(application_index, flight_index):
    """
    Afrer a flight is completed, it no longer needs to listen to events.

    :param application_index: of LogUI
    :param flight_index: flight whose listeners will be disabled
    :return: None
    """
    driver = goto_application(application_index=application_index)

    click_xpath(driver=driver,
                xpath="/html/body/div[1]/main/section/div[2]/div[" + flight_index + "]/span[1]/a/span",
                name="Disable flight")
    driver.quit()


def get_authorization_token(driver, flight_index):
    """
    Get authorization token of flight from LogUI.

    :param driver: of browser
    :param flight_index: of flight in LogUI
    :return: authorization token
    """
    # Find and return authorization token
    click_xpath(driver=driver,
                xpath="/html/body/div[1]/main/section/div[2]/div[" + flight_index + "]/span[5]/a",
                name="Click auth token button")

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "logui-flight-authorisation-token")))

        token = driver.find_element_by_id("logui-flight-authorisation-token").get_attribute("innerHTML")
        return token
    except:
        print("Auth token not loaded")
    finally:
        driver.quit()


def check_settings():
    """
    Check settings by printing message in setting element of DOM.

    :return: message in setting element of DOM.
    """
    driver = login(webdriver.Chrome())
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[2]/a",
                name="Settings")
    print(driver.find_element_by_xpath("/html/body/div[1]/main/p").text)


def log_parser(flight_index, logs_directory):
    """
    Parse log files.

    :param flight_index: flight of LogUI
    :param logs_directory: logs directory
    :return: log data
    """
    with open(logs_directory + str(flight_index) + ".log", 'r') as log:
        log_data = json.loads(log.read())
    log.close()
    return log_data


def driver_hardcode(auth_token, file):
    assert auth_token is not None
    assert auth_token != ""

    i = 0
    existing = ""

    for line in fileinput.input(file, inplace=1):
        i += 1
        if i == 104:
            existing += '                authorisationToken: \'' + auth_token + '\',\n'
        else:
            existing += line

    with open(file, 'w') as output:
        output.write(existing)


def get_browsers():
    """
    Return list of browsers. Add browsers to list here to run in test suite.
    :return:
    """
    # return [webdriver.Chrome(), webdriver.Firefox()]
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    chrome_browser = webdriver.Chrome(chrome_options=chrome_options)

    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    firefox_browser = webdriver.Firefox(options=firefox_options)

    # safari_browser = webdriver.Safari()

    return [chrome_browser, firefox_browser]
