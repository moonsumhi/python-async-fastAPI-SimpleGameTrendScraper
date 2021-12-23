from odmantic import Model
from typing import List, Dict


class GameModel(Model):
    keywords: List
    keyword: List[Dict]
    name: str
    count: int
    entname: str
    givenrate: str

    class Config:
        collection = "games"
