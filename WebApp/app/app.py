from flask import Flask, render_template, request, flash, url_for, redirect
import os 
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import pymongo
import requests
from .helper_news import search, get_top_news, predict

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

Prediction = {}
Prediction[0] = {"header": "Fact", "caption": "Feel free to share!", "logic": "Verified news from at least 2 sources, did not appear as Fake News Alert."}
Prediction[1] = {"header": "Latest News", "caption": "Not advisable to share immediately!", "logic": "Verified news from 1 source only, did not appear as FakeNewsAlert."}
Prediction[2] = {"header": "No Search Results", "caption": "Avoid sharing unverified news or rumours!", "logic": "No search results."}
Prediction[3] = {"header": "Precautions Needed", "caption": "Please take precautions and manually check the news authenticity from at least 2 verified news sources before sharing!", "logic": "Appear in both Verified New and Fake News Alert."}
Prediction[4] = {"header": "Suspected Fake News", "caption": "Avoid sharing unverified news or rumours!", "logic": "Appear in Fake News Alert."}

# deprecated
def mongo_search(keyword):
    coll = pymongo.MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]
    result = list(coll.find({"$text":{"$search": keyword}}))
    return result

# def search(keyword, max_results = 10):
#     result = requests.get(f"http://localhost:9200/news/_search?q={keyword}")
#     x = result.json().get("hits").get("hits")[0:max_results]
#     titles = [j.get("_source").get("title") for j in x]
#     urls = [j.get("_source").get("url") for j in x]
#     categories = [j.get("_source").get("category") for j in x]
#     sources = [j.get("_source").get("news_vendor") for j in x]
#     scores = [j.get("_score") for j in x]
#     result_dict = dict(title = titles, url = urls, category = categories, source = sources, score = scores)
#     return result_dict

    
@app.route("/", methods=['GET'])
def index():
    dp = {}  
    return render_template('index.html', dp = dp)
  
@app.route("/search", methods=['GET'])
def get_search():
    return redirect("/")

@app.route("/search_old", methods=['POST'])
def results():
    dp = request.form
    dp2 = {}
    if dp is not None:
        keyword = dp.get("keyword")
        dp2["keyword"] = keyword
        result_dict = search(keyword)
        
        # search
        r = search(keyword, index="all_news")
        ddf_fna, n_fna, mscore_fna = get_top_news(r, category = "FakeNewsAlert")
        ddf_news, n_news, mscore_news = get_top_news(r, category = "News")
        idx = predict(n_fna, n_news, mscore_fna, mscore_news)
        pred = Prediction[idx]
        
        # assign to render
#         dp2["ddf_fna"] = ddf_fna
        
        return render_template('search.html', dp = dp2, 
                               keyword = keyword,
                               n_fna = n_fna, n_news = n_news,
                               ddf_fna = ddf_fna, ddf_news = ddf_news,
                               pred = pred
                              )
    
@app.route("/search", methods=['GET', 'POST'])
def results2():
    dp = request.form
    dp2 = {}
    if dp is not None:
        keyword = dp.get("keyword")
        dp2["keyword"] = keyword
        
        # search
        r = search(keyword, index = "all_news")
        ddf_fna, n_fna, mscore_fna = get_top_news(r, category = "FakeNewsAlert")
        ddf_news, n_news, mscore_news = get_top_news(r, category = "News")
        
        show_result = 1
        if keyword is None or keyword.strip() == "":
            show_result = 0
            
        n = [n_fna, n_news]
        ddf = [ddf_fna, ddf_news]
        title = ["Fake News Alert", "Verified News"]
            
        idx = predict(n_fna, n_news, mscore_fna, mscore_news)
        pred = Prediction[idx]
        
        # assign to render
#         dp2["ddf_fna"] = ddf_fna
        
        return render_template('search2.html', dp = dp2, 
                               keyword = keyword,
                               n = n,
                               ddf = ddf,
                               title = title,
                               show_result = show_result,
#                                n_fna = n_fna, n_news = n_news,
#                                ddf_fna = ddf_fna, ddf_news = ddf_news,
                               pred = pred
                              )
    
@app.route("/monitor", methods = ['GET'])
def monitor():
    return render_template('monitor.html')