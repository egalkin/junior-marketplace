#!/bin/bash
export DIR="$(pwd)" 
cd $DIR/marketplace.app/marketplace/content
export FLASK_APP=data_app.py
flask run &
python3 delete_content.py
cd $DIR
export OUTPUT="$(ps aux | grep flask | head -n 1 | awk '{print $2}')"
kill $OUTPUT
export FLASK_APP=runserver.py
exec bash

