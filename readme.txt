      _           _                 _
  ___| | ___  ___| |_ _ __ ___   __| | ___
 / _ \ |/ _ \/ __| __| '__/ _ \ / _` |/ _ \
|  __/ |  __/ (__| |_| | | (_) | (_| |  __/
 \___|_|\___|\___|\__|_|  \___/ \__,_|\___|
 
              electrode v1.0.1
              by Chris Campbell
              Twitter: @t0x0_nz			  
	      
About
"""""
electrode is a Python script that automates security testing of applications. Selenium is used to log in to an application and execute key actions that will guide the subsequent ZAP Spider and Active Scan.

Sample Screenshot: http://iforce.co.nz/i/uskdeeo1.mco.png


Version History
"""""""""""""""
0.1 - 21/1/16 - Initial release for OWASP NZ Day 2016 demonstration.
1.0 - 12/8/16 - Migration from PoC form.
1.0.1 - 12/8/16 - Removed redundant debugging outputs. Variablised listen port. Fixed Selenium button location bug.


Requirements
""""""""""""
OWASP ZAP 2.5 (https://github.com/zaproxy/zaproxy/wiki/Downloads)
Python 2.7+ (including PyPI)
Selenium for Python 2.53.0 (pip install selenium==2.53.0)
ZAP Client API for Python 2.4 (pip install python-owasp-zap-v2.4)
Firefox 46.0


Configuration
""""""""""""""
First, complete the settings.ini file (example one provided for FooBl0g):

[Target]
description=<description of app/test>
target=<base URL of website>
pagesToExclude=<comma separated list of URL's to exclude>

[Auth]
username=<username>
password=<password>
loginUrl=<URL of login page>
loggedInElement=<ID of an element only seen when logged in>
usernameText=<ID of username textbox>
passwordText=<ID of password textbox>
loginButton=<ID of submit/login button>

[ZAP]
port=<port ZAP will listen on>
dir=<installation directory of ZAP>
reportDir=<directory to write report to>

Obviously, exclude the angled brackets.

As the configuration file is read as a dictionary, each test must be given a unique section name, e.g. Test1 and Test2:

[Test1]
description=Search Test
url=https://example.com/FooBlog
inputs=[{"searchText":"espresso","searchText":"machine"}]
button=submitButton

This will name the test 'Search Test' (for logging purposes), browse to 'https://example.com/FooBlog', enter 'espresso' in 'searchText' and then 'machine' into 'searchText'. It will be submitted using the button 'submitButton'.

[Test2]
description=Merchandise Test
url=https://example.com/FooBlog/view_item.aspx?id=epmrvem7ROKUjXQJ
inputs=[{"mainContent_reviewText":"Test review."}]
button=mainContent_submitButton

This will name the test 'Merchandise Test' (for logging purposes), browse to 'https://example.com/FooBlog/view_item.aspx?id=epmrvem7ROKUjXQJ' and enter Test review.' in 'mainContent_reviewText'. It will be submitted using the button 'mainContent_submitButton'.


Operation
"""""""""
Either from the command line (as a standalone test) or as part of a Jenkins build, you can batch run the script as follows:

python electrode.py %BUILD_ID%

%BUILD_ID% is a Jenkins environment variable. Where it is undefined a timestamp will be used.

It doesn't matter if ZAP is running or not. If it's running then the script will use the proxy, and if it's not then ZAP will be started in daemon mode and terminated afterwards.


sqlmap
""""""
If running electrode as part of CI, it is advised that you compliment electrode with sqlmap or nosqlmap. An example of how you may run it is:

python C:\Python27\Scripts\sqlmap\sqlmap.py -v 2 --url="https://example.com/view_post.aspx?id=4" --user-agent=SQLMAP --delay=1 --timeout=15 --retries=2 --keep-alive --threads=10 --eta --batch --dbms=PostgreSQL --os=Windows --level=5 --risk=3 --banner --is-dba --dbs --tables --technique=BEUST -s C:\temp\can_report.txt --flush-session -t C:\temp\scan_trace.txt --fresh-queries > c:\temp\sqlmap_example-build-%BUILD_ID%.log

You are also able to define the root of your site as --url and add --crawl - however this will significantly blow out the duration of your scan.


To Do
"""""
- Handle more element types (checkbox, etc).