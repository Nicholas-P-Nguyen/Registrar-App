#-----------------------------------------------------------------------
# testregdetails.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

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
            + 'use when interacting with the browser; headless tells '
            + 'the browser not to display its window and so is faster, '
            + 'especially when using X Windows')

    args = parser.parse_args()

    return (args.serverURL, args.browser, args.mode)

#-----------------------------------------------------------------------

def create_driver(browser, mode):

    if browser == 'firefox':
        try:
            options = FirefoxOptions()
            if mode == 'headless':
                options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        except Exception:  # required if using snap firefox
            options = FirefoxOptions()
            if mode == 'headless':
                options.add_argument('-headless')
            service = FirefoxService(
                executable_path='/snap/bin/geckodriver')
            driver = webdriver.Firefox(options=options, service=service)

    else:  # browser == 'chrome'
        options = ChromeOptions()
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

def run_test(server_url, driver, classid):

    print_flush(UNDERLINE)
    try:
        driver.get(server_url)
        link_element = driver.find_element(By.LINK_TEXT, classid)
        link_element.click()
        class_details_table = driver.find_element(
            By.ID, 'classDetailsTable')
        print_flush(class_details_table.text)
        course_details_table = driver.find_element(
            By.ID, 'courseDetailsTable')
        print_flush(course_details_table.text)
    except Exception as ex:
        print(str(ex))

#-----------------------------------------------------------------------

def main():

    server_url, browser, mode = get_args()

    driver = create_driver(browser, mode)

    run_test(server_url, driver, '8321')
    run_test(server_url, driver, '9032')
    run_test(server_url, driver, '8293')
    run_test(server_url, driver, '9977')
    run_test(server_url, driver, '10188')
    run_test(server_url, driver, '9012')

    # Testing class ID that doesn't exist
    run_test(server_url, driver, '01010444')
    run_test(server_url, driver, '')  
    run_test(server_url, driver, '8321 9032')  
    run_test(server_url, driver, 'abc123') 
    run_test(server_url, driver, '9032')
    run_test(server_url, driver, 'abcdefg')

    # # Testing database cannot be opened
    # shutil.copy('reg.sqlite', 'regbackup.sqlite')
    # os.remove('reg.sqlite')
    # run_test(server_url, driver, '9012')
    # shutil.copy('regbackup.sqlite', 'reg.sqlite')

    # # Testing corrupted database
    # shutil.copy('reg.sqlite', 'regbackup.sqlite')
    # shutil.copy('regflawed.sqlite', 'reg.sqlite')
    # run_test(server_url, driver, '8321')
    # shutil.copy('regbackup.sqlite', 'reg.sqlite')


    driver.quit()

if __name__ == '__main__':
    main()
