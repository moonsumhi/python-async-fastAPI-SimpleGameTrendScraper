import aiohttp
import asyncio
from app.config import NAVER_API_ID, NAVER_API_SECRET


class NaverScraper:
    """
    네이버 오픈 API를 이용한 데이터 수집
    """

    NAVER_API_CAFE = "https://openapi.naver.com/v1/search/cafearticle.json"

    @staticmethod
    async def fetch(session, url, headers):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result["items"]

    def unit_api(self, keyword, start):
        return {
            "url": f"{self.NAVER_API_CAFE}?query={keyword}&display=10&start={start}",
            "headers": {
                "X-Naver-Client-Id": NAVER_API_ID,
                "X-Naver-Client-Secret": NAVER_API_SECRET,
            },
        }

    async def search(self, keyword, total_page):
        apis = [self.unit_api(keyword, 1 + i * 10) for i in range(total_page)]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[
                    NaverScraper.fetch(session, api["url"], api["headers"])
                    for api in apis
                ]
            )
            result = []
            for data in all_data:
                if data is not None:
                    for game in data:
                        result.append(game)
            return result

    def run(self, keyword, total_page):
        return asyncio.run(self.search(keyword, total_page))


if __name__ == "__main__":
    scraper = NaverScraper()
    results = scraper.run("신작게임", 10)
    print(results)
    print(len(results))
