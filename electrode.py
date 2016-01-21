#!/usr/bin/python
# -*- coding: utf-8 -*-

#      _           _                 _
#  ___| | ___  ___| |_ _ __ ___   __| | ___
# / _ \ |/ _ \/ __| __| '__/ _ \ / _` |/ _ \
#|  __/ |  __/ (__| |_| | | (_) | (_| |  __/
# \___|_|\___|\___|\__|_|  \___/ \__,_|\___|
#
#              electrode v0.1
#             by Chris Campbell

# Argument 1: fully qualified log file path.

import time
import urllib
import os
import subprocess
import sys
import time
from pprint import pprint
from zapv2 import ZAPv2
from urlparse import urlparse
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

# Define variables.
# Target:
protocol = 'https'
target = '{}://cnwcc1a.cnw.co.nz/fooblog'.format(protocol)
pagesToExclude = ['https://cnwcc1a.cnw.co.nz/fooblog/register.aspx',
                  'https://cnwcc1a.cnw.co.nz/fooblog/logout.aspx',
                  'https://cnwcc1a.cnw.co.nz/fooblog/login.aspx',
                  'https://cnwcc1a.cnw.co.nz/fooblog/reset_pass.aspx']
# Authentication:
username = 'admin'
password = 'foo'
loginUrl = 'https://cnwcc1a.cnw.co.nz/fooblog/login.aspx'
loggedInElement = 'userPanel'
usernameText = 'mainContent_usernameText'
passwordText = 'mainContent_passText'
loginButton = 'loginButton'
loginButtonIsLinkbutton = False
# ZAP listen address:
zap_url = '127.0.0.1:8090'

# Test class definition. Do not edit.
class Test:
    def __init__(self, desc, url, inputs, button):
        self.url = url
	self.desc = desc
        self.inputs = inputs
        self.button = button
# Initialise test list.
tests = []

# Tests to run (format: 'description','url',{'form ID:' 'text','form ID:' 'text'}, {'submit button ID': 'is ASP.NET linkbutton (True/False)'}):
tests.append(Test('Search Test', 'https://cnwcc1a.cnw.co.nz/FooBlog', {'searchText': 'espresso'}, {'submitButton': True}))
tests.append(Test('Merchandise Test', 'https://cnwcc1a.cnw.co.nz/FooBlog/view_item.aspx?id=epmrvem7ROKUjXQJ', {'mainContent_reviewText': 'Test review.'}, {'mainContent_submitButton': True}))
tests.append(Test('Post Test', 'https://cnwcc1a.cnw.co.nz/fooblog/view_post.aspx?id=4', {'mainContent_commentText': 'Test comment.'}, {'mainContent_submitButton': True}))

#
# DO NOT EDIT BELOW.
#

print 'Starting electrode...'

# Determine if ZAP is running.

def is_zap_running(url, proxies):
    try:
        response = urllib.urlopen('http://zap/', proxies=proxies)
        if 'ZAP-Header' \
            in response.headers.get('Access-Control-Allow-Headers', []):
            print 'ZAP started!'
            return True
        else:
            message = 'Service running at {} is not ZAP'.format(url)
            raise Exception(message)
    except IOError:
        return False


# Define proxy addresses.

proxies = {'http': 'http://{}'.format(zap_url),
           'https': 'http://{}'.format(zap_url)}

# Start ZAP if required.

if is_zap_running(zap_url, proxies) is False:
    print 'Starting ZAP...'
    zap_dir = 'C:\Program Files (x86)\OWASP\Zed Attack Proxy'
    subprocess.Popen('{}\zap.bat -daemon -port 8090 -config api.disablekey=true'.format(zap_dir),
                     cwd=zap_dir, stdout=open(os.devnull, 'w'))
    while not is_zap_running(zap_url, proxies):
        print 'Waiting for ZAP to start...'
        time.sleep(10)
else:
    print 'ZAP is already started!'

# Define ZAP object.

zap = ZAPv2(proxies={'http': 'http://{}'.format(zap_url),
            'https': 'http://{}'.format(zap_url)})

# Start new session.

print 'Starting new session...'
zap.core.new_session()

# Prepare context.

print 'Preparing context...'
p = urlparse(target)
cname = p.hostname
cid = zap.context.new_context(cname)
zap.context.set_context_in_scope(cname, True)
zap.context.set_context_in_scope('Default Context', False)
zap.context.include_in_context(cname, '\\Q\\E.*'.format(target))
for page in pagesToExclude:
    zap.context.exclude_from_context(cname, '\\Q{}\\E'.format(page))

# Access target.

print 'Accessing target: ' + target
zap.urlopen(target)
time.sleep(2)

print 'Preparing auth...'

proxyObj = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': zap_url,
    'ftpProxy': zap_url,
    'sslProxy': zap_url,
    'noProxy': '',
    })

# Define Selenium driver.

driver = webdriver.Firefox(proxy=proxyObj)

# Log in to site.

print 'Performing login test...'
driver.get(loginUrl)
driver.find_element_by_id(usernameText).send_keys(username)
driver.find_element_by_id(passwordText).send_keys(password)

if loginButtonIsLinkbutton:
    driver.find_element_by_id(loginButton).send_keys(Keys.RETURN)
else:
    driver.find_element_by_id(loginButton).click()

# Give the page a chance to load.

time.sleep(3)

# Ensure we've logged in.

loggedIn = driver.find_element_by_id(loggedInElement)
print 'Login OK!'

# Perform tests.

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

# Spider target.

print 'Spidering target: {}'.format(target)
zap.spider.set_option_scope_string(target)
zap.spider.set_option_max_depth(10)
zap.spider.set_option_thread_count(3)
spider = zap.spider.scan(target, 0)

# Give the spider a chance to start

time.sleep(5)

while int(zap.spider.status()) < 100:
    print 'Spider progress: {}%'.format(zap.spider.status())
    time.sleep(5)
print 'Spider completed!'

# Wait for passive scan to complete.

print 'Waiting for passive scan...'
print 'Records to scan: {}'.format(zap.pscan.records_to_scan)
while int(zap.pscan.records_to_scan) > 0:
    time.sleep(5)
    print 'Records to scan: {}'.format(zap.pscan.records_to_scan)
print 'Passive scanning complete!'

# Start active scan.

print 'Scanning target: {}'.format(target)
zap.ascan.set_option_thread_per_host(3)

# 1 - URL Query String
# 2 - POST Data
# 4 - HTTP Headers
# 8 - Cookie Data
# 16 - URL Path

zap.ascan.set_option_target_params_injectable(3)
ascan = zap.ascan.scan(target, recurse=True)
time.sleep(5)
while int(zap.ascan.status()) < 100:
    print 'Scan progress: {}%'.format(zap.ascan.status())
    time.sleep(5)
print 'Scan completed!'

# Report the results

print 'Discharging the electrode...'
report_file = sys.argv[1]
file = open(report_file, 'w')
html = zap.core.htmlreport()
file.write(html)
file.close()
print 'Report written to: {}'.format(report_file)

# Shutdown ZAP

zap.core.shutdown()