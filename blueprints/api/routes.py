from blueprints import session
from flask import Blueprint, jsonify
from models import Category, Item

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
