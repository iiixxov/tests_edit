from flask import Flask
from app.database import database


app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


from app import routes
