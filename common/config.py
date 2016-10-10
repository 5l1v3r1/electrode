#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
import json
import sys
import time

class authObj:
    def __init__(self, username, password, loginUrl, loggedInElement, usernameText, passwordText, loginButton):
        self.username = username
        self.password = password
        self.loginUrl = loginUrl
        self.loggedInElement = loggedInElement
        self.usernameText = usernameText
        self.passwordText = passwordText
        self.loginButton = loginButton

class baseObj:
    def __init__(self, description, buildId, target, pagesToExclude, injectMode, depth, threads):
        self.description = description
        self.buildId = buildId
        self.target = target
        self.pagesToExclude = pagesToExclude
        self.injectMode = injectMode
        self.depth = depth
        self.threads = threads

class testObj:
    def __init__(self, description, url, inputs, toggles, button):
        self.description = description
        self.url = url
        self.inputs = inputs
        self.toggles = toggles
        self.button = button

class zapObj:
    def __init__(self, port, url, dir, reportDir):
        self.port = port
        self.url = url
        self.dir = dir
        self.reportDir = reportDir

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

def get_auth_details(parser):
    username = parser.get('Auth', 'username')
    password = parser.get('Auth', 'password')
    loginUrl = parser.get('Auth', 'loginUrl')
    loggedInElement = parser.get('Auth', 'loggedInElement')
    usernameText = parser.get('Auth', 'usernameText')
    passwordText = parser.get('Auth', 'passwordText')
    loginButton = parser.get('Auth', 'loginButton')
    return authObj(username, password, loginUrl, loggedInElement, usernameText, passwordText, loginButton)

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