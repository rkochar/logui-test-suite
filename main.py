import sys
import time
import fileinput
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ChromeOptions, FirefoxOptions
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service
from webdriver_manager.opera import OperaDriverManager
from msedge.selenium_tools import Edge, EdgeOptions

import os
import shutil
import json

from selenium_driver_updater import DriverUpdater

def has_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except:
        return False


def element_loaded(driver, xpath, name):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        return True
    except:
        print("Element not loaded: ", name)

def get_xpath(driver, xpath, name):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(By.XPATH, xpath)
        )
        return driver.find_element_by_xpath(xpath=xpath)
    except:
        print('xpath getter failed: ', name)

def click_xpath(driver, xpath, name):
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
    # driver.fullscreen_window()
    driver.get("http://localhost:8000/#/user/login")
    driver.find_element_by_name("username").send_keys("test_rahul2")
    driver.find_element_by_name("password").send_keys("logui")

    # driver.find_element_by_name("password").send_keys(Keys.ENTER)
    element = driver.find_element_by_xpath("/html/body/div[1]/main/section/div[2]/form/div/button[1]")
    driver.execute_script("arguments[0].click();", element)

    return driver


def goto_application(application_index):
    # Login, click on Manage Application and goto application at index
    driver = webdriver.Chrome()
    login(driver=driver)
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[1]/a",
                name="Manage Application")
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/div[2]/div[" + application_index + "]/a",
                name="Click application at index")

    return driver


def login_and_logout():
    # capabilities = {'edgeOptions': {'debuggerAddress': "localhost:1212"}}
    # driver = webdriver.Edge(executable_path='/home/rkochar/Library/edgedriver_linux64/msedgedriver',
    #                capabilities=capabilities)

    # options = EdgeOptions()
    # options.use_chromium = True
    # options.binary_location = r"/home/rkochar/Library/edgedriver_linux64\msedgedriver"
    # driver = Edge(executable_path=r"/home/rkochar/Library/edgedriver_linux64\msedgedriver",
    #               options=options)  # Modify the path here...

    # driver = service.Service("~/Library/operadriver_linux64").start()
    # service.Service. setProperty("webdriver.chrome.driver", "~/Library/operadriver_linux64");

    # capabilities = {'enable-automation': True,
    #                 'useAutomationExtension': False}
    # driver = webdriver.Opera(executable_path='/home/rkochar/Library/operadriver_linux64/operadriver',
    #                          desired_capabilities=capabilities)
    # time.sleep(10)
    opera_options = ChromeOptions()
    opera_options.add_argument('--user-data-dir')
    opera_options.binary_location = '/home/rkochar/Library/operadriver_linux64/operadriver'
    capabilities = webdriver.DesiredCapabilities()
    # capabilities
    driver = webdriver.Opera(executable_path='/home/rkochar/Library/operadriver_linux64/operadriver',
                             options=opera_options)
    # driver.execute_script("window.open('');")
    #
    # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
    # ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
    # driver.get("google.com")


    # edge_options = EdgeOptions()
    # edge_options.use_chromium = True
    # capabilities = {'options': edge_options}
    # driver = webdriver.Edge(executable_path='/home/rkochar/Library/edgedriver_linux64/msedgedriver',
    #                         capabilities=capabilities)


    # ActionChains(driver).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()
    # driver.execute_script("window.open('');")
    # driver = sel.webdriver.Opera(executable_path=OperaDriverManager().install())

    # driver.find_element_by_name()

    # driver.fullscreen_window()
    # driver.execute_script("window.open('http://localhost:8000/#/user/login")
    driver = webdriver.Chrome()
    driver.get("http://localhost:8000/#/user/login")
    driver.refresh()
    driver.get("http://localhost:8000/#/user/login")
    driver.execute_script("window.open('about:blank', 'secondtab');")
    driver.find_element_by_name("username").send_keys("test_rahul2")
    driver.find_element_by_name("password").send_keys("logui")

    # driver.find_element_by_name("password").send_keys(Keys.ENTER)
    element = driver.find_element_by_xpath("/html/body/div[1]/main/section/div[2]/form/div/button[1]")
    driver.execute_script("arguments[0].click();", element)

    assert not has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/p[2]/strong/a")

    try:
        # wait 10 seconds before looking for element
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/ul/li[4]/a"))
        )
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[1]/a")
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[2]/a")
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[3]/a")
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[4]/a")
        driver.execute_script("arguments[0].click();", element)

        # Verify if login button exists
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/p[2]/strong/a")
    except:
        print("Failure")


