#!/bin/sh

if [[ $VIRTUAL_ENV -ne "/Users/sam/Web/Volla/venv" ]]; then
    echo "The virtual env hasn't been activated!"
    exit 1
fi

python manage.py test
git push heroku master
