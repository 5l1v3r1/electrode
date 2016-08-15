#!/usr/bin/python
# -*- coding: utf-8 -*-

#      _           _                 _
#  ___| | ___  ___| |_ _ __ ___   __| | ___
# / _ \ |/ _ \/ __| __| '__/ _ \ / _` |/ _ \
#|  __/ |  __/ (__| |_| | | (_) | (_| |  __/
# \___|_|\___|\___|\__|_|  \___/ \__,_|\___|
#
#              electrode v1.0.3
#             by Chris Campbell
#             Twitter: @t0x0_nz	

import json
import time
import urllib
import os
import subprocess
import sys
import time
from ConfigParser import SafeConfigParser
from pprint import pprint
from zapv2 import ZAPv2
from urlparse import urlparse
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

class baseObj:
    def __init__(self, description, buildId, target, pagesToExclude, injectMode, depth, threads):
        self.description = description
        self.buildId = buildId
        self.target = target
        self.pagesToExclude = pagesToExclude
        self.injectMode = injectMode
        self.depth = depth
        self.threads = threads

def get_base_config(parser):
    description = parser.get('Target', 'description')
    target = parser.get('Target', 'target')
    pagesToExclude = parser.get('Target', 'pagesToExclude').split(',')
    injectMode = int(parser.get('Target', 'injectMode'))
    depth = int(parser.get('Target', 'depth'))
    threads = int(parser.get('Target', 'threads'))

    if len(sys.argv) > 1:
        buildId = sys.argv[1]
    else:
        buildId = time.strftime("%d%m%Y-%H%M%S")

    return baseObj(description, buildId, target, pagesToExclude, injectMode, depth, threads)

class authObj:
    def __init__(self, username, password, loginUrl, loggedInElement, usernameText, passwordText, loginButton):
        self.username = username
        self.password = password
        self.loginUrl = loginUrl
        self.loggedInElement = loggedInElement
        self.usernameText = usernameText
        self.passwordText = passwordText
        self.loginButton = loginButton

def get_auth_details(parser):
    username = parser.get('Auth', 'username')
    password = parser.get('Auth', 'password')
    loginUrl = parser.get('Auth', 'loginUrl')
    loggedInElement = parser.get('Auth', 'loggedInElement')
    usernameText = parser.get('Auth', 'usernameText')
    passwordText = parser.get('Auth', 'passwordText')
    loginButton = parser.get('Auth', 'loginButton')
    return authObj(username, password, loginUrl, loggedInElement, usernameText, passwordText, loginButton)

class testObj:
    def __init__(self, description, url, inputs, toggles, button):
        self.description = description
        self.url = url
        self.inputs = inputs
        self.toggles = toggles
        self.button = button

def get_tests(parser):
    tests = []

    for section in (section for section in parser.sections() if section.startswith('Test')):
        description = parser.get(section, 'description')
        url = parser.get(section, 'url')
        inputs = json.loads(parser.get(section, 'inputs'))
        inputs = filter(None, inputs)
        toggles = parser.get(section, 'toggles').split(',')
        toggles = filter(None, toggles)
        button = parser.get(section, 'button')
        tests.append(testObj(description, url, inputs, toggles, button))

    return tests

class zapObj:
    def __init__(self, port, url, dir, reportDir):
        self.port = port
        self.url = url
        self.dir = dir
        self.reportDir = reportDir

def get_zap_details(parser):
    port = parser.get('ZAP', 'port')
    url = '127.0.0.1:{0}'.format(port)
    dir = parser.get('ZAP', 'dir')
    reportDir = parser.get('ZAP', 'reportDir')
    return zapObj(port, url, dir, reportDir)

# Define proxy addresses.
def get_proxies(zapConfig):
    return {'http': 'http://{0}'.format(zapConfig.url),
            'https': 'http://{0}'.format(zapConfig.url)}

# Determine if ZAP is running.
def is_zap_running(url, proxies):
    try:
        response = urllib.urlopen('http://zap/', proxies=proxies)
        if 'ZAP-Header' \
            in response.headers.get('Access-Control-Allow-Headers', []):
            return True
        else:
            message = 'Service running at {0} is not ZAP'.format(url)
            raise Exception(message)
    except IOError:
        return False

# Start ZAP if required.
def start_zap(zapConfig, proxies):
    if is_zap_running(zapConfig.url, proxies) is False:
        print 'Starting ZAP...'
        subprocess.Popen('{0}\zap.bat -daemon -port {1} -config api.disablekey=true'.format(zapConfig.dir, zapConfig.port),
                         cwd=zapConfig.dir, stdout=open(os.devnull, 'w'))
        retry = 0
        while not is_zap_running(zapConfig.url, proxies) and retry < 6:
            print 'Waiting for ZAP to start...'
            time.sleep(10)
            retry += 1
        if is_zap_running(zapConfig.url, proxies):
            print 'ZAP started!'
            return True
        else:
            print 'Failed to start ZAP.'
            return False
    else:
        print 'ZAP is already started!'
        return True

# Start new session.
def start_session(zap):
    print 'Starting new session...'
    zap.core.new_session()

