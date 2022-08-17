from fastapi import FastAPI, Form
import uvicorn
from typing import Optional
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup

varzesh3 = FastAPI(title="varzesh3")

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'referer': 'https://www.varzesh3.com'}


@varzesh3.post('/league')
async def scrape_tags(input: HttpUrl = Form(..., description="<h4 style='text-align:right;'>آدرس سایت را وارد کنید</h4>")):
    r = requests.Session()
    page = r.get((input), headers=headers)  # proxies=proxies)
    soup = BeautifulSoup(page.content, 'lxml')
    table = soup.find("tbody")  # دریافت جدول از صفحه
    rank = []

    for ooo in table.find_all("tr"):

        result_rank = ooo.find("td").text.strip()
        result_nameleg = ooo.find("td", attrs={"scope": "row"}).text.strip()
        result_game = ooo.find_all("td")[2].text
        result_win = ooo.find_all("td")[3].text
        result_equal = ooo.find_all("td")[4].text
        result_lost = ooo.find_all("td")[5].text
        result_goal = ooo.find_all("td")[6].text
        result_difference = ooo.find_all("td")[7].text
        result_point = ooo.find_all("td")[8].text

        mamad_behineh = {"rank": result_rank,
                         "team": result_nameleg, "game": result_game, "win": result_win, "equal": result_equal, "lost": result_lost, "goal": result_goal, "difference": result_difference, "point": result_point}

        rank.append(mamad_behineh)

        if soup.find_all('h1'):
            h1 = soup.find_all('h1')[0].text.strip()
        else:
            h1 = ""

    return {
        "name_list": h1,
        "list": rank,
    }


@varzesh3.post('/team')
async def scrape_tags(input: HttpUrl = Form(..., description="<h4 style='text-align:right;'>آدرس سایت را وارد کنید</h4>")):
    r = requests.Session()
    page = r.get((input), headers=headers)  # proxies=proxies)
    soup = BeautifulSoup(page.content, 'lxml')

    # پیدا کردن لینک
    fixtureslink = soup.find("li", attrs={"name": "fixtures"}).get("data-api")  # برنامه‌ها
    resultslink = soup.find("li", attrs={"name": "results"}).get("data-api")  # نتایج
    try:
        playerslink = soup.find("li", attrs={"name": "players"}).get("data-api")  # بازیکنان
    except:
        pass # doing nothing on exception

    # درخواست به لینک api
    fixturesapi = r.request("GET", fixtureslink, headers=headers)
    resultsapi = r.request("GET", resultslink, headers=headers)
    try:
        playersapi = r.request("GET", playerslink, headers=headers)
    except:
        playersapi = None
        pass


    listfixtures = []
    listresults = []
    listplayers = []

    # برنامه‌ها
    def jsonfixtures(x):
        for data in x:
            listfixtures.append(data)

    while fixturesapi.json()["hasMore"] == True:
        listdata = fixturesapi.json()["items"]
        jsonfixtures(listdata)
        # لینک صفحه بعدی
        apifixtures = fixturesapi.json()["_links"][0]["href"]
        fixturesapi = r.request("GET", apifixtures, headers=headers)
    else:
        listdata = fixturesapi.json()["items"]
        jsonfixtures(listdata)

    # نتایج
    def jsonresults(x):
        for data in x:
            listresults.append(data)

    while resultsapi.json()["hasMore"] == True:
        listdata = resultsapi.json()["items"]
        jsonresults(listdata)
        # لینک صفحه بعدی
        apiresults = resultsapi.json()["_links"][0]["href"]
        resultsapi = r.request("GET", apiresults, headers=headers)
    else:
        listdata = resultsapi.json()["items"]
        jsonresults(listdata)

    # بازیکنان
    try:
        playersapi = playersapi.json()["items"]
        for sdsd in playersapi:
            listplayers.append(sdsd)
    except:
        pass

    if soup.find_all('h1'):
        h1 = soup.find_all('h1')[0].text.strip()
    else:
        h1 = ""


    table = soup.find("table" , attrs={"class":"topscorers"}).find("tbody")  # دریافت جدول از گلزنان برتر
    namelist = []
    for v in table.find_all("tr"):
        name = v.find_all("td")[0].text.strip()
        goal = v.find_all("td")[1].text.strip()
        mamad_behineh = {"name": name,"goal": goal}
        namelist.append(mamad_behineh)

    return {
        "name_list": h1,
        "fixtures": listfixtures,
        "results": listresults,
        "players": listplayers,
        "topscorers":namelist
    }
