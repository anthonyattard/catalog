import config
import json
import os
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

from blueprints.api.routes import api
from blueprints.site.routes import site
from blueprints.authc.routes import authc

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(authc)
app.register_blueprint(site)