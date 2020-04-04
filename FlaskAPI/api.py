import datetime
import pymongo
from flask import Flask
from flask_restx import Api, Resource, fields
from flask import request

app = Flask(__name__)
api = Api(app, version='1.0', title='SEBENARNYA.MY News API',
    description='An API to counter COVID-19 Fake News.',
)

ns = api.namespace('news', description='Query SEBENARNYA.MY news/articles.')


# content_fields = {}
# content_fields["SEBENARNYA"] = fields.String()
# content_fields["PENJELASAN"] = fields.String()
# content_fields["PALSU"] = fields.String()
# content_fields["TIDAK BENAR"] = fields.String()

fact_src_fields = api.model('FactSource', {
    'text': fields.String,
    'link': fields.String,
})

content_fields = api.model('Content', {
    'header': fields.String,
    'text': fields.String,
})

model = api.model('News', {
    'title': fields.String(required=False, description='The news title'),
    'date': fields.DateTime(dt_format='rfc822'),
    'content_text': fields.List(fields.Nested(content_fields)),
    'fact_src': fields.Nested(fact_src_fields),
    'label': fields.Integer(),
    'confidence': fields.Integer(),
    'category': fields.String(required=False, description='The news category'),
    'url': fields.String(required=False, description='The news url'),
    
})

class News(object):
    def __init__(self):
        client = pymongo.MongoClient()
        db = client["news"]
#         self.coll = db["sebenarnya_v2_test1"]
        self.coll = db["sebenarnya_v2_proccessed1"]
    
    def get(self, **kwargs):
        if len(kwargs) == 0:
            sample_kwargs = kwargs = { 
                                      "start_date": None,
                                      "end_date": datetime.datetime.today(),
                                      "category": "COVID-19",
                                      "search": "Hebahan", 
                                      "label": 1,
                                      "confidence": 1,
                                      "limit":10
            }
            
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        category = kwargs.get("category")
        search = kwargs.get("search")
        label = kwargs.get("label")
        confidence = kwargs.get("confidence")
        limit = kwargs.get("limit")
        
        filter_query = {}
        if category is not None:
            filter_query["category"] = category
            
        if search is not None:
            search = '\"' + search + '\"'
            filter_query["$text"] = {"$search": search}
        
        if start_date is None:
            start_date = datetime.datetime(2000,1,1)
        else:
            try:
                start_date = parser.parse(start_date)
            except:
                start_date = datetime.datetime(2000,1,1)
            
        if end_date is None:
            end_date = datetime.datetime.today()
        else:
            try:
                end_date = parser.parse(end_date)
            except:
                end_date = datetime.datetime.today()
        
        if label is not None:
            filter_query["label"] = int(label)
        
        if confidence is not None:
            filter_query["confidence"] = int(confidence)
            
        filter_query["date"] = {"$gte": start_date, "$lte": end_date}
            
        enabled_projection = ["title", "date", "content_text", 
                              "category", "fact_src", "label", "confidence", "url"]
        proj = {key:1 for key in enabled_projection}
        
        if limit is None:
            x = list(self.coll.find(filter_query, proj))
        else:
            limit = int(limit)
            x = list(self.coll.find(filter_query, proj).limit(limit))
            
        if x is None:
            return {}
        else:
            return x
   
NEWS = News()

from flask_restx import reqparse

@ns.route('/')
@ns.response(404, 'News/article not found')
@ns.param('category', 'The news category')
@ns.param('start_date', 'Query start date')
@ns.param('end_date', 'Query end date')
@ns.param('search', 'Search news title')
@ns.param('label', 'Label')
@ns.param('confidence', 'Confidence of the label')
@ns.param('limit', 'Limit results')
class Todo(Resource):
    '''Query news from given parameters'''
    @ns.doc('get_todo')
    @ns.marshal_with(model)
    def get(self):
        '''Fetch a given resource'''
        return NEWS.get(**request.args)

if __name__ == '__main__':
    app.run(debug=True)