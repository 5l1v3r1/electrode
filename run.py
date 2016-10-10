#!/usr/bin/python
# -*- coding: utf-8 -*-

#      _           _                 _
#  ___| | ___  ___| |_ _ __ ___   __| | ___
# / _ \ |/ _ \/ __| __| '__/ _ \ / _` |/ _ \
#|  __/ |  __/ (__| |_| | | (_) | (_| |  __/
# \___|_|\___|\___|\__|_|  \___/ \__,_|\___|
#
#              electrode v1.1.0
#             by Chris Campbell
#             Twitter: @t0x0_nz	

from common.config import *
from common.crawler import *
from common.reporting import *
from common.security import *
from ConfigParser import SafeConfigParser
import os

def main():
    print 'Loading configuration...'
    parser = SafeConfigParser()
    pwd = os.path.dirname(os.path.realpath(__file__))
    parser.read(os.path.join(pwd, 'config', 'settings.conf'))
    baseConfig = getBaseConfig(parser)
    authConfig = getAuthDetails(parser)
    testConfig = getTests(parser)
    zapConfig = getZapDetails(parser)

    print 'Starting electrode...'
    proxies = getProxies(zapConfig)
    zapStarted = startZap(zapConfig, proxies)

    if zapStarted:
        zap = createElectrode(zapConfig)
        startSession(zap)
        prepareContext(zap, baseConfig)
        driver = createDriver(zapConfig)
        preflightOk = prepareScan(zap, driver, baseConfig, authConfig)

        if preflightOk:
            testsOk = seleniumTests(driver, testConfig)
            if testsOk:
                spiderTarget(zap, baseConfig)
                passiveScan(zap)
                activeScan(zap, baseConfig)
                reportResults(zap, baseConfig, zapConfig)
                discharge(zap)

    print 'Run complete.'

if __name__ == "__main__":
    main()