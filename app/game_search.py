import aiohttp
import xmltodict
import json
import asyncio


class GameSearch:
    GAMESEARCH_URL = "http://www.grac.or.kr/WebService/GameSearchSvc.asmx/game"

    @staticmethod
    async def fetch(session, url, game_name):
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.text()
                result = xmltodict.parse(result)
                result = json.dumps(result["result"])
                result = json.loads(result)

                try:
                    item = result["item"]
                    gametitle_list = item["gametitle"].split()
                    if game_name in gametitle_list:
                        return {"gamename": game_name, "gameinfo": item}
                    else:
                        return None
                except KeyError:
                    return None

    def unit_api(self, game_name):
        return {
            "url": f"{self.GAMESEARCH_URL}?gametitle={game_name}&entname=&rateno=&display=1&pageno=1",
            "game_name": game_name,
        }

    async def search(self, game_names):
        apis = [self.unit_api(game_name) for game_name in game_names]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[
                    GameSearch.fetch(session, api["url"], api["game_name"])
                    for api in apis
                ]
            )
            result = []
            for data in all_data:
                if data is not None:
                    result.append(data)

            return result

    def run(self, game_names):
        return asyncio.run(self.search(game_names))


if __name__ == "__main__":
    data = {
        "스타크래프트": 27,
        "게임": 19,
        "신작게임": 14,
        "12월": 4,
        "게임을": 3,
        "펄어비스": 3,
        "더": 2,
        "닌텐도": 2,
        "나오는": 2,
        "시프트업": 2,
        "코지마": 2,
        "후기": 2,
        "플레이": 2,
        "출시": 2,
        "게임들": 2,
        "액션": 2,
        "2021년": 2,
        "좋고": 2,
    }
    a = GameSearch()
    print(a.run(data.keys()))
