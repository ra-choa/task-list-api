from flask import abort, make_response, Response
from ..db import db
import os
import requests

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response , 400))
    
    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError as e:
        response = {"message": f"Invalid request: missing {e.args[0]}"}
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201


def get_models_with_filters(cls, filters=None, sort_attr="id"):
    query = db.select(cls)

    if filters:
        for attribute, value in filters.items():
            if hasattr(cls, attribute):
                query = query.where(getattr(cls, attribute).ilike(f"%{value}%"))
        
        sort_order = filters.get("sort", "asc")
        if sort_order == "desc":
            query = query.order_by(getattr(cls, sort_attr).desc())
        else:
            query = query.order_by(getattr(cls, sort_attr).asc())
    else:
        query = query.order_by(getattr(cls, sort_attr))

    models = db.session.scalars(query)
    return [model.to_dict() for model in models]


def send_slack_notification(message):
    slack_token = os.environ.get("SLACKBOT_API_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL")

    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
        }
    data = {
        "channel": slack_channel,
        "text": message
        }
    slack_response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=data)

    if not slack_response.ok:
            print("Slack error:", slack_response.text)  

def update_model(obj, data):
    for attr, value in data.items():
        if hasattr(obj, attr):
            setattr(obj, attr, value)

    db.session.commit()
    return Response(status=204, mimetype="application/json")
