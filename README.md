# Gojek_Api

Install
#######
# clone the repository
$ git clone https://github.com/dileepnsp/Gojek_Api.git
$ cd flask
$ cd webapp/Source


Create a virtualenv and activate it:
####################################

$ python3 -m venv venv
$ . venv/bin/activate

$ pip install - r requirements.txt

Run:
####
$ flask run

API Calls:
##########

http://127.0.0.1:5000/total_trips?start=2019-01-01&end=2019-01-31
http://127.0.0.1:5000/average_fare_heatmap?date=2019-01-01
http://127.0.0.1:5000/avg_speed_24hrs?date=2019-01-01
