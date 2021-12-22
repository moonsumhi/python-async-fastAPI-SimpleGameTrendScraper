from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.naver_scraper import NaverScraper
from app.kakao_scraper import KakaoScraper
from app.config import BASE_DIR
from app.models import mongodb
from app.counting import UpdateDB


app = FastAPI(title="데이터 수집가")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {"request": request, "title": "데이터 수집가"}
    return templates.TemplateResponse("index.html", context=context)


@app.get("/search", response_class=HTMLResponse)
async def search_result(request: Request):
    keyword = request.query_params.get("q")

    if not keyword:
        context = {"request": request}
        return templates.TemplateResponse("index.html", context=context)

    naver_scraper = NaverScraper()
    kakao_scraper = KakaoScraper()

    naver_data = await naver_scraper.search(keyword, 10)
    kakao_data = await kakao_scraper.search(keyword, 10)

    updatedb = UpdateDB()
    games = await updatedb.update_db_cnt(keyword, naver_data + kakao_data, 2)
    games = games[:20]
    context = {"request": request, "keyword": keyword, "games": games}
    return templates.TemplateResponse("index.html", context=context)


@app.on_event("startup")
async def on_app_start():
    await mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    await mongodb.close()
