# logui-test-suite

This test suite is for my investigative [bachelor thesis](https://repository.tudelft.nl/islandora/object/uuid%3A3795fe80-6518-46b4-a714-9a4165091baf?collection=educationData) on Cross Browser Inconsistencies.

[LogUI](https://github.com/logui-framework/) attaches listeners to elements of [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model) (Document Object Model). When an element is interacted with, the listener is triggered which logs an entry in a log file.

I simulate an user with Selenium Webdriver and trigger different elements of a html page with simple interactions and then complex combinations of interactions hoping to find inconsistencies in how browsers log the same interactions.

## Installation
[Selenium Webdriver](https://www.selenium.dev/documentation/webdriver/getting_started/install_library/)

[Brower drivers](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)

[LogUI Server](https://github.com/logui-framework/server/wiki/First-Run-Guide)

[LogUI Client](https://github.com/logui-framework/client/wiki/Quick-Start-Guide)

PyTest

## Run Test Suite
Run test suite by running `test/test_main.py`.

## Testing More Browsers
Add your browsers in `get_browsers()` method in `main.py`.