from flask import session as login_session
from flask import Blueprint, flash, redirect, render_template, request, url_for
from forms import ItemForm
from models import Category, Item
from sqlalchemy import desc

from blueprints import session

site = Blueprint('site', __name__)

@site.route('/homepage')
def homepage():
    return "<h1>homepage</h1>"


@site.route('/')
def showHome():
    """This will show all categories with the latest items"""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(9)

    return render_template(
           'home.html', categories=categories,
           items=items, login_session=login_session)


@site.route('/catalog')
def catalogRedirect():
    """This will redirect /catalog to showHome()"""
    return redirect(url_for('site.showHome'), code=301)


@site.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    """This will show all items in a category"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=category).all()

    return render_template(
           'category.html', categories=categories,
           category=category, items=items)


@site.route('/catalog/<string:category_name>/<int:item_id>')
def showItem(category_name, item_id):
    """This will show an item"""
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(id=item_id, category=category).one()

    return render_template('item.html', category=category, item=item)


@site.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        flash("Please login to create a new item")
        return redirect(url_for('site.showLogin'))

    categories = session.query(Category).all()

    # This loads the ItemForm into a local variable
    form = ItemForm(request.form)

    if request.method == 'GET':
        # This will render a form to add a new item
        return render_template('newitem.html', categories=categories, form=form)
    if request.method == 'POST':
        # This checks whether the form passes validation
        if form.validate():
            # This will add a new item to the database
            category = session.query(Category).filter_by(
                       name=request.form['category']).one()

            item = Item(name=request.form['name'],
                        description=request.form['description'],
                        category=category,
                        user_id=login_session['user_id'])
            session.add(item)
            session.commit()

            return redirect(url_for('site.showHome'))
        else:
            # This will run if the form fails validation
            return render_template('newitem.html', categories=categories, form=form)



@site.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        flash("If you are the item owner, please login to edit this item")
        return redirect(url_for('site.showLogin'))

    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()

    # Checks if the current user is not the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("You're not authorized to edit this item")
        return redirect(url_for('site.showHome'))

    # This loads the ItemForm into a local variable
    form = ItemForm(request.form)

    if request.method == 'GET':
        # This will render a form to edit an item
        form.name.data = item.name
        form.description.data = item.description
        return render_template(
               'edititem.html',
               categories=categories, item=item, form=form)

    if request.method == 'POST':
        # This checks whether the form passes validation
        if form.validate():
            # This will commit the item edit to the database
            item.category = item.category
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            if request.form['category']:
                item.category = session.query(Category).filter_by(
                                name=request.form['category']).one()
            session.add(item)
            session.commit()

            return redirect(url_for(
                            'site.showItem',
                            category_name=item.category.name, item_id=item.id))
        else:
            # This will run if the form fails validation
            return render_template(
                   'edititem.html',
                   categories=categories, item=item, form=form)


@site.route('/catalog/<item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        flash("If you are the item owner, please login to delete this item")
        return redirect(url_for('authc.showLogin'))

    item = session.query(Item).filter_by(id=item_id).one()

    # Checks if the current user is not the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("You're not authorized to delete this item")
        return redirect(url_for('site.showHome'))

    if request.method == 'GET':
        # This will render a form to delete an item
        return render_template('deleteitem.html', item=item)
    if request.method == 'POST':
        # This will delete an item from the database
        session.delete(item)
        session.commit()
        return redirect(url_for('site.showHome'))