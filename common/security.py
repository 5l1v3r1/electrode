#!/usr/bin/python
# -*- coding: utf-8 -*-

from urlparse import urlparse
from zapv2 import ZAPv2
import os
import subprocess
import time
import urllib

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

# Shut down ZAP.
def discharge(zap):
    # Shutdown ZAP
    print 'Discharging the electrode...'
    zap.core.shutdown()