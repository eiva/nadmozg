#!/bin/sh
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
heroku plugins:install heroku-container-registry
docker login -e _ -u _ --password=$HEROKU_API_KEY registry.heroku.com
heroku ps:scale worker=1
heroku container:push worker --app $HEROKU_APP_NAME
