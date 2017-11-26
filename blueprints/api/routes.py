from flask import Blueprint

import config
import json
import random
import string

import requests

import httplib2
from flask import session as login_session
from flask import (Flask, abort, flash, g, jsonify, make_response, redirect,
                   render_template, request, url_for)
from forms import ItemForm
from models import Base, Category, Item, User
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from blueprints import session

api = Blueprint('api', __name__)

@api.route('/catalog')
def catalogJSON():
    """This will return the catalog in JSON format"""
    output_json = []
    categories = session.query(Category).all()
    for category in categories:
        items = session.query(Item).filter_by(category_id=category.id)
        category_output = {}
        category_output["id"] = category.id
        category_output["name"] = category.name
        category_output["Item"] = [i.serialize for i in items]
        output_json.append(category_output)
    return jsonify(Categories=output_json)


@api.route('/catalog/<string:category_name>')
def categoryJSON(category_name):
    """This will return a specific category and its items in JSON format"""
    output_json = []

    # Check to see if category and category items exist
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category.id)

        category_output = {}
        category_output["id"] = category.id
        category_output["name"] = category.name
        category_output["Item"] = [item.serialize for item in items]
        output_json.append(category_output)

        return jsonify(Category=output_json)
    except:
        return jsonify(Category=output_json)


@api.route('/catalog/<string:category_name>/<int:item_id>')
def itemJSON(category_name, item_id):
    """This will return an item in JSON format"""

    # Check to see if the item exists
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(
                  id=item_id, category=category).one()

        return jsonify(Item=[item.serialize])
    except:
        return jsonify(Item=[])
