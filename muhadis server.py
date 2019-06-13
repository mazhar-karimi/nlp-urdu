import islamicqa
from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify 

app = Flask(__name__,static_url_path='')
api = Api(app)

class Search(Resource):
    def get(self, question):        
        hadiths =  islamicqa.getanswer(question, strict=False)
        result = {'hadiths': hadiths}       
        return jsonify(result)
    
#api.add_resource(Js1, '/js/<filename>') 

api.add_resource(Search, '/search/<question>')

@app.route('/js/<path:path>')
def get_js(path):
    return send_from_directory('Muhaddis/js', path)

@app.route('/css/<path:path>')
def get_css(path):
    return send_from_directory('Muhaddis/css', path)

@app.route('/images/<path:path>')
def get_images(path):
    return send_from_directory('Muhaddis/images', path)

@app.route('/fonts/<path:path>')
def get_fonts(path):
    return send_from_directory('Muhaddis/fonts', path)

@app.route('/')
def get_():
    return send_from_directory('Muhaddis', "index.html")

if __name__ == '__main__':
     app.run(port='5002')