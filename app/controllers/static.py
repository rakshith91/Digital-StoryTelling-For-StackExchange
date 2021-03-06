from flask import send_from_directory, render_template, abort, redirect
from flask import Blueprint
from jinja2 import TemplateNotFound

STATIC_PATH = "static"

root_handler = Blueprint('root_handler', __name__)

@root_handler.route('/')
def hande_root():
	return redirect('/main/')

@root_handler.route('/main/')
def hande_main():
	return send_from_directory(STATIC_PATH, 'index.html')
