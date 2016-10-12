#!/usr/bin/python
# -*- coding: utf-8 -*-

from urlparse import urlparse
from zapv2 import ZAPv2
import os
import subprocess
import time
import urllib

# Determine if ZAP is running.
def isZapRunning(url, proxies):
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
def startZap(zapConfig, proxies):
    if isZapRunning(zapConfig.url, proxies) is False:
        print 'Starting ZAP...'
        subprocess.Popen('{0}\zap.bat -daemon -port {1} -config api.disablekey=true'.format(zapConfig.dir, zapConfig.port),
                         cwd=zapConfig.dir, stdout=open(os.devnull, 'w'))
        retry = 0
        while not isZapRunning(zapConfig.url, proxies) and retry < 6:
            print 'Waiting for ZAP to start...'
            time.sleep(10)
            retry += 1
        if isZapRunning(zapConfig.url, proxies):
            print 'ZAP started!'
            return True
        else:
            print 'Failed to start ZAP.'
            return False
    else:
        print 'ZAP is already started!'
        return True

# Start new session.
def startSession(zap):
    print 'Starting new session...'
    zap.core.new_session()

# Prepare context.
def prepareContext(zap, baseConfig):
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
def createElectrode(zapConfig):
    return ZAPv2(proxies={'http': 'http://{0}'.format(zapConfig.url),
                'https': 'http://{0}'.format(zapConfig.url)})
    
# Spider the target to build up a sitemap.
def spiderTarget(zap, baseConfig):
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
def passiveScan(zap):
    # Wait for passive scan to complete.
    print 'Waiting for passive scan...'
    print 'Records to scan: {0}'.format(zap.pscan.records_to_scan)
    while int(zap.pscan.records_to_scan) > 0:
        time.sleep(5) # throttle iterations.
        print 'Records to scan: {0}'.format(zap.pscan.records_to_scan)
    print 'Passive scanning complete!'

# Main vulnerability testing.
def activeScan(zap, baseConfig):
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