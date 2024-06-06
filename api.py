import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
class Tft():
    def __init__(self, name, tag) -> None:
        self.api_key = os.getenv("API_KEY")
        self.summonerId = os.getenv("SUMMONER")

        self.url_base = "https://la2.api.riotgames.com"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": f"{self.api_key}"
        }
        self.puuid = self.get_uuid(name, tag)

    def get_url(self, url):
        response = requests.get(url, headers=self.header)
        print("response: ", response.status_code)
        if response.status_code == 404:
            return None
        return response.json()
    
    def get_uuid(self, name, tag):
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
        
        return str(self.get_url(url)['puuid'])


    def tft_league_entries(self):
        url = self.url_base + f"/tft/league/v1/entries/by-summoner/{self.summonerId}"
        print(self.get_url(url))
        
    def mastery(self):
        url = self.url_base + f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.puuid}"
        df = pd.DataFrame(self.get_url(url)) 
        # print(df)
        df.drop("puuid", axis=1, inplace=True)
        # print(df)
        return df.to_dict()

    def spectator(self):
        url = self.url_base + f"/tft/match/v1/matches/by-puuid/{self.puuid}/ids"
        data = self.get_url(url)
        if data:
            df = pd.DataFrame(dict(data)) 
            # df.drop("puuid", axis=1, inplace=True)
            df.to_csv("export2.csv", index=False)
        else:
            print("No hay ninguna partida en curso.")

class Ddragon():
    def __init__(self):
        self.current_version = self.getLastVersion()
        
    def get_url(self, url):
        response = requests.get(url)
        if response.status_code == 404:
            return None
        return response.json()
    
    def getLastVersion(self):
        url = 'https://ddragon.leagueoflegends.com/api/versions.json'
        return self.get_url(url)[0]
    
    def getIndexChamps(self) -> dict:
        champions = {"id": [],
                     "name": []}
        url = f"https://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/es_MX/champion.json"
        data = self.get_url(url)["data"]
        for key, value in data.items():
            champions["id"].append(int(value["key"]))
            champions["name"].append(key)
        
        return champions

    def getChampByName(self, name: str):
        name = name.capitalize()
        url = f"https://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/es_MX/champion/{name}.json"
        data = self.get_url(url)["data"]
        return data[name]

    def getChampByKey(self, key:int ):
        champs = self.getIndexChamps()
        pos = champs["id"].index(key)
        return self.getChampByName(champs["name"][pos])["title"]
        
    def getAllDataChamp(self):
        url = f"https://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/es_MX/champion.json"
        data = self.get_url(url)["data"]
        return data
        
if __name__ == "__main__":
    tft = Tft("Thejairex", "las")
    print(tft.puuid)
    tft.mastery()
    dragon = Ddragon()
    # print(dragon.get_all_champ())
    # print(dragon.getChampByName("JHIN"))
    # print(dragon.getChampByKey(202))
    