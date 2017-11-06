from models import Base, Category, Item
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import desc
from flask import session as login_session
import random, string

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state


@app.route('/')
def showHome():
    """This will show all categories with the latest items"""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(9)

    return render_template('home.html', categories=categories, items=items)


@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    """This will show all items in a category"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=category).all()

    return render_template('category.html', categories=categories, category=category, items=items)


@app.route('/catalog/<string:category_name>/<int:item_id>')
def showItem(category_name, item_id):
    """This will show an item"""
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(id=item_id, category=category).one()

    return render_template('item.html', category=category, item=item)
    

@app.route('/catalog/new', methods = ['GET', 'POST'])
def newItem():
    categories = session.query(Category).all()
    if request.method == 'GET':
        # This will render a form to add a new item
        return render_template('additem.html', categories=categories)
    if request.method == 'POST':
        # This will add a new item to the database
        category = session.query(Category).filter_by(name=request.form['category']).one()

        item = Item(name=request.form['name'],
                    description=request.form['description'],
                    category=category)
        session.add(item)
        session.commit()

        return redirect(url_for('showHome'))


@app.route('/catalog/<int:item_id>/edit', methods = ['GET', 'POST'])
def editItem(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'GET':
        # This will render a form to edit an item
        return render_template('edititem.html', categories=categories, item=item)

    if request.method == 'POST':
        # This will commit the item edit to the database
        item.category = item.category
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category = session.query(Category).filter_by(name=request.form['category']).one()
        session.add(item)
        session.commit()

        return redirect(url_for('showItem', category_name=item.category.name, item_id=item.id))


@app.route('/catalog/<item_id>/delete', methods = ['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'GET':
        # This will render a form to delete an item
        return render_template('deleteitem.html', item=item)
    if request.method == 'POST':
        # This will delete an item from the database
        session.delete(item)
        session.commit()
        return redirect(url_for('showHome'))


@app.route('/catalog.json')
def catalogJSON():
    return "This will return the catalog in JSON format"


@app.route('/catalog/<category>.json')
def categoryJSON(category):
    return "This will return a specific category and its items in JSON format"


@app.route('/catalog/<category>/<item_name>.json')
def itemJSON(category, item_name):
    return "This will return an item in JSON format"


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)
    