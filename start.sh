#!/bin/bash
# start.sh

nohup celery -A backend_tasks.task_manage.celery_app worker --loglevel=info --logfile=celery.log &

sleep 10

nohup uvicorn app:app --host 0.0.0.0 --port 6895 --reload &

wait