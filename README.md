# Swaggergenerator
Automatically generate Swagger documentation from javascript routers and controllers using python.<br>
A Medium-article explaining the code and what it can be used for can be found here: www.medium.com/fremtind/swaggergenerator<br>

# Use
Put both pythonscripts inside the same folder as your javascript router and controller that you want to generate swagger .js files for.<br> 
Edit the swaggergen.py file to read in the router and controller files.<br> 
The swaggergen.py file imports the swaggerschemagen.py file.<br> 
Run python swaggergen.py in your terminal in the same directory as your router and controller files.<br>
See 4 outputs being generated instantly: 2 .json files to help you debugging (these can be deleted later) and 2 swagger.js files that can be used with OpenApi Swagger documentation.<br>
Modify the pythoncode (espescially the regex part) to better suit your needs.<br> 

# Contribute
This repo is something we use to help automatically generate swagger for our OpenAPI. Feel free to use and improve on it.
Let's free ourselves from the tyranny of manual documentation!
