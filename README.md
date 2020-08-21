# Trad
Website for collaborative translation of videos and subtitles.


## Usage

### Requirements
- Python 3.6 / Django 3.1 (might work with others version but has only be tested with this one)

### Installation
- Clone this repo to your local machine using `https://github.com/damien-dd/trad`
```
git clone https://github.com/damien-dd/trad
```

- Create python virtual environment and install Django into it (if not already done)
```
cd trad
python3 -m venv venv
source venv/bin/activate
pip install Django==3.1
```

- Install all required dependencies 
```
pip install -r requirements.txt
```

- Set up and create all database tables
./manage.py migrate
By default it will use SQLite database which shall only be used for test. For production you can setup another database backend in [settings.py](trad/settings.py)


### Run the test server
- Run the test server within the virtual environment
```
./manage.py runserver
```

- Open a web browser and go to http://127.0.0.1:8000

