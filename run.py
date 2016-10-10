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

if __name__ == "__main__":
    main()