import config
import json
import random
import string

import requests

import httplib2
from flask import session as login_session
from flask import (Flask, abort, flash, g, jsonify, make_response, redirect,
                   render_template, request, url_for)
from models import Base, Category, Item, User
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('google_auth.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Config variables used to access the variables in the templates
app.config['GOOGLE_CLIENT_ID'] = config.GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = config.GOOGLE_CLIENT_SECRET


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Show Login Page"""
    state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google Login"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_auth.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    return "You have been logged in"


@app.route('/gdisconnect')
def gdisconnect():
    """Google Logout"""
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    return "You have been logged out"


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook Login"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('facebook_auth.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('facebook_auth.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token'
           '?grant_type=fb_exchange_token'
           '&client_id=%s&client_secret=%s&fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me'
           '?access_token=%s&fields=name,id,email'
           % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    print login_session
    return "You have been logged in"


@app.route('/fbdisconnect')
def fbdisconnect():
    """Facebook Logout"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
           % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"


@app.route('/disconnect')
def disconnect():
    """Disconnect based on provider"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('showHome'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showHome'))


# User Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user.id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
def showHome():
    """This will show all categories with the latest items"""
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(9)

    return render_template(
           'home.html', categories=categories,
           items=items, login_session=login_session)


@app.route('/catalog')
def catalogRedirect():
    """This will redirect /catalog to showHome()"""
    return redirect(url_for('showHome'), code=301)


@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    """This will show all items in a category"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=category).all()

    return render_template(
           'category.html', categories=categories,
           category=category, items=items)


@app.route('/catalog/<string:category_name>/<int:item_id>')
def showItem(category_name, item_id):
    """This will show an item"""
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(id=item_id, category=category).one()

    return render_template('item.html', category=category, item=item)


@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        flash("Please login to create a new item")
        return redirect(url_for('showLogin'))

    categories = session.query(Category).all()

    if request.method == 'GET':
        # This will render a form to add a new item
        return render_template('newitem.html', categories=categories)
    if request.method == 'POST':
        # This will add a new item to the database
        category = session.query(Category).filter_by(
                   name=request.form['category']).one()

        item = Item(name=request.form['name'],
                    description=request.form['description'],
                    category=category,
                    user_id=login_session['user_id'])
        session.add(item)
        session.commit()

        return redirect(url_for('showHome'))


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        flash("If you are the item owner, please login to edit this item")
        return redirect(url_for('showLogin'))

    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()

    # Checks if the current user is not the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("You're not authorized to edit this item")
        return redirect(url_for('showHome'))

    if request.method == 'GET':
        # This will render a form to edit an item
        return render_template(
               'edititem.html',
               categories=categories, item=item)

    if request.method == 'POST':
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
                        'showItem',
                        category_name=item.category.name, item_id=item.id))


@app.route('/catalog/<item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        flash("If you are the item owner, please login to delete this item")
        return redirect(url_for('showLogin'))

    item = session.query(Item).filter_by(id=item_id).one()

    # Checks if the current user is not the owner of the item
    if login_session['user_id'] != item.user_id:
        flash("You're not authorized to delete this item")
        return redirect(url_for('showHome'))

    if request.method == 'GET':
        # This will render a form to delete an item
        return render_template('deleteitem.html', item=item)
    if request.method == 'POST':
        # This will delete an item from the database
        session.delete(item)
        session.commit()
        return redirect(url_for('showHome'))


@app.route('/api/catalog')
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


@app.route('/api/catalog/<string:category_name>')
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


@app.route('/api/catalog/<string:category_name>/<int:item_id>')
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


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
