#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import urllib
import os
import subprocess
import sys
import time
from urlparse import urlparse
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

# Authentication:
username = 'admin'
password = 'foo'
loginUrl = 'https://cnwcc1a.cnw.co.nz/fooblog/login.aspx'
loggedInElement = 'userPanel'
usernameText = 'mainContent_usernameText'
passwordText = 'mainContent_passText'
loginButton = 'loginButton'
loginButtonIsLinkbutton = False

# Test class definition. Do not edit.
class Test:
    def __init__(self, desc, url, inputs, button):
        self.url = url
	self.desc = desc
        self.inputs = inputs
        self.button = button

# Initialise test list.
tests = []

# Tests to run.
tests.append(Test('Search Test', 'https://cnwcc1a.cnw.co.nz/FooBlog', {'searchText': 'espresso'}, {'submitButton': True}))
tests.append(Test('Merchandise Test', 'https://cnwcc1a.cnw.co.nz/FooBlog/view_item.aspx?id=epmrvem7ROKUjXQJ', {'mainContent_reviewText': 'Test review.'}, {'mainContent_submitButton': True}))
tests.append(Test('Post Test', 'https://cnwcc1a.cnw.co.nz/fooblog/view_post.aspx?id=4', {'mainContent_commentText': 'Test comment.'}, {'mainContent_submitButton': True}))

# Initialise webdriver.
driver = webdriver.Firefox()

# Log in to site.
print('Performing login test...')
driver.get(loginUrl)
driver.find_element_by_id(usernameText).send_keys(username)
driver.find_element_by_id(passwordText).send_keys(password)
driver.find_element_by_id(loginButton).click()
if loginButtonIsLinkbutton:
    driver.find_element_by_id(loginButton).send_keys(Keys.RETURN)
else:
    driver.find_element_by_id(loginButton).click()
# Give the page a chance to load.
time.sleep(3)
# Ensure we've logged in.
loggedIn = driver.find_element_by_id(loggedInElement)
print('Login OK!')

# Perform tests.
for test in tests:
    print 'Performing test: {}'.format(test.desc)
    driver.get(test.url)
    for form, text in test.inputs.iteritems():
        driver.find_element_by_id(form).send_keys(text)
    if test.button.values()[0]:
        driver.find_element_by_id(test.button.keys()[0]).send_keys(Keys.RETURN)
    else:
        driver.find_element_by_id(test.button.keys()[0]).click()
    time.sleep(3)
