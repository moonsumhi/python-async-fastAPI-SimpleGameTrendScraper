import aiohttp
import asyncio
from app.config import KAKAO_API_AK


class KakaoScraper:
    """
    카카오 오픈 API를 이용한 데이터 수집
    """

    KAKAO_API_CAFE = "https://dapi.kakao.com/v2/search/cafe"
    KAKAO_API_AK = "KakaoAK " + KAKAO_API_AK

    @staticmethod
    async def fetch(session, url, headers):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result["documents"]

    def unit_api(self, keyword, start):
        return {
            "url": f"{self.KAKAO_API_CAFE}?query={keyword}&size=10&page={start}",
            "headers": {"Authorization": KAKAO_API_AK},
        }

    async def search(self, keyword, total_page):
        apis = [self.unit_api(keyword, i) for i in range(1, total_page + 1)]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[
                    KakaoScraper.fetch(session, api["url"], api["headers"])
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
    scraper = KakaoScraper()
    results = scraper.run("신작게임", 10)
    print(results)
    print(len(results))
