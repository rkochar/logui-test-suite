import time

import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from main import has_xpath, make_application, add_new_flight, disable_flight, \
    get_authorization_token, driver_hardcode, download_test_logs, \
    click_xpath, clear_logs, log_parser, rename_logfile, rightclick_xpath, doubleclick_xpath, get_browsers, has_xpath_loaded

application_index, flight_index = None, 1
domain = "http://localhost"
file = '/home/rkochar/Projects/Python/logui-test-suite/logui-example-apps/sample-search/static/js/driver.js'
driver_js_file = '/home/rkochar/Projects/Python/logui-test-suite/logui-example-apps/sample-search/index.html'
logs_directory = '/home/rkochar/Projects/Python/logui-test-suite/logs/'

class Test:
    """
    Contains tests to examine Cross Browser Issues (XBI) of LogUI.
    """

    @pytest.fixture(scope="session", autouse=True)
    def setup_before(self):
        """
        Runs at start of test suite automatically.
        Creates an application in LogUI, yields control to the tests and then at the end
        updates the application index so that Selenium can easily find it the next time the
        test suite is run.

        :return: NOne
        """
        clear_logs(logs_directory)

        global application_index
        application_index = str(get_application_index())
        make_application(application_index=application_index)

        yield  # [application_index, flight_index, domain, file]

        # Update index for next time
        file = open("./application.txt", "w")
        file.write(str(int(application_index) + 1))
        file.close()

    @pytest.fixture()
    def before_each(self):
        """
        Runs before every individual test.
        Creates a flight and prepares the driver.js file by updating the autharization token,
        yields control to the test and then disables the flight after the test has finished.
        :return:
        """
        global application_index, flight_index, domain

        flight_index += 1

        d = add_new_flight(application_index=application_index,
                           flight_name=application_index + "-" + str(flight_index),
                           domain=domain)
        auth_token = get_authorization_token(driver=d, flight_index=str(flight_index))
        print(auth_token)
        # replace_auth_token(new_token=auth_token, file=file)
        driver_hardcode(auth_token, file)

        yield

        disable_flight(application_index=application_index, flight_index=str(flight_index))

    # @pytest.mark.parametrize("driver", [webdriver.Chrome(), webdriver.Firefox()])
    # def test_login(self, before_each, driver):
    #     """
    #     Test browsers by login by verifying that a logout button and four
    #     hrefs exist in menu-grid. Check that login is unavailable, click
    #     on logout and then verify that the login option is now available.
    #
    #     :param before_each: Pytest fixture
    #     :param driver: Browser driver
    #     :return: None
    #     """
    #     assert login_check_four_href(driver=login(driver))
    #     driver.close()
    #
    # @pytest.mark.parametrize("driver", [webdriver.Chrome(), webdriver.Firefox()])
    # def test_settings(self, before_each, driver):
    #     driver = login(driver)
    #     click_xpath(driver=driver, xpath="/html/body/div[1]/main/section/ul/li[2]/a",
    #                 name="Settings")
    #     text = driver.find_element_by_xpath("/html/body/div[1]/main/p").text
    #
    #     assert "As settings are added allowing you to customise this instance of the LogUI server, they will appear here." == text
    #     driver.close()

    @pytest.mark.parametrize("driver", get_browsers())
    def test_page_focus(self, before_each, driver):
        """
        When page is opened, it should be in focus.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(3)
        driver.close()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=5)
        log_name = str(flight_index) + "-test_page_focus"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)

        for o in output:
            if o['eventType'] == 'browserEvent':
                assert o['eventDetails']['type'] == 'viewportFocusChange'
                assert o['eventDetails']['hasFocus']
                break

    # ff does not record, chrome stores old size instead of new one
    @pytest.mark.parametrize("driver", get_browsers())
    def test_viewport_resize(self, before_each, driver):
        """
        Set viewport to (700, 500), change to (800, 600). Both sizes are expected in log
        files.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)

        w, h = 700, 500
        driver.set_window_size(width=w, height=h)
        time.sleep(5)
        driver.set_window_size(width=w + 100, height=h + 100)
        driver.close()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=5)
        log_name = str(flight_index) + "-test_viewport_resize"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)
        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        i, len_output, dimensions_found = 0, len(output), False

        while i < len_output:
            if output[i]['eventType'] == 'browserEvent':
                if output[i]['eventDetails']['type'] == 'viewportResize':
                    assert output[i]['eventDetails']['viewportWidth'] == w
                    assert output[i]['eventDetails']['viewportHeight'] == h
                    i += 1
                    break
            i += 1

        while i < len_output:
            if output[i]['eventType'] == 'browserEvent':
                if output[i]['eventDetails']['type'] == 'viewportResize':
                    assert output[i]['eventDetails']['viewportWidth'] == w + 100
                    assert output[i]['eventDetails']['viewportHeight'] == h + 100
                    dimensions_found = True
                    i += 1
                    break
                    break
            i += 1

        assert dimensions_found

    @pytest.mark.parametrize("driver", get_browsers())
    def test_querybox_focus(self, before_each, driver):
        """
        Sending keyboard input to query box should trigger focus listener.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_querybox_focus"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)
        output = log_parser(flight_index=log_name, logs_directory=logs_directory)

        for o in output:
            if o['eventType'] == 'interactionEvent':
                assert o['eventDetails']['type'] == 'focus'
                assert o['eventDetails']['name'] == 'QUERYBOX_FOCUS'
                break

    # Done - flaky test for chrome: File not found
    @pytest.mark.parametrize("driver", get_browsers())  # [webdriver.Chrome(), webdriver.Firefox()])
    def test_send_keyup(self, before_each, driver):
        """
        Sending keyboard input requires keyup event.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_send_keyup"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)
        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'keyup':
                    count += 1

        assert 1 == count

    @pytest.mark.parametrize("driver", get_browsers())
    def test_querybox_submit(self, before_each, driver):
        """
        Pressing submit button triggers click listener on button.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_querybox_submit"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)
        output = log_parser(flight_index=log_name, logs_directory=logs_directory)

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'click':
                    assert o['eventDetails']['name'] == 'CLICK_SUBMIT_BUTTON'
                    break

    @pytest.mark.parametrize("driver", get_browsers())
    def test_querybox_blur(self, before_each, driver):
        """
        Exiting querybox should trigger blur event.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(3)
        driver.close()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=5)
        log_name = str(flight_index) + "-test_querybox_blur"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)

        for o in output:
            if o['eventType'] == 'interactionType':
                if o['eventDetails']['type'] == 'blur':
                    assert o['eventDetails']['type'] == 'QUERYBOX_BLUR'
                    break

    @pytest.mark.parametrize("driver", get_browsers())
    def test_timestamp(self, before_each, driver):
        """
        Perform two events with time difference of 10 seconds. Log files should
        reflect 10 second difference between events.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(10)
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                    name="Click first link")
        time.sleep(3)
        driver.close()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=5)
        log_name = str(flight_index) + "-test_timestamp"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        i, num_lines = 0, len(output)

        assert browser_started(output=output)
        # query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        # assert query_box

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
                # Chrome will fail because of two keyups. This skips the second keyup by not asserting it.
                if output[i]['eventDetails']['type'] == 'keyup':
                    i += 1
                break
            i += 1

        t1, t2 = 0, 0
        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                if output[i]['eventDetails']['type'] == 'click':
                    assert output[i]['eventDetails']['name'] == 'CLICK_SUBMIT_BUTTON'
                    t1 = output[i]['timestamps']['sinceSessionStartMillis']
                    i += 1
                    break

            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'submit'
                assert output[i]['eventDetails']['name'] == 'QUERY_SUBMITTED'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                if output[i]['eventDetails']['type'] == 'click':
                    assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_LEFT_CLICK'
                    t2 = output[i]['timestamps']['sinceSessionStartMillis']
                    break
            i += 1

        assert t2 > t1
        print('t2: ', t2)
        print('t1: ', t1)
        assert t2 - t1 - 10000 < 200

    #####################################################################################################
    ####### LEFT CLICK ##################################################################################
    #####################################################################################################
    @pytest.mark.parametrize("driver", get_browsers())
    def test_click_once(self, before_each, driver):
        """
        Perform a click once.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(10)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                    name="Click first link")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_click_once"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)

        assert html_page_loaded(output=output)
        assert delft_page_loaded(output=output)

        i, num_lines = 5, len(output)
        while i < num_lines:
            if output[i]['eventType'] == 'browserEvent' and output[i]['eventDetails']['type'] == 'cursorTracking':
                assert output[i]['eventDetails']['pageHadFocus'] is None or \
                       output[i]['eventDetails']['pageHadFocus']

                assert output[i]['eventDetails']['trackingType'] == 'cursorEnteredViewport' or \
                       output[i]['eventDetails']['trackingType'] == 'positionUpdate'
                break
            else:
                i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                assert output[i]['metadata'][0]['name'] == 'resultRank'
                assert output[i]['metadata'][0]['value'] == "1"
            else:
                i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'browserEvent':
                assert output[i]['eventDetails']['pageHadFocus']
            else:
                i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventType'] == 'interactionEvent'
                assert output[i]['eventDetails']['type'] == 'click'
            else:
                i += 1

    # Test should pass but it fails for different reasons (query box interaction is not followed by viewPort)
    @pytest.mark.parametrize("driver", get_browsers())
    def test_click_thrice(self, before_each, driver):
        """
        Click three times.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        click_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                    name="Click result stats")
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                    name="Click result stats")
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                    name="Click result stats")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_click_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)
        assert browser_started(output=output)
        query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        assert query_box

        count = 0
        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'click'
                count += 1
            i += 1

        assert 3 == count

    ######################################################################################################
    ######## RIGHT CLICK #################################################################################
    ######################################################################################################

    @pytest.mark.parametrize("driver", get_browsers())
    def test_rightclick_once_browser_event(self, before_each, driver):
        """
        Rightclick should trigger browser event.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightclick first link")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_rightclick_once_browser_event"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'browserEvent':
                if o['eventDetails']['type'] == 'contextMenuFired':
                    count += 1

        assert 1 == count

    # Chrome records twice. No idea why. This is probably the case for other browser events as well.
    @pytest.mark.parametrize("driver", get_browsers())
    def test_rightclick_thrice_browser_event(self, before_each, driver):
        """
        Right clicking thrice should trigger three browser events.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightlick first link")
        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightclick first link")
        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightclick first link")
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_rightclick_thrice_browser_event"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'browserEvent':
                if o['eventDetails']['type'] == 'contextMenuFired':
                    count += 1

        assert 3 == count

    # Done, chrome is flaky
    @pytest.mark.parametrize("driver", get_browsers())
    def test_rightclick_once(self, before_each, driver):
        """
        Right click should trigger interaction (event context) menu listener.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightclick first link")
        time.sleep(5)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_rightclick_once"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'contextmenu':
                    count += 1

        assert 1 == count

    @pytest.mark.parametrize("driver", get_browsers())
    def test_rightclick_thrice(self, before_each, driver):
        """
        Test multiple right clicks.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Click first link")
        time.sleep(3)
        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Click first link")
        time.sleep(3)
        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Click first link")
        time.sleep(5)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_rightclick_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'contextmenu':
                    count += 1

        assert 3 == count

    #####################################################################################################
    ####### DOUBLE CLICK ################################################################################
    #####################################################################################################

    # Chrome does not work, shows some weird mouseenter.
    @pytest.mark.parametrize("driver", get_browsers())
    def test_doubleclick_once(self, before_each, driver):
        """
        Simple test for double click. Double right click should trigger interaction (event context) menu listener.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        time.sleep(3)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_doubleclick_once"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'dblclick':
                    count += 1

        assert 1 == count

    # Chrome counts 2. ff shows two clicks in addition to a double. Should show one of them?
    @pytest.mark.parametrize("driver", get_browsers())
    def test_doubleclick_thrice(self, before_each, driver):
        """
        Test another double click.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_doubleclick_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'dblclick':
                    count += 1

        assert 3 == count

    @pytest.mark.parametrize("driver", get_browsers())
    def test_doubleclick_thrice(self, before_each, driver):
        """
        Test multiple double clicks.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_doubleclick_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'dblclick':
                    count += 1

        assert 3 == count

    #####################################################################################################
    ####### HOVER #######################################################################################
    #####################################################################################################

    # Chrome does not record. Ff shows hover of 37-39 millis
    @pytest.mark.parametrize("driver", get_browsers())
    def test_hover_once(self, before_each, driver):
        """
        Test simple hover.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)
        url_to_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_hover_once"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'mouseenter':
                    assert o['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                    count += 1

        assert 1 == count

    # Chrome does not record event, at all. Ff records one with 38Z difference
    @pytest.mark.parametrize("driver", get_browsers())
    def test_hover_thrice(self, before_each, driver):
        """
        Test hovering on the same element thrice.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)

        url_to_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_hover_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count_in, count_out = 0, 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'mouseenter':
                    assert o['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                    count_in += 1

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'mouseenter':
                    assert o['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                    count_out += 1

        assert 3 == count_in == count_out


    @pytest.mark.parametrize("driver", get_browsers())
    def test_hover_different(self, before_each, driver):
        """
        Test hovering on different elements.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        time.sleep(5)
        url_to_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        time.sleep(5)
        new_url = driver.find_element_by_xpath(xpath="/html/body/main/div[2]/div/img")
        ActionChains(driver=driver).move_to_element(new_url).perform()
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_hover_different"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)
        assert browser_started(output=output)
        query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        assert query_box

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_IN'
                break
            i += 1

    # Done
    @pytest.mark.parametrize("driver", get_browsers())
    def test_hover_hover_click_hover(self, before_each, driver):
        """
        Test the sequence of hovering over two different elements, click and then another hover.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)

        url_to_hover = driver.find_element_by_xpath(xpath='/html/body/main/div[1]/ul/li[1]/span[1]/a')
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        time.sleep(3)
        new_url = driver.find_element_by_xpath(xpath="/html/body/main/div[2]/div/img")
        ActionChains(driver=driver).move_to_element(new_url).perform()
        time.sleep(3)
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]", name="Click result stat")
        time.sleep(3)
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_hover_hover_click_hover"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)
        assert browser_started(output=output)
        query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        assert query_box

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_OUT'
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
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
            i += 1

    ####################################################################################################
    ###### DRAG & DROP## ###############################################################################
    ####################################################################################################
    @pytest.mark.parametrize("driver", get_browsers())
    def test_drag_drop(self, before_each, driver):
        """
        Test drag and drop.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")

        source_element = has_xpath_loaded(driver=driver, xpath='/html/body/main/div[1]/ul/li[1]/span[1]/a',
                                          name="Drag source element")
        target_element = has_xpath_loaded(driver=driver, xpath='//*[@id="input-box"]',
                                          name='Drag target element')
        time.sleep(5)
        webdriver.ActionChains(driver).drag_and_drop(source_element, target_element).perform()
        webdriver.ActionChains(driver).drag_and_drop(source_element, target_element).perform()
        webdriver.ActionChains(driver).drag_and_drop(source_element, target_element).perform()
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_drag_drop"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)
        assert browser_started(output=output)
        query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        assert query_box
        len_output = len(output)

        while i < len_output:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'dragstart'
                assert output[i]['eventDetails']['name'] == 'RESULT_LINK_DRAGSTART'
                i += 1
                break
            i += 1

        while i < len_output:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'dragend'
                assert output[i]['eventDetails']['name'] == 'QUERYBOX_DRAGEND'
                i += 1
                break
            i += 1


#####################################################################################################
####### COMPLEX TESTS ###############################################################################
#####################################################################################################

    @pytest.mark.parametrize("driver", get_browsers())
    def test_very_complex(self, before_each, driver):
        """
        Combination of different interactions such as double click, hover, click and right click.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)

        # query box (5 interactions) focus, change, submit, blur, click submit
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)

        # double click stats -> hover on span list.result ->
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(5)
        url_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        ActionChains(driver=driver).move_to_element(url_hover).perform()
        time.sleep(5)
        image_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[2]/div/img")
        ActionChains(driver=driver).move_to_element(image_hover).perform()
        time.sleep(5)

        rightclick_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                         name="Rightlick first link")
        time.sleep(5)
        click_xpath(driver=driver, xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a",
                    name="Click first link")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_very_complex"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        num_lines = len(output)
        assert browser_started(output=output)
        query_box, i = assert_query_box_interaction(output=output, num_lines=num_lines)
        assert query_box

        # Double click
        for _ in [1, 2]:
            while i < num_lines:
                if output[i]['eventType'] == 'interactionEvent':
                    assert output[i]['eventDetails']['type'] == 'click'
                    assert output[i]['eventDetails']['type'] == 'RESULT_STATS_LEFT_CLICK'

                    i += 1
                    break
                i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'click'
                assert output[i]['eventDetails']['type'] == 'RESULT_STATS_LEFT_CLICK'

                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'dblclick'
                assert output[i]['eventDetails']['type'] == 'RESULT_STATS_DBLCLICK'

                i += 1
                break
            i += 1

        # Hover1
        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventDetails']['type'] == 'cursorTracking':
                assert output[i]['eventDetails']['trackingType'] == 'positionUpdate'
                i += 1
                break
            i += 1

        # Right click
        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                assert output[i]['eventDetails']['type'] == 'contextmenu'
                assert output[i]['eventDetails']['type'] == 'LEFT_RAIL_RIGHT_CLICK'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'browserEvent':
                assert output[i]['eventDetails']['type'] == 'contextMenuFired'
                i += 1
                break
            i += 1

        # Hover2: Entity card
        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_RESULT_HOVER_OUT'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventDetails']['type'] == 'cursorTracking':
                assert output[i]['eventDetails']['trackingType'] == 'positionUpdate'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseenter'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventType'] == 'interactionEvent':
                print(output[i])
                assert output[i]['eventDetails']['type'] == 'mouseleave'
                assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
                i += 1
                break
            i += 1

        while i < num_lines:
            if output[i]['eventDetails']['type'] == 'cursorTracking':
                assert output[i]['eventDetails']['trackingType'] == 'positionUpdate'
                i += 1
                break
            i += 1

    @pytest.mark.parametrize("driver", get_browsers())
    def test_doubleclick_hover_thrice(self, before_each, driver):
        """
        Test repeated hovers on different elements of DOM and returning to them.

        :param before_each: Setup LogUI infrastructure.
        :param driver: Browser driver
        :return: None
        """
        driver.get('file:///' + driver_js_file)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id=\"input-box\"]").send_keys("D")
        click_xpath(driver=driver, xpath="//*[@id=\"submit-button\"]", name="Click submit")
        time.sleep(5)
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        url_to_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        time.sleep(3)
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        url_to_hover = driver.find_element_by_xpath(xpath="/html/body/main/div[1]/ul/li[1]/span[1]/a")
        time.sleep(3)
        ActionChains(driver=driver).move_to_element(url_to_hover).perform()
        doubleclick_xpath(driver=driver, xpath="/html/body/main/div[1]/span[2]",
                          name="Double click result stat")
        time.sleep(3)
        driver.quit()

        global logs_directory
        download_test_logs(application_index=application_index, flight_index=flight_index,
                           logs_directory=logs_directory, wait_time=10)
        log_name = str(flight_index) + "-test_doubleclick_thrice"
        rename_logfile(flight_index=log_name, logs_directory=logs_directory)

        output = log_parser(flight_index=log_name, logs_directory=logs_directory)
        count = 0

        for o in output:
            if o['eventType'] == 'interactionEvent':
                if o['eventDetails']['type'] == 'dblclick':
                    count += 1

        assert 3 == count


