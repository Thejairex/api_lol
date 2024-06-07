import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()


class League():
    def __init__(self, name, tag) -> None:
        self.name = name
        self.tag = tag
        self.api_key = os.getenv("API_KEY")
        self.summonerId = os.getenv("SUMMONER")

        self.url_base = "https://la2.api.riotgames.com"
        self.region_base = "https://americas.api.riotgames.com/"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": f"{self.api_key}"
        }
        self.puuid = self.get_uuid(self.name, self.tag)

    def get_url(self, url):
        response = requests.get(url, headers=self.header)
        print("response: ", response.status_code)
        if response.status_code == 404:
            return None
        return response.json()

    def get_multiple_urls(self, urls):
        results = []

        def fetch_url(url):
            response = requests.get(url, headers=self.header)
            return response.json()

        # Utiliza un ThreadPoolExecutor para ejecutar las solicitudes en paralelo
        with ThreadPoolExecutor(max_workers=15) as executor:
            # Mapea las URL a las funciones de solicitud y ejecuta en paralelo
            futures = [executor.submit(fetch_url, url) for url in urls]

            # Recopila los resultados de las solicitudes
            for future in futures:
                results.append(future.result())

        return results

    def get_uuid(self, name, tag):
        url = self.region_base + \
            f"riot/account/v1/accounts/by-riot-id/{name}/{tag}"

        return str(self.get_url(url)['puuid'])

    def mastery(self):
        url = self.url_base + \
            f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{
                self.puuid}"
        df = pd.DataFrame(self.get_url(url))
        # print(df)
        df.drop("puuid", axis=1, inplace=True)
        # print(df)
        return df.to_dict()

        url = self.url_base + \
            f"/tft/match/v1/matches/by-puuid/{self.puuid}/ids"
        data = self.get_url(url)
        if data:
            df = pd.DataFrame(dict(data))
            # df.drop("puuid", axis=1, inplace=True)
            df.to_csv("export2.csv", index=False)
        else:
            print("No hay ninguna partida en curso.")

    def summoner(self):
        url = self.url_base + \
            f"/lol/summoner/v4/summoners/by-puuid/{self.puuid}"
        data = self.get_url(url)
        json = {
            "gameName": f"{self.name}#{self.tag}",
            "profileIconId": data["profileIconId"],
            "summonerLevel": data["summonerLevel"]}
        del data
        return json

    def matchs(self):
        winrate = {
            "totalGames": 0,
            "win": 0,
            "lose": 0
        }
        roles = {
            "TOP": {"games": 0, "wins": 0, "lose": 0},
            "JUNGLE": {"games": 0, "wins": 0, "lose": 0},
            "MIDDLE": {"games": 0, "wins": 0, "lose": 0},
            "BOTTOM": {"games": 0, "wins": 0, "lose": 0},
            "UTILITY": {"games": 0, "wins": 0, "lose": 0},
        }
        champions = {

        }

        url = self.region_base + \
            f"/lol/match/v5/matches/by-puuid/{self.puuid}/ids?count={45}"
        matches = self.get_url(url)
        matches_details_urls = [
            self.region_base + f"/lol/match/v5/matches/{matchId}" for matchId in matches]

        for match_detail in self.get_multiple_urls(matches_details_urls):
            index = match_detail["metadata"]["participants"].index(self.puuid)
            win = match_detail["info"]["participants"][index]["win"]
            role = match_detail["info"]["participants"][index]["teamPosition"]
            championId = match_detail["info"]["participants"][index]["championId"]
            championName = match_detail["info"]["participants"][index]["championName"]
            
            if role:
                roles[role]["games"] += 1
                if win:
                    roles[role]["wins"] += 1
                else:
                    roles[role]["lose"] += 1
            if championId not in champions:
                champions[championId] = {
                    "name": championName,
                    "games": 0,
                    "wins": 0,
                    "lose": 0
                }
            
            if win:
                winrate["win"] += 1
                champions[championId]["wins"] += 1
            else:
                winrate["lose"] += 1
                champions[championId]["lose"] += 1

            winrate["totalGames"] += 1
            champions[championId]["games"] += 1

        champions = dict(sorted(champions.items(), key=lambda item: item[1]["games"], reverse=True))
        return {"winrate": winrate, "roles": roles, "champions": champions}


class Ddragon():
    def __init__(self):
        self.current_version = self.getLastVersion()

        # const
        base = f"https://ddragon.leagueoflegends.com/cdn/{
            self.current_version}/img/"
        self.images = {"splash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/",
                       "passive": base + "passive/",          # json.passive.image.full
                       "spell": base + "spell/",
                       "profileIcon": base + "profileicon/"}

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
        url = f"https://ddragon.leagueoflegends.com/cdn/{
            self.current_version}/data/es_MX/champion.json"
        data = self.get_url(url)["data"]
        for key, value in data.items():
            champions["id"].append(int(value["key"]))
            champions["name"].append(key)
        del data
        return champions

    def getChampByName(self, name: str):
        name = name.capitalize()
        url = f"https://ddragon.leagueoflegends.com/cdn/{
            self.current_version}/data/es_MX/champion/{name}.json"
        data = self.get_url(url)["data"]
        return data[name]

    def getChampByKey(self, key: int):
        champs = self.getIndexChamps()
        pos = champs["id"].index(key)
        return self.getChampByName(champs["name"][pos])["title"]

    def getAllDataChamp(self):
        url = f"https://ddragon.leagueoflegends.com/cdn/{
            self.current_version}/data/es_MX/champion.json"
        data = self.get_url(url)["data"]
        return data


if __name__ == "__main__":
    tft = League("Thejairex", "las")
    print(tft.puuid)
    # print(tft.matchs_test)
    dragon = Ddragon()
    # print(dragon.get_all_champ())
    # print(dragon.getChampByName("JHIN"))
    # print(dragon.getChampByKey(202))
