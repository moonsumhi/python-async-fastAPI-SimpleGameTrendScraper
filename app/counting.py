from typing import List, Dict
from collections import Counter
from app.models.game import GameModel
from app.models import mongodb
import re
from app.game_search import GameSearch

from pathlib import Path
import json
import asyncio


class UpdateDB:
    @staticmethod
    async def add_mongodb(key: str, game_name: str, game_info: Dict, words_cnt: Dict):
        if await mongodb.engine.find_one(
            GameModel, GameModel.name == game_info["gametitle"]
        ):
            game_model = await mongodb.engine.find_one(
                GameModel, GameModel.name == game_info["gametitle"]
            )
            # 찾은 game_model의 키워드로 검색했던 이력이 있다면 더해주지 않고 리턴한다.
            if key not in game_model.keywords:
                game_model.keywords = game_model.keywords + [key]
                game_model.keyword.append({"key": key, "cnt": words_cnt[game_name]})
                game_model.count = game_model.count + words_cnt[game_name]
                await mongodb.engine.save(game_model)
        else:
            game_model = GameModel(
                keywords=[key],
                keyword=[{"key": key, "cnt": words_cnt[game_name]}],
                name=game_info["gametitle"],
                count=words_cnt[game_name],
                entname=game_info["entname"],
                givenrate=game_info["givenrate"],
            )
            await mongodb.engine.save(game_model)
        return game_model

    @staticmethod
    async def delete_mongodb(key: str, game_model):
        # keywords update
        game_model.keywords.remove(key)
        # keyword update
        cnt = 0
        candi = game_model.keyword
        for kw in candi:
            if kw["key"] == key:
                cnt = kw["cnt"]
                game_model.keyword.remove(kw)
                break
        # count update
        game_model.count -= cnt

        if game_model.count > 0:
            await mongodb.engine.save(game_model)
        else:
            await mongodb.engine.delete(game_model)

    async def update_delete_mongodb(self, key: str):
        games = await mongodb.engine.find(GameModel, GameModel.keywords.in_([key]))
        await asyncio.gather(*[UpdateDB.delete_mongodb(key, game) for game in games])
        results = await mongodb.engine.find(GameModel)
        sorted_results = sorted(results, key=lambda x: -x.count)

        return sorted_results

    def counting_word_cnt(self, games: List[Dict], threshold: int):
        words = []
        for game in games:
            title = game["title"]
            title = re.sub("<[^>]+>", "", title)
            title = re.sub("[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`'…》\”\“\’·]", "", title)
            word_list = title.split()
            for word in word_list:
                word = word.strip()
                words.append(word)
        words_cnt = Counter(words)
        words_cnt = {x: count for x, count in words_cnt.items() if count >= threshold}
        sorted_words_cnt = dict(sorted(words_cnt.items(), key=lambda x: -x[1]))
        print(sorted_words_cnt)

        return sorted_words_cnt

    async def update_add_db_cnt(self, key: str, games: List[Dict], threshold: int):
        words_cnt = self.counting_word_cnt(games, threshold)
        game_search = GameSearch()
        searched_game_list = await game_search.search(words_cnt.keys())

        await asyncio.gather(
            *[
                UpdateDB.add_mongodb(key, game["gamename"], game["gameinfo"], words_cnt)
                for game in searched_game_list
            ]
        )

        results = await mongodb.engine.find(GameModel)

        sorted_results = sorted(results, key=lambda x: -x.count)
        return sorted_results

    async def run(self, key: str, games: List[Dict], threshold: int):
        await mongodb.connect()
        # await self.update_add_db_cnt(key, games, threshold)
        await self.update_delete_mongodb(key)
        await mongodb.close()


if __name__ == "__main__":
    DATA_DIR = str(Path(__file__).resolve().parent) + "/test.json"
    with open(DATA_DIR) as f:
        data = json.loads(f.read())
        data = data["items"]
    temp = UpdateDB()
    asyncio.run(temp.run("신작게임", data, 2))
