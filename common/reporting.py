#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

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