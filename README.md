# Google Cloud SDK App Engine:
1. The Austrian government data portal provides COVID-19 data source as web url's and information is available in CSV or JSON format.
2. Data sources are pre-processed by removing null and zero value records, parsed into JSON format and exposed to the REST APIs, developed using Python Flask framework.
3. The back end processing is done in Google Cloud Server.
4. The Flask REST API is deployed using the Google Cloud SDK app engine service. The REST API is provided with unique domain name and secure web server url for universal access. Mobile app feature sends request parameters to the web server url deployed in Google Cloud server and receives the requested data in JSON format by the REST API's.
The app can be deployed in the Google Cloud Server with the following steps.
* Create Google Cloud console account and enable billing.
* Create a new project and enable cloud build and app engine API.
Cloud Build -> Settings -> Enable Cloud Build
App Engine -> Enable CI/CD
* Open powershell and run git clone 'repository url' to clone the project to be deployed and use editor to view files.
* Navigate to the cloned repository, cd 'Repository name' and run the command to deploy the application into the Googlr Cloud server. Once the deployment is successful, the secure web server url with unique domain name is provided for universal access.

`gcloud app deploy`
