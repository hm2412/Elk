# Team Elk Small Group project

## Team members
The members of the team are:
- Rashida Begum
- Alexey Khromin
- Haleema Mohammed
- August Stoele
- Jiaxuan Yu

## Project structure
The project is called `Code Tutors`.  It currently consists of `tutorials`.
It includes a `home page, sign up page, log in page, student dashboard, tutor dashboard and admin dashboard`.

## Deployed version of the application
The deployed version of the application can be found [*here*](https://emilieyu.pythonanywhere.com/).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*Note: if css styling is not visible, clear cache*

## Sources
The packages used by this application are specified in `requirements.txt`
