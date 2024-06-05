from flask import *
from dotenv import load_dotenv
from jinja2 import Environment
import os


from api import Tft, Ddragon

app = Flask(__name__)
load_dotenv()
app.secret_key = 'supersecretkey'
# print(os.getenv("USERNAME"),os.getenv("TAG"))
tft = Tft(os.getenv("USERNAME"),os.getenv("TAG"))
dragon = Ddragon()

# Función personalizada que envuelve la función type()
def get_type(obj):
    return type(obj)

# Crear un entorno de Jinja
env = Environment()

# Agregar la función personalizada al entorno de Jinja
env.globals['type'] = get_type


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mastery")
def mastery():
    championId = session.get("championId")
    championName = session.get("championName")
    championLevel = session.get("championLevel")
    championPoint = session.get("championPoint")
    milestoneGrades = session.get("milestoneGrades")
    
    return render_template("mastery.html", championId= championId,
                           championName = championName, 
                           championLevel= championLevel,
                           championPoint =championPoint ,
                           milestoneGrades = milestoneGrades)

@app.route("/api/mastery")
def api_mastery():
    json = tft.mastery()
    champs = dragon.getIndexChamps()
    for id, key in json["championId"].items():
        i = champs["id"].index(key)
        json["championId"][id] = champs["name"][i]
    
    for id, key in json["milestoneGrades"].items():
        value = json["milestoneGrades"][id]
        if type(value) == float:
            json["milestoneGrades"][id]  = []
    
    session["championId"] = list(json["championId"].keys())
    session["championName"] = list(json["championId"].values())
    session["championLevel"] = list(json["championLevel"].values())
    session["championPoint"] = list(json["championPoints"].values())
    session["milestoneGrades"] = list(json["milestoneGrades"].values())
    
    return redirect(url_for("mastery"))

@app.route("/api/mastery/show")
def api_mastery_show():
    json = tft.mastery()
    champs = dragon.getIndexChamps()
    
    for id, key in json["championId"].items():
        i = champs["id"].index(key)
        json["championId"][id] = champs["name"][i]

    return jsonify(json["milestoneGrades"])

if __name__ == "__main__":
    app.run(debug=True)