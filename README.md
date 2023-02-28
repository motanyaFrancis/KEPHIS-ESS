<!-- @format -->

# KEPHIS Portal

## Project Description

KEPHIS website UX design

##### By Enock Abere

![views](static/img/1.png)

### Live link

Visit the application on http://20.231.15.166:98

### Setup & Run Instructions

- Create and activate a virtual environment
- Install the dependencies listed in the requirements.txt
- Create a .env file. This will contain environment variables as listed in the .env.sample file.
- Finally, run your app on MODE='dev' config for debugging purposes

### Development

#### Making modifications

To make advancements/modifications, follow these steps:

- Fork the repository
- Create a new branch (git checkout -b improve-feature)
- Make the appropriate changes in the files
- Add changes made
- Commit your changes (git commit -am 'Improve feature')
- Push to the branch (git push origin improve-feature)
- Create a Pull Requestsou

### Technologies Used

Technologies used to develop this application:

- Python v3.9.5
- Django 3.2.7
- Bootstrap5
- HTML
- CSS

### Support and contact details

Should you be unable to access the website, have any recommendations and/or questions, feel free to email me:[emaeba@kobby.co.ke]

# Passwords to show and hide amount in 2 envelopes

# Tender Stage


## Project Installation
To setup a local development environment:

Create a virtual environment in which to install Python pip packages. With [virtualenv](https://pypi.python.org/pypi/virtualenv),
```bash
virtualenv venv            # create a virtualenv for linux/Unix Users
source venv/bin/activate   # activate the Python virtualenv 
```

or with [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/),
```bash
mkvirtualenv -p python3 {{project_name}}   # create and activate environment
workon {{project_name}}   # reactivate existing environment
```
Install development dependencies,
```bash
pip install -r requirements.txt
```
make Database Migrations,
```bash
python manage.py makemigrations
```
Migrate Database,
```bash
python manage.py migrate
```

Run the web application locally,
```bash
python manage.py runserver 8000 # 127.0.0.1:8000
```

Create Superuser,
```bash
python manage.py createsuperuser
```