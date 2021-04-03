mkdir Gojek_Api
git clone https://github.com/dileepnsp/Gojek_Api.git .
cd Gojek_Api
python3 -m venv venv
. venv/bin/activate
pip install - r requirements.txt
cd webapp/Source/
flask run
