# Cashflow Challenge
## Requirements
### Backend
#### Inputs
-   Loan amount (or principal)
-   Interest rate (an annual percentage rate or APY)
-   Term (in years)
#### Outputs
- An array/list of JSON blobs. The JSON blob is expected to be formatted like the following:
```javascript
{
    'month': 1,
    'starting-balance': 250000,
    'fixed-payment': 1140.13,
    'principal-payment': 384.92,
    'interest-payment': 755.21,
    'ending-balance': 248859.87,
    'total-interest': 755.21
}
```
So ultimately the response from the back-end would be:
```javascript
[{'month': 1,'starting-balance': 250000,'fixed-payment': 1140.13,'principal-payment': 384.92,'interest-payment': 755.21,'ending-balance': 248859.87,'total-interest': 755.21
},...]
```

### Frontend
#### Outputs
There should be two pages, one for data-entry of the inputs described for the Backend (Principal, rate, term), and another for displaying what the back-end returns.

- A safeguard/check must be implemented to ensure that an inputted term (in years) does not exceed 30. It is suggested to leverage a modal to notify user.
- Calculations **must** be derived from backend. The backend performs any calculations for the loan, and the frontend only displays the result.

## Approach

### System Design

A database or caching mechanism (memcached/redis) does not seem necessary given the requirements and scope of this mini-project. 
This also ruled out needing to leverage larger frameworks like Django, Pyramid, RoR. 
Flask/Falcon/Starlette/Bottle/Go/ExpressJS and other micro-frameworks might appear as a more suitable fit for these requirements. Consequently, FastAPI which leverages asyncio (enabling multi-threading / asynchronous views) was selected to explore this problem with, as well providing a great convenience by auto-generating docs (accessible via /docs URL) which is akin to Swagger.

Sending data via POST (over GET) was selected to be the way the http server would receive data from the front-end. This was more out of convenience the way model objects can be auto generated on receiving a POST that is formatted as expected. The down-side to this choice is that if a user wants to share results after data-entry, it may not be easily share-able via URL. Extra work may have to be done in the front-end to accommodate results-sharing URLs (such as leveraging hash params).

### Directory Design Pattern

The Project is structured similarly to that of Django's apps pattern:
```
.
├── config (base app)
│   ├── __init__.py
│   └── settings.py
├── loans_app
│   ├── __init__.py
│   ├── controller.py
│   ├── models.py
│   └── tests.py
├── static
│   ├── css
│   │   ├── cashflow.css
│   │   ├── bootstrap.min.css
│   │   ├── datatables.min.css
│   │   └── fixedHeader.dataTables.min.css
│   └── js
│       ├── bootstrap_jq.min.js
│       ├── bootstrap.min.js
│       ├── dataTables.fixedHeader.min.js
│       ├── datatables.min.js
│       └── cashflow.js
├── templates
│   └── index.html
├── Dockerfile
├── main.py (like manage.py)
├── README.md
└── requirements.txt
```
#### loans_app
The loans app consists of the controller.py, models.py and tests.py
To not fall into an anti-pattern, the business-logic (where we perform calculations related to the loan's payment plan) is placed alongside the models used to describe the entities involved in the calculation. 
While it may be tempting to simply perform the calculation leveraging python dicts (instead of classes describing objects), this can be considered anti-pattern as we would not be leveraging the framework's built-in validation tools, and can be further chaotic when extending features / calculations.

The controller.py is the equivalent to a urls.py (if from a Django background). Here is where routing is handled. Due to the small scope of the app, we only have 2 views; one providing the landing page, the other being the endpoint used for performing the payment plan calculations.

tests.py is where we leverage pytest to help automate the running of tests. Currently there are tests that ensure the validations work as expected and the calculations for base cases work as expected. We can further extend these tests for edge-case testing.

#### config
In config's settings.py we describe some further settings of this project, such as where templates (html) files are found, staticfiles (js, css, imgs) would be found, as well as security and interface settings.

Currently for the sake of demo-ing CORs is disabled and the API can be used without any domain names whitelisted.

#### templates
The layout is found here. A single view has been leveraged (producing a single-page app) which aids in preventing reloading of resources (assuming it is not optimized by remaining cached in user browser).

#### static
Customized js and css can be found in their respective directories in the cashflow.js and cashflow.css files. By leveraging bootstrap, minimal frontend custom work needed to be done (though this requires loading bootstrap+jquery which might be considered an expensive network call).


## Running the project

This project can be run in two ways
1. Docker building and running the image
2. Manually: creating a virtualenv, pip installing the requirements and running the app via uvicorn

### Docker method

Assuming docker is installed and available in system PATH

```shell
$ docker image build -t cashflow .
```
The cmd above will build the image as described in Dockerfile with the relevant dependencies from the project.

```shell
$ docker image ls
```
Running the cmd above should confirm that the image is in the list of images available on your system.

```shell
$ docker run -p 80:80 -d cashflow
```
The cmd above creates the container with the built image. It maps the container's local port to the host system's port to make it accessible from the host system.

```shell
$ docker container ls
```
The cmd above would show a list of containers currently running. cashflow should be somewhere on that list (with a unique id).

```shell
$ docker container stop [unique id]
```
The cmd above would stop the running container.

### Manually

Assuming python 3 is already installed on the system, the following commands can be run in the app's main directory (where the requirements.txt file is accessible)

```shell
$ python3 -m venv cashflow-env
```
The cmd above creates a virtualenv named cashflow-env

```shell
$ source cashflow-env/bin/activate
```
For a *nix based pc, the above would apply/enable the environment so that it uses the virtualenv's Python instead of the system-wide Python.

```shell
(cashflow-env) $ python3 -m pip install requirements.txt
```
The above cmd prepares the virtualenv with all the packages needed for this project to run.

```shell
(cashflow-env) $ uvicorn main:app --host 0.0.0.0 --port 80
```
The cmd above runs the server.
This process can be stopped with Ctrl+C (assuming it was not run in a screen or tmux and user has not detached from that context)