# Prepare context.
def prepare_context(zap, baseConfig):
    print 'Preparing context...'
    p = urlparse(baseConfig.target)
    cname = p.hostname
    cid = zap.context.new_context(cname)
    zap.context.set_context_in_scope(cname, True)
    zap.context.set_context_in_scope('Default Context', False)
    zap.context.include_in_context(cname, '\\Q\\E.*'.format(baseConfig.target))
    for page in baseConfig.pagesToExclude:
        zap.context.exclude_from_context(cname, '\\Q{0}\\E'.format(page))

# Create ZAP driver.
def create_electrode(zapConfig):
    return ZAPv2(proxies={'http': 'http://{0}'.format(zapConfig.url),
                'https': 'http://{0}'.format(zapConfig.url)})
    
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

# Check if element exists on page using Selenium.
def element_exists(driver, id):
    try:
        driver.find_element_by_id(id)
        return True
    except Exception:
        print 'Element does not exist: {0}'.format(id)
        return False

# Access the target and log in.
def prepare_scan(zap, driver, baseConfig, authConfig):
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
    if element_exists(driver, authConfig.usernameText):
        driver.find_element_by_id(authConfig.usernameText).send_keys(authConfig.username)
    else:
        return False
    if element_exists(driver, authConfig.passwordText):
        driver.find_element_by_id(authConfig.passwordText).send_keys(authConfig.password)
    else:
        return False

    if element_exists(driver, authConfig.loginButton):
        element = driver.find_element_by_id(authConfig.loginButton)
        driver.execute_script("arguments[0].click();", element)
        
        # Give the login a chance to complete.
        time.sleep(5)

        # Ensure we've logged in.
        if element_exists(driver, authConfig.loggedInElement):
            print 'Login OK!'
            return True
        else:
            print 'Login failed.'
            return False
    else:
        return False

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
        

# Spider the target to build up a sitemap.
def spider_target(zap, baseConfig):
    # Spider target.
    print 'Spidering target: {0}'.format(baseConfig.target)
    zap.spider.set_option_scope_string(baseConfig.target)
    zap.spider.set_option_max_depth(baseConfig.depth)
    zap.spider.set_option_thread_count(baseConfig.threads)
    spider = zap.spider.scan(baseConfig.target, 0)

    # Give the spider a chance to start.
    time.sleep(5)

    while int(zap.spider.status()) < 100:
        print 'Spider progress: {0}%'.format(zap.spider.status())
        time.sleep(5)
    print 'Spider completed!'

# Passively scan the target.
def passive_scan(zap):
    # Wait for passive scan to complete.
    print 'Waiting for passive scan...'
    print 'Records to scan: {0}'.format(zap.pscan.records_to_scan)
    while int(zap.pscan.records_to_scan) > 0:
        time.sleep(5) # throttle iterations.
        print 'Records to scan: {0}'.format(zap.pscan.records_to_scan)
    print 'Passive scanning complete!'

# Main vulnerability testing.
def active_scan(zap, baseConfig):
    # Start active scan.
    print 'Scanning target: {0}'.format(baseConfig.target)
    zap.ascan.set_option_thread_per_host(baseConfig.threads)
    zap.ascan.set_option_target_params_injectable(baseConfig.injectMode)
    ascan = zap.ascan.scan(baseConfig.target, recurse=True)
    time.sleep(5)
    while int(zap.ascan.status()) < 100:
        time.sleep(5) # throttle iterations.
        print 'Scan progress: {0}%'.format(zap.ascan.status())
    print 'Scan completed!'

# Produce the HTML report.
def report_results(zap, baseConfig, zapConfig):
    # Report the results
    print 'Writing report...'
    reportFilename = '{0}-zap_report-{1}.html'.format(baseConfig.description, baseConfig.buildId)
    reportPath = os.path.join(zapConfig.reportDir, reportFilename)
    html = zap.core.htmlreport()
    with open(reportPath, 'w') as file:
        file.write(html)
    print 'Report written to: {0}'.format(reportPath)

# Shut down ZAP.
def discharge(zap):
    # Shutdown ZAP
    print 'Discharging the electrode...'
    zap.core.shutdown()

# Define workflow:
print 'Loading configuration...'
parser = SafeConfigParser()
parser.read('settings.ini')
baseConfig = get_base_config(parser)
authConfig = get_auth_details(parser)
testConfig = get_tests(parser)
zapConfig = get_zap_details(parser)

print 'Starting electrode...'
proxies = get_proxies(zapConfig)
zapStarted = start_zap(zapConfig, proxies)

if zapStarted:
    zap = create_electrode(zapConfig)
    start_session(zap)
    prepare_context(zap, baseConfig)
    driver = create_driver(zapConfig)
    preflightOk = prepare_scan(zap, driver, baseConfig, authConfig)

    if preflightOk:
        testsOk = selenium_tests(driver, testConfig)
        if testsOk:
            spider_target(zap, baseConfig)
            passive_scan(zap)
            active_scan(zap, baseConfig)
            report_results(zap, baseConfig, zapConfig)
            discharge(zap)

print 'Run complete.'