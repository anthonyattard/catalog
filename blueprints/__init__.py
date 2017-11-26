import config
import json
from flask import Flask
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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