# SuiteCoder - Coding for the cloud in the cloud

An online Code Editor especially designed to edit your SuiteScript files so that you can customize NetSuite anywhere everywhere. Suite Coder is a Python based Web App that runs on Google App Engine.


### Deployment Instructions

* Downlaod and Install Google Cloud SDK for Python https://cloud.google.com/appengine/docs/standard/python/download
* Create an new project on Google App Engine https://console.cloud.google.com/appengine
* Download or Clone App Source Code
* Run the command `gcloud app deploy` from the root of app source code folder

### Customization guidelines

* Suitecoder UI is built using JQuery and Angular 1.2. Code Mirror JS component is used as code editor. With basic knowledge of HTML/JS, one can make useful UI/UX tweaks. 
* Keywords list for the code completion AKA IntelliSense can be modified from static/js/deferred.js file.
* For adding features like compatibility of SuiteScript 2.0, knowledge of Python in required.
