#!/bin/bash

NAME="Socket_app"                                       # Name of the application
DJANGODIR= Your project directory
SOCKFILE=Location of the socket file
USER=ubuntu                                                  # the user to run as
GROUP=ubuntu                                           # the group to run as
NUM_WORKERS=1                                              # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=Socket_app.settings     # which settings file should Djangouse
DJANGO_WSGI_MODULE=Socket_app.wsgi                      # WSGI module name
echo "Starting $NAME as `whoami`"

# Activate the virtual environment

cd $DJANGODIR
source /home/ubuntu/webapps/backend/env/bin/activate #activate file location of your environment
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

# below mention code creates a single process that will handle multiple connection with multiple threads

exec gunicorn -k eventlet ${DJANGO_WSGI_MODULE}:application \
 --name $NAME \
 --workers $NUM_WORKERS \
 --user=$USER --group=$GROUP \
 --bind=0.0.0.0:8000 \
 --threads=1000 \
 --log-level=debug \
 --log-file=-