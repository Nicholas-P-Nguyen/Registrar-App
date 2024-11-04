#-----------------------------------------------------------------------
# testregoverviews.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#-----------------------------------------------------------------------

def get_args():

    parser = argparse.ArgumentParser(
        description='Test the ability of the reg application to '
            + 'handle "primary" (class overviews) queries')

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
            + 'the browser not to display its window and so is faster, '
            + 'especially when using X Windows')

    parser.add_argument(
        'delay', metavar='delay', type=int,
        help='the number of seconds that this program should delay '
            + 'between interactions with the browser')

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

def run_test(delay, driver, input_values):

    print_flush('-----------------')
    for key, value in input_values.items():
        print_flush(key + ': |' + value + '|')

    try:
        if 'dept' in input_values:
            dept_input = driver.find_element(By.ID, 'deptInput')
            dept_input.send_keys(input_values['dept'])
            time.sleep(delay) # Necessary for virtual DOM libraries.

        if 'coursenum' in input_values:
            coursenum_input = driver.find_element(By.ID,
                'coursenumInput')
            coursenum_input.send_keys(input_values['coursenum'])
            time.sleep(delay) # Necessary for virtual DOM libraries

        if 'area' in input_values:
            area_input = driver.find_element(By.ID, 'areaInput')
            area_input.send_keys(input_values['area'])
            time.sleep(delay) # Necessary for virtual DOM libraries

        if 'title' in input_values:
            title_input = driver.find_element(By.ID, 'titleInput')
            title_input.send_keys(input_values['title'])
            time.sleep(delay) # Necessary for virtual DOM libraries

        # Wait for the AJAX calls to complete.
        time.sleep(delay)

        overviews_table = driver.find_element(By.ID, 'overviewsTable')
        print_flush(overviews_table.text)

        # This works, but only with libraries that don't use
        # a virtual DOM:
        #if 'dept' in input_values:
        #    dept_input.clear()
        #if 'coursenum' in input_values:
        #    coursenum_input.clear()
        #if 'area' in input_values:
        #    area_input.clear()
        #if 'title' in input_values:
        #    title_input.clear()

        # This works with all (tested) libraries:
        if 'dept' in input_values:
            key_count = len(input_values['dept'])
            dept_input.send_keys(Keys.BACKSPACE * key_count)
            time.sleep(delay)
        if 'coursenum' in input_values:
            key_count = len(input_values['coursenum'])
            coursenum_input.send_keys(Keys.BACKSPACE * key_count)
            time.sleep(delay)
        if 'area' in input_values:
            key_count = len(input_values['area'])
            area_input.send_keys(Keys.BACKSPACE * key_count)
            time.sleep(delay)
        if 'title' in input_values:
            key_count = len(input_values['title'])
            title_input.send_keys(Keys.BACKSPACE * key_count)
            time.sleep(delay)

    except Exception as ex:
        print(str(ex), file=sys.stderr)

#-----------------------------------------------------------------------

def main():

    server_url, browser, mode, delay = get_args()

    driver = create_driver(browser, mode)

    driver.get(server_url)

    run_test(delay, driver,
        {'dept':'COS'})
    run_test(delay, driver,
        {'dept':'COS', 'coursenum':'2', 'area':'qr', 'title':'intro'})

    # Add more tests here.

    driver.quit()

if __name__ == '__main__':
    main()
