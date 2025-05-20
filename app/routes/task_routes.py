from flask import abort, Blueprint, make_response, request, Response
from app.models.task import Task
from app.models.goal import Goal
from ..db import db
from sqlalchemy import cast, String, Integer
from .route_utilities import validate_model
from datetime import datetime
import os
import requests

bp = Blueprint("tasks_bp", __name__, url_prefix = "/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()
    try:
        new_task = Task.from_dict(request_body)

    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    tasks = db.session.execute(query).scalars().all()

    sort_order_param = request.args.get("sort", "asc")
    if sort_order_param == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.title.asc())

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    
    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    completed_at_param =request.args.get("completed_at")
    if completed_at_param:
        query = query.where(Task.completed_at.ilike(f"%{completed_at_param}%"))

    is_complete_param = request.args.get("is_complete")
    if is_complete_param:
        # is_complete_bool = is_complete_param.lower() == "true"
        # query = query.where(Task.is_complete == is_complete_bool)

        if is_complete_param.lower() == "true":
            query = query.where(Task.task_completed == True)
        elif is_complete_param.lower() == "false":
            query = query.where(Task.task_completed == False)

    query = query.order_by(Task.id)
    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())
    return tasks_response, 200


@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}, 200

@bp.patch("/<task_id>/mark_complete")
def mark_task_as_complete(task_id):
    task = validate_model(Task, task_id)

    # task.is_complete = True
    task.completed_at = datetime.now()

    db.session.commit()

    slack_token = os.environ.get("SLACKBOT_API_TOKEN")
    slack_channel = "sno-task-tracker-bot2"
    slack_text = f"Someone just completed the task {task.title}! 🎉"

    if slack_token:
        url =  "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        message_request_body = {
            "channel": slack_channel,
            "text": slack_text

        }
        requests.post(url, headers=headers, json=message_request_body)
    
    return Response(status=204, mimetype="application/json")
    # return {"task": task.to_dict()}, 200

@bp.patch("/<task_id>/mark_incomplete")
def mark_task_as_incomplete(task_id):
    task = validate_model(Task, task_id)
    
    # task.is_complete = False
    task.completed_at = None

    db.session.commit()
    return Response(status=204, mimetype="application/json")
    # return {"task": task.to_dict()}, 200

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")