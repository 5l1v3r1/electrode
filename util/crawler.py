#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
import time

# Create Selenium driver.
def createDriver(zapConfig):
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
def seleniumTests(driver, testConfig):
    # Perform tests.
    for test in testConfig:
        print 'Performing test: {0} ({1})'.format(test.description, test.url)
        driver.get(test.url)
        # Give the new page a chance to load.
        time.sleep(2)
        if len(test.inputs) > 0:
            for input in test.inputs:
                for form, text in input.iteritems():
                    if elementExists(driver, form):
                        driver.find_element_by_id(form).send_keys(text)
                    else:
                        return False
        if len(test.toggles) > 0:
            for form in test.toggles:
                if elementExists(driver, form):
                    element = driver.find_element_by_id(form)
                    driver.execute_script("arguments[0].click();", element)
                else:
                    return False
        if elementExists(driver, test.button):
            element = driver.find_element_by_id(test.button)
            driver.execute_script("arguments[0].click();", element)
            # Wait a moment before the next test.
            time.sleep(1)
        else:
            return False
    return True

# Access the target and log in.
def prepareScan(zap, driver, baseConfig, authConfig):
    # Access target.
    print 'Accessing target: {0}'.format(baseConfig.target)
    zap.urlopen(baseConfig.target)
    driver.get(baseConfig.target)
    # Maximise window to avoid invalid element locations.
    driver.maximize_window()
    # Give the new page a chance to load.
    time.sleep(2)

    # Log in to site.
    print 'Performing login...'
    driver.get(authConfig.loginUrl)
    # Give the new page a chance to load.
    time.sleep(2)
    if elementExists(driver, authConfig.usernameText):
        driver.find_element_by_id(authConfig.usernameText).send_keys(authConfig.username)
    else:
        return False
    if elementExists(driver, authConfig.passwordText):
        driver.find_element_by_id(authConfig.passwordText).send_keys(authConfig.password)
    else:
        return False

    if elementExists(driver, authConfig.loginButton):
        element = driver.find_element_by_id(authConfig.loginButton)
        driver.execute_script("arguments[0].click();", element)
        
        # Give the login a chance to complete.
        time.sleep(5)

        # Ensure we've logged in.
        if elementExists(driver, authConfig.loggedInElement):
            print 'Login OK!'
            return True
        else:
            print 'Login failed.'
            return False
    else:
        return False

# Check if element exists on page using Selenium.
def elementExists(driver, id):
    try:
        driver.find_element_by_id(id)
        return True
    except Exception:
        print 'Element does not exist: {0}'.format(id)
        return False