def make_application(driver, application_index):
    # Login, click "Manage Application" and "Add new application"
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


def add_new_flight(application_index, flight_index, domain):
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
            .send_keys(flight_index)

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
    chrome_options_chain = webdriver.ChromeOptions()
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

    # Selenium does not support renaming of downloaded files.
    # Store file in logs directory, find latest and rename to "<flight_index>.log"
    # filepath = os.path.dirname(sys.argv[0]) + "/logs/"
    # filename = max([logs_directory + f for f in os.listdir(logs_directory)], key=os.path.getctime)
    # os.rename(filename, str(flight_index) + ".log")


def rename_logfile(flight_index, logs_directory):
    for f in os.listdir(logs_directory):
        if f.startswith("logui-"):
            print("Renaming: ", f, "==============================")
            os.rename(logs_directory + f, logs_directory + str(flight_index) + '.log')


def disable_flight(application_index, flight_index):
    driver = goto_application(application_index=application_index)

    click_xpath(driver=driver,
                xpath="/html/body/div[1]/main/section/div[2]/div[" + flight_index + "]/span[1]/a/span",
                name="Disable flight")
    driver.quit()


def get_authorization_token(driver, flight_index):
    # driver = goto_application(application_index=application_index)

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


def replace_auth_token(new_token, file):
    assert new_token is not None
    assert new_token != ""

    print("Token added: ", new_token)

    # file = '/home/rkochar/Projects/Python/Selenium/test/config_object.json'
    # print(os.listdir('/home/rkochar/Projects/Python/Selenium/test'))
    # assert os.path.isfile(file)

    # for f in os.listdir("./logui-example-apps/sample-search/static"):
    #     print(f)
    # with open('./logui-example-apps/sample-search/static/tmp.json', 'r') as json_object:
    with open(file, 'r') as json_object:
        tmp = json_object.read()
    json_data = json.loads(tmp)
    json_object.close()

    json_data['logUIConfiguration']['authorisationToken'] = new_token
    with open(file, "w") as outfile:
        json.dump(json_data, outfile, indent=4)
    outfile.close()


def check_settings():
    driver = login(webdriver.Chrome())
    click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[2]/a",
                name="Settings")
    print(driver.find_element_by_xpath("/html/body/div[1]/main/p").text)


def log_parser(flight_index, logs_directory):
    with open(logs_directory + str(flight_index) + ".log", 'r') as log:
        log_data = json.loads(log.read())
    log.close()
    return log_data
    # print(log_data[1].keys())
    # print(log_data[1]['applicationSpecificData']['userID'])


# def practice():
    # driver_js_file = '/home/rkochar/Projects/Python/Selenium/logui-example-apps/sample-search/index.html'
    #
    # driver = webdriver.Chrome()
    # driver.get('file:///' + driver_js_file)
    # driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
    # doubleclick_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
    #
    # rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a", name="Right click first link")
    # time.sleep(10)
    # output = log_parser(flight_index="3-test_hover_hover_click_hover", logs_directory="/home/rkochar/Projects/Python/Selenium/logs/")
    # num_lines = len(output)
    # assert browser_started(output=output)
    # query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
    # assert query_box
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         print(output[i])
    #         assert output[i]['eventDetails']['type'] == 'mouseenter'
    #         assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         assert output[i]['eventDetails']['type'] == 'mouseleave'
    #         assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         print(output[i])
    #         assert output[i]['eventDetails']['type'] == 'mouseenter'
    #         assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_IN'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         assert output[i]['eventDetails']['type'] == 'click'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         assert output[i]['eventDetails']['type'] == 'mouseleave'
    #         assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_OUT'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         print(output[i])
    #         assert output[i]['eventDetails']['type'] == 'mouseenter'
    #         assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
    #         i += 1
    #         break
    #     i += 1
    #
    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         assert output[i]['eventDetails']['type'] == 'mouseleave'
    #         assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
    #     i += 1
    #
    # assert True

