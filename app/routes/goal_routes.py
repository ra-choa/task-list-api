from flask import abort, Blueprint, make_response, request, Response
from app.models.task import Task
from app.models.goal import Goal
from ..db import db
from sqlalchemy import cast, String, Integer
from .route_utilities import validate_model
from datetime import datetime
import os
import requests

bp = Blueprint("goals_bp", __name__, url_prefix = "/goals")


@bp.post("") 
def create_goal():  
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)

    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))
        
    db.session.add(new_goal)
    db.session.commit()

    return {"goal": new_goal.to_dict()}, 201

@bp.get("/<goal_id>")
def get_one_goal_by_id(goal_id):
    goal = validate_model(Goal, goal_id)

    # response = [goal.to_dict() for goal in goal.goals]
    return {"goal": goal.to_dict()}, 200

@bp.get("")
def get_all_goals():
    query = db.select(Goal)
    goals = db.session.execute(query).scalars().all()

    sort_order_param = request.args.get("sort", "asc")
    if sort_order_param == "desc":
        query = query.order_by(Goal.title.desc())
    else:
        query = query.order_by(Goal.title.asc())

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Goal.title.ilike(f"%{title_param}%"))

    query = query.order_by(Goal.id)
    goals = db.session.scalars(query)

    goals_response = []
    for goal in goals:
        goals_response.append(goal.to_dict())
    return goals_response, 200


@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")

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
    
    for task in goal.tasks:
        task.goal_id = None
        
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        task.goal_id = goal.id

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