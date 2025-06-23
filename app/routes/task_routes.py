from flask import abort, Blueprint, make_response, request, Response
from app.models.task import Task
from ..db import db
from .route_utilities import validate_model, create_model,get_models_with_filters, send_slack_notification, update_model
from datetime import datetime, timezone
import os
import requests

bp = Blueprint("tasks_bp", __name__, url_prefix = "/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()
    
    return create_model(Task, request_body)

@bp.get("")
def get_all_tasks():
    filters = request.args.to_dict()
    return get_models_with_filters(
            Task, 
            filters,
            sort_attr="title"), 200

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}, 200

@bp.patch("/<task_id>/mark_complete")
def mark_task_as_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    message = f"Someone just completed the task: *{task.title}* ! 🎉"
    send_slack_notification(message)

    return make_response(task.to_dict(), 200)

@bp.patch("/<task_id>/mark_incomplete")
def mark_task_as_incomplete(task_id):
    task = validate_model(Task, task_id)
    
    task.completed_at = None

    db.session.commit()
    return Response(status=204, mimetype="application/json")

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    return update_model(task, request_body)

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")