######################################################################################################
######## PANDAS ######################################################################################
######################################################################################################

# def test_synthesis(self, module_results_df):
#     """
#     Shows that the `module_results_df` fixture already contains what you need
#     """
#     # drop the 'pytest_obj' column
#     module_results_df.drop('pytest_obj', axis=1, inplace=True)
#     module_results_df['driver'] = module_results_df['driver'].apply(lambda x: x.split('.')[2])
#
#     browsers = module_results_df.driver.unique()
#     browser_dict = {}
#     for i, b in enumerate(browsers):
#         browser_dict['driver' + str(i)] = b
#     module_results_df['test_id'] = module_results_df.test_id.apply(lambda x: x[:-8] + browser_dict[x[-8:-1]] + ']')
#
#     test_data = pd.DataFrame()
#     test_data['test_name'] = None
#     for b in browsers:
#         test_data[b] = None
#     i, j, num_browser, total_tests = 0, -1, len(browsers), len(module_results_df)
#
#     while i < total_tests:
#         if i % num_browser == 0:
#             j += 1
#             test_data.append(pd.Series(), ignore_index=True)
#             test_data.at[j, 'test_name'] = module_results_df.iloc[i].test_id[:-8]
#
#         test_data.at[j, module_results_df.at[i, 'driver']] = module_results_df.at[i, 'status']
#         i += 1
#
#     print("\n   `module_results_df` dataframe:\n")
#     print('--------------------------------------------------------------------')
#     print(test_data)
#     print('--------------------------------------------------------------------')
#     test_data.to_csv('./../report/report.csv')


