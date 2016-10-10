#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

# Create Selenium driver.
def create_driver(zapConfig):
    proxyObj = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': zapConfig.url,
        'ftpProxy': zapConfig.url,
        'sslProxy': zapConfig.url,
        'noProxy': '',
        })

    # Define Selenium driver.
    return webdriver.Firefox(proxy=proxyObj)

# Perform the Selenium tests to derive the ZAP tests from.
def selenium_tests(driver, testConfig):
    # Perform tests.
    for test in testConfig:
        print 'Performing test: {0} ({1})'.format(test.description, test.url)
        driver.get(test.url)
        # Give the new page a chance to load.
        time.sleep(2)
        if len(test.inputs) > 0:
            for input in test.inputs:
                for form, text in input.iteritems():
                    if element_exists(driver, form):
                        driver.find_element_by_id(form).send_keys(text)
                    else:
                        return False
        if len(test.toggles) > 0:
            for form in test.toggles:
                if element_exists(driver, form):
                    element = driver.find_element_by_id(form)
                    driver.execute_script("arguments[0].click();", element)
                else:
                    return False
        if element_exists(driver, test.button):
            element = driver.find_element_by_id(test.button)
            driver.execute_script("arguments[0].click();", element)
            # Wait a moment before the next test.
            time.sleep(1)
        else:
            return False
    return True

# Check if element exists on page using Selenium.
def element_exists(driver, id):
    try:
        driver.find_element_by_id(id)
        return True
    except Exception:
        print 'Element does not exist: {0}'.format(id)
        return False