# output = log_parser(flight_index="2", logs_directory="/home/rkochar/Projects/Python/Selenium/logs/")
#     data = log_parser(2, "/home/rkochar/Projects/Python/Selenium/logs/")
#     print(data)
#
#     counter = False
#     for d in data:
#         if d['browserEvents']['hasFocus'] != counter:
#             print(d['timestamps']['eventTimestamp'])
#             counter = not counter

# html_file = '/home/rkochar/Projects/Python/Selenium/logui-example-apps/sample-search/index.html'
# driver = webdriver.Chrome()
# driver.get('file:///' + html_file)
# driver.fullscreen_window()
# print(driver.find_element_by_xpath('/html/body/main/div[1]/span[1]/p[2]/strong').text)
#
# print(driver.find_element_by_xpath('/html/body/main/div[1]/span[1]/p[3]').text)
#
# driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("a")
# click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")


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
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    chrome_browser = webdriver.Chrome(chrome_options=chrome_options)

    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    firefox_browser = webdriver.Firefox(firefox_options=firefox_options)

    return [chrome_browser, firefox_browser]

# def browser_started(output):
#     for o in output:
#         if o['eventType'] == 'statusEvent':
#             assert o['eventDetails']['type'] == 'started'
#             return True
#     return False


def assert_query_box_interaction(output, num_lines):
    i = 0
    # while i < num_lines:
    #     if output[i]['eventType'] == 'browserEvent':
    #         assert output[i]['eventDetails']['hasFocus']
    #         i += 1
    #         break
    #     i += 1

    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'focus'
            assert output[i]['eventDetails']['name'] == 'QUERYBOX_FOCUS'
            i += 1
            break
        i += 1

    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'keyup'
            assert output[i]['eventDetails']['name'] == 'QUERYBOX_CHANGE'
            i += 1
            break
        i += 1

    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            # Chrome will fail because of two keyups. This skips the second keyup by not asserting it.
            if output[i]['eventDetails']['type'] == 'submit':
                assert output[i]['eventDetails']['name'] == 'QUERY_SUBMITTED'
                i += 1
                break
        i += 1

    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'click'
            i += 1
            break
        i += 1

    while i < num_lines:
        if output[i]['eventType'] == 'browserEvent':
            assert output[i]['eventDetails']['type'] == 'viewportFocusChange' or 'viewportResize'
            return True, i + 1
            break
        i += 1

    assert False

if __name__ == '__main__':
#     rename_logfile(69, '/home/rkochar/Projects/Python/Selenium/logs/')
#     logs_directory = ""
#     for x in os.getcwd().split('/')[:-1]:
#         logs_directory += x + "/"
#     # logs_directory += "logs/"
#     download_test_logs(120, 2, logs_directory, 5)

# disable_flight(sel.webdriver.Chrome(), 2, 2)
# driver_hardcode("abcd")
#     # replace_auth_token("abcd")
#     login_and_logout()
    login_and_logout()
# print(log_parser(1))
# login_and_logout()
# make_application(sel.webdriver.Chrome(), 3)
# add_new_flight(sel.webdriver.Chrome(), "test3", "", 5)

# chrome_options_chain = webdriver.ChromeOptions()
# param = {"download.default_directory": "/home/rkochar/Projects/Python/Selenium/logs"}
# chrome_options_chain.add_experimental_option("prefs", param)
# driver_chrome = webdriver.Chrome(chrome_options=chrome_options_chain)
# get_authorization_token(sel.webdriver.Chrome(), 2, 2)
# replace_auth_token(get_authorization_token(sel.webdriver.Chrome(), 2, 2))
# check_settings()