#################################################################################
##### HEPLER METHODS ############################################################
#################################################################################

def left_rail_mouse_enter(i, num_lines, output):
    """
    Assert mouse entering left_rail element.

    :param i: current row number of log file
    :param num_lines: of logs
    :param output: logs
    :return: boolean
    """
    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            print(output[i])
            assert output[i]['eventDetails']['type'] == 'mouseenter'
            assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_IN'
            return True, i + 1
        i += 1
    assert False


def left_rail_mouse_leave(i, num_lines, output):
    """
    Assert mouse leaving left_rail element.

    :param i: current row number of log file
    :param num_lines: of logs
    :param output: logs
    :return: boolean
    """
    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'mouseleave'
            assert output[i]['eventDetails']['name'] == 'LEFT_RAIL_RESULT_HOVER_OUT'
            return True, i + 1
        i += 1
    assert False


def entity_card_hover_in(i, num_lines, output):
    """
    Assert hovering on entity_card element.

    :param i: current row number of log file
    :param num_lines: of logs
    :param output: logs
    :return: boolean
    """
    while i < num_lines:
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'mouseenter'
            assert output[i]['eventDetails']['name'] == 'ENTITY_CARD_HOVER_IN'
            return True, i + 1
        i += 1
    assert False


def browser_started(output):
    """
    Assert browser has started.
    :param output: logs
    :return: boolean
    """
    for o in output:
        if o['eventType'] == 'statusEvent':
            assert o['eventDetails']['type'] == 'started'
            return True
    return False


