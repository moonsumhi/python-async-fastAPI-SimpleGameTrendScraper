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
    async def check_mongodb(key: str, game_name: str, game_info: Dict, words_cnt: Dict):
        if await mongodb.engine.find_one(GameModel, GameModel.name == game_name):
            game_model = await mongodb.engine.find_one(
                GameModel, GameModel.name == game_name
            )
            game_model.count = game_model.count + words_cnt[game_name]
            await mongodb.engine.save(game_model)
        else:
            game_model = GameModel(
                keyword=key,
                name=game_info["gametitle"],
                count=words_cnt[game_name],
                entname=game_info["entname"],
                givenrate=game_info["givenrate"],
            )
            await mongodb.engine.save(game_model)
        return game_model

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

    async def update_db_cnt(self, key: str, games: List[Dict], threshold: int):
        words_cnt = self.counting_word_cnt(games, threshold)
        game_search = GameSearch()
        searched_game_list = await game_search.search(words_cnt.keys())

        results = await asyncio.gather(
            *[
                UpdateDB.check_mongodb(
                    key, game["gamename"], game["gameinfo"], words_cnt
                )
                for game in searched_game_list
            ]
        )

        sorted_results = sorted(results, key=lambda x: x.count)
        return sorted_results

    async def run(self, key: str, games: List[Dict], threshold: int):
        mongodb.connect()
        await self.update_db_cnt(key, games, threshold)
        mongodb.close()


if __name__ == "__main__":
    DATA_DIR = str(Path(__file__).resolve().parent) + "/test.json"
    with open(DATA_DIR) as f:
        data = json.loads(f.read())
        data = data["items"]
    temp = UpdateDB()
    asyncio.run(temp.run("신작게임", data, 2))
