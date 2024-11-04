#-----------------------------------------------------------------------
# testregdetails.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

#-----------------------------------------------------------------------

def get_args():

    parser = argparse.ArgumentParser(
        description='Test the ability of the reg application to '
            + 'handle "secondary" (class details) queries')

    parser.add_argument(
        'serverURL', metavar='serverURL', type=str,
        help='the URL of the reg application')

    parser.add_argument(
        'browser', metavar='browser', type=str,
        choices=['firefox', 'chrome'],
        help='the browser (firefox or chrome) that you want to use')

    parser.add_argument(
        'mode', metavar='mode', type=str,
        choices=['normal','headless'],
        help='the mode (normal or headless) that this program should '
            + 'use when interacting with Firefox; headless tells '
            + 'Firefox not to display its window and so is faster, '
            + 'especially when using X Windows')

    parser.add_argument(
        'delay', metavar='delay', type=int,
        help='the number of seconds that this program should delay '
            + 'between interactions with Firefox')

    args = parser.parse_args()

    return (args.serverURL, args.browser, args.mode, args.delay)

#-----------------------------------------------------------------------

def create_driver(browser, mode):

    if browser == 'firefox':
        from selenium.webdriver.firefox.options import Options
        try:
            options = Options()
            if mode == 'headless':
               options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        except Exception as ex:  # required if using snap firefox
            from selenium.webdriver.firefox.service import Service
            options = Options()
            if mode == 'headless':
                options.add_argument('-headless')
            service = Service(executable_path='/snap/bin/geckodriver')
            driver = webdriver.Firefox(options=options, service=service)

    else:  # browser == 'chrome'
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if mode == 'headless':
            options.add_argument('-headless')
        options.add_argument('--remote-debugging-pipe')
        driver = webdriver.Chrome(options=options)

    return driver

#-----------------------------------------------------------------------

def print_flush(message):
    print(message)
    sys.stdout.flush()

#-----------------------------------------------------------------------

def run_test(server_url, delay, driver, classinfo):

    print_flush('-----------------')
    print_flush('classid: ' + classinfo[2])

    try:
        driver.get(server_url)

        # Make sure that the desired classid is visible.
        dept_input = driver.find_element(By.ID, 'deptInput')
        dept_input.send_keys(classinfo[0])

        # For libraries (e.g. React) that use a virtual DOM, wait
        # for the library to update the browser DOM.
        time.sleep(delay)

        coursenum_input = driver.find_element(By.ID, 'coursenumInput')
        coursenum_input.send_keys(classinfo[1])

        # Wait for the AJAX call to complete.
        time.sleep(delay)

        button_element = driver.find_element(
            By.ID, 'button' + str(classinfo[2]))
        button_element.click()

        # Wait for the AJAX call to complete.
        time.sleep(delay)

        class_details_table = driver.find_element(By.ID,
            'classDetailsTable')
        print_flush(class_details_table.text)
        course_details_table = driver.find_element(By.ID,
            'courseDetailsTable')
        print_flush(course_details_table.text)

    except Exception as ex:
        print(str(ex), file=sys.stderr)

#-----------------------------------------------------------------------

def main():

    server_url, browser, mode, delay = get_args()

    driver = create_driver(browser, mode)

    run_test(server_url, delay, driver, ['COS', '333', '8321'])

    # Add more tests here.

    driver.quit()

if __name__ == '__main__':
    main()
