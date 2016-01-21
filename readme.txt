      _           _                 _
  ___| | ___  ___| |_ _ __ ___   __| | ___
 / _ \ |/ _ \/ __| __| '__/ _ \ / _` |/ _ \
|  __/ |  __/ (__| |_| | | (_) | (_| |  __/
 \___|_|\___|\___|\__|_|  \___/ \__,_|\___|
 
               electrode v0.1
              by Chris Campbell 
	      
About
"""""
electrode is a Python script that automates security testing of applications. Selenium is used to log in to an application and execute key actions that will guide the subsequent ZAP Spider and Active Scan.


Version History
"""""""""""""""
0.1 - 21/1/16 - Initial release for OWASP NZ Day 2016 demonstration.


Requirements
""""""""""""
OWASP ZAP 2.4+ (https://github.com/zaproxy/zaproxy/wiki/Downloads)
Python 2.7+ (including PyPI)
Selenium for Python (pip install selenium)
ZAP Client API for Python (pip install python-owasp-zap-v2.4)


Configuration
""""""""""""""
First, define variables at the top of your script. The default variables are for the FooBlog test application.

- protocol: http or https.
- target: The target of your application.
- pagesToExclude: A string array of pages to be excluded in the scan.
- username: Username to use for login.
- password: Password to use for login.
- loginUrl: URL of the login page.
- loggedInElement: ID of an element that will be present once logged in.
- usernameText: ID of the username textbox.
- passwordText: ID of the password textbox.
- loginButton: ID of the button to be pressed for login.
- loginButtonIsLinkbutton: Is the button to be pressed an ASP.NET Linkbutton? True or False. A Linkbutton is interacted with differently by Selenium.
- zap_url: ip:port of the ZAP listener.

Tests are to be added to the tests object array. Syntax is as follows:

tests.append(Test('description','url',{'form ID:' 'text','form ID:' 'text'}, {'submit button ID': 'is ASP.NET linkbutton (True/False)'})

For example:

tests.append(Test('Search Test', 'https://example.com', {'searchText': 'espresso'}, {'submitButton': True}))

This will:
- Browse to https://example.com
- Enter 'espresso' into the textbox with ID 'searchText'
- Click on the ASP.NET Linkbutton with ID 'submitButton'

Another example is:

tests.append(Test('Search Test', 'https://example.com/foo?id=1', {'nameText': 'Bob Dole','commentText': 'An example.'}, {'submitButton': False}))

This will:
- Browse to https://example.com/foo?id=1
- Enter 'Bob Dole' into the textbox with ID 'nameText', and 'An example.' into the textbox with ID 'commentText'.
- Click on the regular button with ID 'submitButton'

You are able to use the accompanying script selenium_test.py to execute your tests independent of the ZAP operations.


Operation
"""""""""
Either from the command line (as a standalone test) or as part of a Jenkins build, you can batch run the script as follows:

python electrode.py <log path>

Where <log path> is the log you wish to output, e.g.

python d:\electrode\electrode.py c:\temp\zap_example_build-%BUILD_ID%.html

(%BUILD_ID% is a Jenkins environment variable)

It doesn't matter if ZAP is running or not. If it's running then the script will use the proxy, and if it's not then ZAP will be started in daemon mode and terminated afterwards.


sqlmap
""""""
If running electrode as part of CI, it is advised that you compliment electrode with sqlmap or nosqlmap. An example of how you may run it is:

python C:\Python27\Scripts\sqlmap\sqlmap.py -v 2 --url="https://example.com/view_post.aspx?id=4" --user-agent=SQLMAP --delay=1 --timeout=15 --retries=2 --keep-alive --threads=10 --eta --batch --dbms=PostgreSQL --os=Windows --level=5 --risk=3 --banner --is-dba --dbs --tables --technique=BEUST -s C:\temp\can_report.txt --flush-session -t C:\temp\scan_trace.txt --fresh-queries > c:\temp\sqlmap_example-build-%BUILD_ID%.log

(%BUILD_ID% is a Jenkins environment variable)

You are also able to define the root of your site as --url and add --crawl - however this will significantly blow out the duration of your scan.