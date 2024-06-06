from flask import *
from dotenv import load_dotenv
import os


from api import Tft, Ddragon

load_dotenv()

"""Constansts Values"""
app = Flask(__name__)
dragon = Ddragon()
app.secret_key = 'supersecretkey'
tft = Tft(os.getenv("USERNAME"),os.getenv("TAG"))
base = "https://ddragon.leagueoflegends.com/cdn/14.11.1/img/"
images = {"splash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/", #
          "passive": base + "passive/",          # json.passive.image.full
          "spell": base + "spell/"}             # spell.image.full
print(images)
del base
# imgSplash = base  + "champion/splash/"
# imgPasive = base + "passive/" 
# imgSpell = base + "spell/" 


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


@app.route("/champions/<champName>")
def champRender(champName):
    champInfo = dragon.getChampByName(champName)
    
    return render_template("champ.html", name=champName, json=champInfo, images=images)


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