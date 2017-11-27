from blueprints import session
import dicttoxml
from flask import Blueprint, jsonify, request
from models import Category, Item

api = Blueprint('api', __name__)


@api.route('/catalog')
def catalogAPI():
    """Returns a catalog data object"""
    output = []
    categories = session.query(Category).all()
    for category in categories:
        items = session.query(Item).filter_by(category_id=category.id)
        category_output = {}
        category_output["id"] = category.id
        category_output["name"] = category.name
        category_output["Item"] = [i.serialize for i in items]
        output.append(category_output)

    return formatData(output, "Category")


@api.route('/catalog/<string:category_name>')
def categoryAPI(category_name):
    """Returns a category and its items as data objects"""
    output = []

    # Check to see if category and category items exist
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category.id)

        category_output = {}
        category_output["id"] = category.id
        category_output["name"] = category.name
        category_output["Item"] = [item.serialize for item in items]
        output.append(category_output)

        return formatData(output, "Category")
    except:
        return formatData(output, "Category")


@api.route('/catalog/<string:category_name>/<int:item_id>')
def itemAPI(category_name, item_id):
    """Returns an item data object"""
    output = []

    # Check to see if the item exists
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(
                  id=item_id, category=category).one()
        output = [item.serialize]

        return formatData(output, "Item")
    except:
        return formatData(output, "Item")


# API Helper Functions
def formatData(output, collection):
    """Returns a data object as json(default) or xml"""
    format = request.args.get('format')
    # If query string for key format is xml
    if format == 'xml' or format == 'XML':
        # This will return the catalog in XML format
        xml_output = dicttoxml.dicttoxml(output)
        return xml_output, 200, {'Content-Type': 'text/xml; charset=utf-8'}
    # If no query string is passed or any query other than format=xml is passed
    else:
        # Returns the catalog in JSON format.
        return jsonify({collection: output})
