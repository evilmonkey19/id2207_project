# Project ID2207 - Modern Methods in Software Engineering
This project is a part of the course ID2207 - Modern Methods in Software Engineering at KTH Royal Institute of Technology. 

## Group members
* Eashin Matubber 
* Enric Perpinyà

## The project
This project it has been using Python and the Django framework. The project is a web application that allows SEP to create financial requests, manage events, create tasks and recruit staff. For more information about the project, please refer to the BusinessForHomework.pdf file.

## Try the app online
We have deployed the app using fly.io. You can try the app online by going to the following link: https://winter-flower-3917.fly.dev. It is highly recommended to run it locally instead of using the online version as the session management is not working properly in the online version.

## To run the project
It is recommended to run the project in a virtual environment. This is out of the scope of this README, but it can be done by following the instructions [here](https://docs.python.org/3/library/venv.html).
```bash
python3 -m venv venv
source venv/bin/activate
```
 Run the following commands before running the server:
```bash
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py loaddata data.json
python3 manage.py createsuperuser
```

To run the server:
```bash
python3 manage.py runserver
```

## To run the tests
The tests have been using the pytest and django. To run the tests, run the following command:
```bash
python3 manage.py test
```

## Preloaded users
There are multiple users already preloaded and for all of them the password is **test12345**. The following users have been preloaded in the database:
* Username: **admin_manager**, password: **test12345**
* Username: **customer_service**, password: **test12345**
* Username: **financial_manager**, password: **test12345**
* Username: **production_manager**, password: **test12345**
* Username: **senior_customer_service**, password: **test12345**
* Username: **service_manager**, password: **test12345**
* Username: **subteam_photography**, password: **test12345**
* Username: **subteam_production**, password: **test12345**