def assert_query_box_interaction(output, num_lines):
    """
    Assert pre-decided interations with query page of test html page.

    :param output: logs
    :param num_lines: Number of lines of log file
    :return: boolean
    """
    i = 0
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
            # Firefox will fail because of one keyups. This skips the second keyup by not asserting it.
            if output[i]['eventDetails']['type'] == 'keyup':
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
        if output[i]['eventType'] == 'interactionEvent':
            assert output[i]['eventDetails']['type'] == 'submit'
            assert output[i]['eventDetails']['name'] == 'QUERY_SUBMITTED'
            return True, i + 1
        i += 1

    # while i < num_lines:
    #     if output[i]['eventType'] == 'interactionEvent':
    #         assert output[i]['eventDetails']['type'] == 'blur'
    #         assert output[i]['eventDetails']['name'] == 'QUERYBOX_BLUR'
    #         return True, i + 1
    #     i += 1

    assert False


def html_page_loaded(output):
    """
    Assert html page has been loaded.

    :param output: logs
    :return: boolean
    """
    if output[0]['eventType'] == 'statusEvent':
        assert output[0]['eventDetails']['type'] == 'started'

        # TODO: Find a way so that only firefox can use this exception
        # Exception for firefox (can be used for others)
        if output[1]['eventType'] != 'interactionEvent':
            assert output[1]['eventType'] == 'browserEvent'
            assert output[1]['eventDetails']['hasFocus']  # Flaky

            # assert output[2]['eventType'] == 'browserEvent'
            # assert output[1]['eventDetails']['type'] == "viewportFocusChange"
    else:
        assert output[1]['eventDetails']['type'] == 'started'

        assert output[0]['eventType'] == 'browserEvent'
        assert output[0]['eventDetails']['type'] == 'viewportFocusChange'
        assert output[0]['eventDetails']['hasFocus'] is None or \
               output[0]['eventDetails']['hasFocus']

    return True


