from odmantic import Model


class GameModel(Model):
    keyword: str
    name: str
    count: int
    entname: str
    givenrate: str

    class Config:
        collection = "games"
