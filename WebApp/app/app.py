from flask import Flask, render_template, request, flash, url_for, redirect
import os 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import pymongo

MONGO_URI = "localhost:27017"
MONGO_DB = "news"
MONGO_COLLECTION = "sebenarnya_v2_proccessed2"
    
app = Flask(__name__)

app_data = {
    "name":         "UniJagung Search Engine",
    "description":  "A Search Engine for COVID-19 Fake News",
    "html_title":   "UniJagung Search Engine",
    "project_name": "UniJagung Search Engine",
    "keywords":     "UniJagung Search Engine"
}
app.config.from_object(__name__)
SECRET_KEY = os.environ.get("flask_secret")
app.config.update(dict(
    SECRET_KEY=SECRET_KEY,
    WTF_CSRF_SECRET_KEY=SECRET_KEY
))

# @app.route('/')
# def index():
#     return render_template('index.html', app_data=app_data)

# class SearchForm(FlaskForm):
#     search = StringField('Search', validators=[DataRequired()])
    
@app.route("/", methods=['GET'])
def index():
    dp = {}  
    return render_template('index.html', dp = dp)
  
@app.route("/search", methods=['GET'])
def get_search():
    return redirect("/")

@app.route("/search", methods=['POST'])
def results():
    print(request.form)
    dp = request.form
    dp2 = {}
    if dp is not None:
        keyword = dp.get("keyword")
        dp2["keyword"] = keyword
        coll = pymongo.MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]
        result = list(coll.find({"$text":{"$search": keyword}}))
        dp2["result"] = result
        dp2["result_len"] = len(result)
        print(len(result))
        return render_template('search.html', dp = dp2)
    
    
    
    
#     if form.validate():
#         # Save the comment here.
#         flash('Hello ' + name)
#     else:
#         flash('All the form fields are required. ')

    

# @app.route('/b1')
# def b1():
#     return render_template('b1.html', app_data=app_data)

# @app.route('/b2')
# def b2():
#     return render_template('b2.html', app_data=app_data)

# @app.route('/b3')
# def b3():
#     return render_template('b3.html', app_data=app_data)
