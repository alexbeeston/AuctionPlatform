# Background
This project was developed by a team of four students as a class project for CS3450, Introduction to Software Engineering, at Utah State University. The code was developed over the Fall 2019 semester and provides a platform for a small-scale local auction, both live and silent. The platform runs over a local networt.

## Build instructions
Dependencies
1. python (version 3.7 or greater)
2. pipenv

After cloning the repository, run the following commands in the root-level directory of the repository:
1. pipenv install
2. pipenv shell
3. python manage.py runserver [port number]

## Tool stack description and setup procedure
- Django version 2.2
- SQLLite (default database for Django)
- HTML5 and Javascript
  
## Unit and system testing instructions
- uses Django's built in test framework; all tests are in auction_app/test.py
- test with "python manage.py test"
