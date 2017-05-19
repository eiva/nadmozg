#! /bin/bash
while :
do

rm -rf .ve

git pull

virtualenv -p python3 .ve
source ./.ve/bin/activate
pip install -r requirements.txt

(
cd src
python app.py
)

sleep 10

done