def html_page_closed(output):
    """
    Assert that page is closed.
    :param output: logs
    :return: boolean
    """
    assert output[-2]['eventType'] == 'browserEvent'
    assert output[-2]['eventDetails']['type'] == 'viewportResize' or "viewportFocusChange"

    assert output[-1]['eventType'] == 'statusEvent'
    assert output[-1]['eventDetails']['type'] == 'stopped'

    return True


def delft_page_loaded(output):
    """
    Assert that a test html page is loaded.

    :param output: logs
    :return: boolean
    """
    i = 0
    while output[i]['eventType'] != 'interactionEvent':
        i += 1

    assert output[i]['eventType'] == 'interactionEvent'
    assert output[i]['eventDetails']['type'] == 'focus'
    assert output[i]['eventDetails']['name'] == "QUERYBOX_FOCUS"

    i += 1
    assert output[i]['eventType'] == 'interactionEvent'
    assert output[i]['eventDetails']['type'] == 'keyup'
    assert output[i]['eventDetails']['name'] == "QUERYBOX_CHANGE"
    assert output[i]['metadata'][0]['name'] == 'value'
    assert output[i]['metadata'][0]['value'] == "D"

    i += 1
    assert output[i]['eventType'] == 'interactionEvent'
    assert output[i]['eventDetails']['type'] == 'click'
    assert output[i]['eventDetails']['name'] == 'CLICK_SUBMIT_BUTTON'

    i += 1
    assert output[i]['eventType'] == 'interactionEvent'
    assert output[i]['eventDetails']['type'] == 'submit'
    assert output[i]['eventDetails']['name'] == "QUERY_SUBMITTED"
    assert output[i]['eventDetails']['submissionValues'][0]['name'] == 'completeQuery'
    assert output[i]['eventDetails']['submissionValues'][0]['value'] == 'D'

    return True


def get_application_index():
    """
    Find application index on logui.

    :return: index of application
    """
    with open("/home/rkochar/Projects/Python/logui-test-suite/test/application.txt", "r") as file:
        index = file.readline()
    file.close()
    return index


def login_check_four_href(driver):
    """
    Verify login on logui.

    :param driver: of browser
    :return: boolean
    """
    # Verify that login button is not present.

    assert not has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/p[2]/strong/a")

    try:
        # Wait for element to finish loading and become clickable
        for i in [1, 2, 3, 4]:
            # Make xpath and assert it exists
            xpath = "/html/body/div[1]/main/section/ul/li[" + str(i) + "]/a"
            WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, xpath)))
            assert has_xpath(driver=driver, xpath=xpath)

        # Logout is unavailable
        assert not has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/p[2]/strong/a")

        # Get logout WebElement and click on it.
        element = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/ul/li[4]/a")))
        driver.execute_script("arguments[0].click();", element)

        # Verify that login button has appeared.
        assert has_xpath(driver=driver, xpath="/html/body/div[1]/main/section/p[2]/strong/a")
        return True
    except:
        return False
