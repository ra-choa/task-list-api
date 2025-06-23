from flask import abort, Blueprint, make_response, request, Response
from app.models.task import Task
from app.models.goal import Goal
from ..db import db
from .route_utilities import validate_model, create_model, get_models_with_filters, update_model


bp = Blueprint("goals_bp", __name__, url_prefix = "/goals")


@bp.post("") 
def create_goal():
    request_body = request.get_json()

    return create_model(Goal, request_body)

@bp.get("/<goal_id>")
def get_one_goal_by_id(goal_id):
    goal = validate_model(Goal, goal_id)

    return {"goal": goal.to_dict()}, 200

@bp.get("")
def get_all_goals():
        filters = request.args.to_dict()
        return get_models_with_filters(
            Goal, 
            filters,
            sort_attr="title"), 200

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    return update_model(goal, request_body)

@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.post("/<goal_id>/tasks")
def assign_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])

    valid_tasks = []
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        valid_tasks.append(task)

    goal.tasks = valid_tasks
    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200

@bp.get("/<goal_id>/tasks")
def get_tasks_for_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    tasks_response = []
    for task in goal.tasks:
        task_dict = task.to_dict()
        task_dict["goal_id"] = goal.id
        tasks_response.append(task_dict)

    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": tasks_response
    }, 200