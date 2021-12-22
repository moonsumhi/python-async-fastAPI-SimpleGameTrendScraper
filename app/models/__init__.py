from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from app.config import MONGO_DB_NAME, MONGO_URL


class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.engine = AIOEngine(motor_client=self.client, database=MONGO_DB_NAME)

        print("DB와 성공적으로 연결됐습니다.")

    async def close(self):
        self.client.close()


mongodb = MongoDB()
