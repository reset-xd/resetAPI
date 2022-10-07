"""
If you plan on using the /user endpoint then you need to have "discord_token"
as environment variable.
"""
from dotenv import load_dotenv

load_dotenv(".env")

from os import getenv
token = getenv("discord_token")

# region [imports]
import anyio
import datetime
import json as jsonlib
import random
from akinator import Akinator
import aiohttp
from tetris.impl import custom
from tetris.impl import scorer
import tetris
from core.base_models import *
from core.game_functions import *
from core.image_gen import *
import uuid
import aiohttp
import fastapi
import secrets
import xmltodict
from aioify import aioify
from bson.objectid import ObjectId
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from extras import (art_of_war, edn, emojify_string, morse_decode,
                    morse_encode, text_to_owo, user_info, premium_user_checker)

# mysql connection

limiter = Limiter(key_func=get_remote_address)
app = fastapi.FastAPI(redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# endregion

# region [html templates]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("100/minute")
async def homepage(request: fastapi.Request):
    resp = edn(app)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "endpoints": resp
    })


class Parser:
    thumbnail:str
    title:str
    views:str
    link:str
    date:str
    viewcount:str

    description:str
    sub:str
    joined:str
    totalviews:str
    channelicon:str
    channelbanner:str
    name:str

    def __init__(self, data, channeldata):
        try:
            self.thumbnail = data.split('{"thumbnails":[{"url":"')[1].split("?")[0]
        except:
            self.thumbnail = "none"
        
        try:
            self.title = data.split('"title":{"runs":[{"text":"')[1].split('"}]')[0]
        except:
            self.title = "none"
        
        try:
            self.views = data.split('"viewCountText":{"simpleText":"')[1].split('"},"')[0]
        except:
            self.views = "none"
        
        try:
            self.link = "https://www.youtube.com/watch?v=" + self.thumbnail.split("/")[-2]
        except:
            self.link = "none"
         
        try:
            self.date = data.split('"publishedTimeText":{"simpleText":"')[1].split('"},')[0]
        except:
            self.date = "none"
        
        try:
            self.viewcount = data.split('"viewCountText":{"simpleText":"')[1].split('"},')[0]
        except:
            self.viewcount = "none"
        

        try:
            self.description = channeldata.split('{"description":{"simpleText":"')[1].split('"},')[0]
        except:
            self.description = "none"
        
        try:
            self.joined = channeldata.split('"joinedDateText":{"runs":[{"text":"Joined "},{"text":"')[1].split('"}]')[0]
        except:
            self.joined = "none"
        
        try:
            self.totalviews = channeldata.split(',"viewCountText":{"simpleText":"')[1].split('"},')[0]
        except:
            self.totalviews = "none"
        
        try:
            self.channelicon = channeldata.split('"height":88},{"url":"')[1].split('"')[0]
        except:
            self.channelicon = "none"
        
        try:
            self.name = channeldata.split('{"channelMetadataRenderer":{"title":"')[1].split('","')[0]
        except:
            self.name = "none"
        
        try:
            self.sub = channeldata.split('"subscriberCountText":{"accessibility":{"accessibilityData":{"label":"')[1].split('"}},')[0]
        except:
            self.sub = "none"
        
        try:
            self.channelbanner = channeldata.split('"tvBanner":{"thumbnails":[{"url":"')[1].split('"')[0]
        except:
            self.channelbanner = "none"
        
@app.get("/youtube", tags=["json endpoints"], summary="youtube infos")
async def latest_video_yt(
        channel_link="https://www.youtube.com/c/DailyDoseOfInternet"):
    """
    [GET] 
    get the latest youtube video information

    # parameters
    channel_link: link to channel (eg. https://www.youtube.com/c/DailyDoseOfInternet)

    # returns
    ```json
    {
      "thumbnail": "https://i.ytimg.com/vi/sIzBhYBsTdA/hqdefault.jpg",
      "title": "Horse Doesn't Realize It Was Just Born",
      "link": "https://www.youtube.com/watch?v=sIzBhYBsTdA",
      "date": "16 hours ago"
    }
    ```
    """

    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
    async with aiohttp.ClientSession(
            headers={"User-Agent": useragent}) as session:
        async with session.get(channel_link + "/videos") as resp:
            data1 = await resp.text()

        async with session.get(channel_link + "/about") as resp:
            data2 = await resp.text()

    a = Parser(data1, data2)
    return {
        "channelbanner":
        a.channelbanner.replace("w320",
                                "w1280").replace("00000000ffffffff",
                                                 "32b75a57cd48a5a8"),
        "channelicon":
        a.channelicon,
        "channelname":
        a.name,
        "joined":
        a.joined,
        "totalsubs":
        a.sub,
        "thumbnail":
        a.thumbnail,
        "title":
        a.title,
        "link":
        a.link,
        "date":
        a.date,
        "viewcount":
        a.viewcount,
        "description":
        a.description
    }


@app.get("/support", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("100/minute")
def homepage(request: fastapi.Request):
    return RedirectResponse("https://www.buymeacoffee.com/resetxd")


# endregion


# region [game endpoints][tetris]


tetris_current_playing = {}

@app.post("/game/tetris/create",tags=["games endpoints"],summary="create tetris game")
async def tetris_create_game(request: fastapi.Request):
    """
    [POST] method

    create a new tetris game

    endpoint - /game/tetris/create

    # returns
    ```json
    {
        "game_id": game-token,
        board: "ready to use board",
        "next": "next piece"
    }
    ```
    """
    game_id = str(uuid.uuid4())
    global tetris_current_playing
    game = tetris.BaseGame(custom.CustomEngine,board_size=(15,10), scorer=scorer.GuidelineScorer)
    game.engine.parts["gravity"] = PerMoveGravity
    game.reset()
    tetris_current_playing[str(game_id)] = {"game":game}
    return {"game_id":str(game_id), "board":tetris_render_board(game), "next": tetris_next_piece(game)}

@app.post("/game/tetris/action",tags=["games endpoints"],summary="tetris game actions")
async def tetris_action(request: fastapi.Request, action:tetris_action):
    """
    [POST] method

    perform an action on a tetris game

    endpoint - /game/tetris/action

    # parameters
    - **game_id** - game token
    - **action** - action to perform (left, right, rotate, soft_drop, hard_drop, swap, hold)

    # returns
    ```json
    {
        "win": true or false if the game still playing,
        "board":"updated board",
        "next":"next piece"
    }
    ```
    """
    global tetris_current_playing
    if action.action == "left":
        tetris_current_playing[action.game_id]["game"].left()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing) ,"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "right":
        tetris_current_playing[action.game_id]["game"].right()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "rotate":
        tetris_current_playing[action.game_id]["game"].rotate()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "soft_drop":
        tetris_current_playing[action.game_id]["game"].soft_drop()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "hard_drop":
        tetris_current_playing[action.game_id]["game"].hard_drop()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "swap":
        tetris_current_playing[action.game_id]["game"].swap()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}
    elif action.action == "hold":
        tetris_current_playing[action.game_id]["game"].swap()
        tetris_current_playing[action.game_id]["game"].tick()
        return {"win":str(tetris_current_playing[action.game_id]["game"].playing),"board":tetris_render_board(tetris_current_playing[action.game_id]["game"]),"score":tetris_current_playing[action.game_id]["game"].score, "next": tetris_next_piece(tetris_current_playing[action.game_id]["game"])}

# endregion

# region [UnixTime]

@app.get("/unixtime/fromunix",tags=["unixtime"],summary="unixtime")
async def unixtime(timestamp):
    """
    convert epos to simple string<br>/unixtime/fromunix?timestamp=1549892280<br>
    get unixtime

    endpoint - /unixtime/fromunix

    # parameters
    - **timestamp**: timestamp (1549892280)

    # returns
    ```json
    {
        "Datetime": "2019-02-11 13:38:00"
    }
    ```
    """
    return {"Datetime": datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')}

@app.get("/unixtime/tounix",tags=["unixtime"],summary="unixtime")
async def unixtime(date):
    """
    convert epos to simple string<br>/unixtime/tounix?date=2019%2F02%2F11+13%3A38%3A00<br>
    get unixtime

    endpoint - /unixtime/tounix

    # parameters
    - **date**: date (2019/02/11 13:38:01)(2019-02-11 13:38:01)

    # returns
    ```json
    {
        "UnixTimeStamp": "1549892280"
    }
    ```
    """
    if date == "now":
        return {"UnixTimeStamp": int(datetime.datetime.now().timestamp())}
    date = date.replace("-","/")
    data = {"Datetime": str(int(datetime.datetime.strptime(date, '%Y/%m/%d %H:%M:%S').timestamp()))}
    return data


# endregion 

# region [internal endpoints]


def get_redoc_html(
    *,
    openapi_url: str,
    title: str,
    redoc_js_url:
    str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    redoc_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    with_google_fonts: bool = True,
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """
    if with_google_fonts:
        html += """
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    """
    html += f"""
    <link rel="shortcut icon" href="{redoc_favicon_url}">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    </head>
    <body>
    <redoc spec-url="{openapi_url}"></redoc>
    <script src="{redoc_js_url}"> </script>
    <script data-name="BMC-Widget" data-cfasync="false"         src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="resetxd" data-description="Support me on Buy me a coffee!" data-message="" data-color="#FFDD00" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
    </body>
    </html>
    """

    return HTMLResponse(html)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url=app.openapi_url,
                          title="resapi docs",
                          redoc_favicon_url="/static/avatar1.png")


@app.get("/internal/endpoints", include_in_schema=False)
@limiter.limit("5/minute")
async def end(request: fastapi.Request):
    async with aiohttp.ClientSession() as client:
        response = await client.get(f"{request.url._url[:22]}openapi.json")
        json = await response.json()
        json = json["paths"]
    ret = ""
    for x in json:
        try:
            resp = json[x]["get"]["description"].split("<br>")
            ret += f"""
            <div class="col-md-6" style="margin-bottom: 8px;">
                <div class="card" style="background: rgba(255,255,255,0);border-radius: 22px;margin-top: 0px;border: 3px solid #8a00ff;box-shadow: 5px 5px 20px #8a00ff, -5px -5px 20px #8a00ff;">
                    <div class="card-body">
                        <h4 class="card-title" style="color: #8a00ff;">{x[1:]}</h4>
                        <p class="card-text" style="font-size: 23px;color: #bf00ff;">{resp[0]}</p><a class="card-link" href="{resp[1]}" style="color: #df00ff;">test endpoint</a>
                    </div>
                </div>
            </div>

            """
        except:
            pass
    return ret


@app.get("/asset/{file_path}", include_in_schema=False)
async def asset(requests: fastapi.Request, file_path: str):
    return FileResponse(f"./asset/{file_path}")


# endregion

# region [json endpoints]


@app.get("/art-of-war", tags=["json endpoints"], summary="art of war")
@limiter.limit("100/minute")
def artOfWar(request: fastapi.Request):
    """
    sun tzu the art of war book related quotes<br>/art-of-war<br>

    """
    return {"quote": random.choice(art_of_war)}


@app.get("/art-of-war.json", include_in_schema=False)
@limiter.limit("100/minute")
def artOfWarJson(request: fastapi.Request):
    return {"quote": art_of_war}


@app.get("/emojify", tags=["json endpoints"], summary="emojify")
@limiter.limit("100/minute")
def emojify(request: fastapi.Request, text: str):
    """
    emojify a string<br>/emojify?text=omg+reset+is+the+best<br>

    creates a discord friendly string

    # parameters
    - **text**: text to emojify

    # return
    ```json
    {
        "emojified": "text"
    }
    ```
    """
    return {"emojified": emojify_string(text)}


@app.get("/news", tags=["json endpoints"], summary="myanimelist news")
@limiter.limit("100/minute")
async def news(request: fastapi.Request):
    """
    gives anime news in json format<br>/news<br>

    # return
    ```json
        [
            {"guid":"", "title":"", "description":"", "media:thumbnail":"", "pubDate":"", "link":""},
            {...},
            {...}
        ]
    ```
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://myanimelist.net/rss/news.xml") as repo:
            resultJson = await repo.text()
            returnJson = jsonlib.dumps(xmltodict.parse(resultJson))
    return jsonlib.loads(returnJson)["rss"]["channel"]["item"]


@app.get("/user", tags=["json endpoints"], summary="user info")
@limiter.limit("100/minute")
async def user(request: fastapi.Request, userid: str):
    """
    user info<br>/user?userid=424133185123647488<br>

    # parameters
    - **userid**: discord user ID (not user name)

    # return
    ```json
    {
        "name":"reset",
        "avatar":"https://cdn.discordapp.com/avatars/424133185123647488/26fc2ba791f1fcd2f678d5761e2cdab2.png?size=1024",
        "banner":null,
        "discriminator":"8278",
        "id":"424133185123647488",
        "banner_color":"#18191c",
        "accent-color":1579292
    }
    ```
    """
    ret = await user_info(token, userid)
    return ret


@app.get("/avatar/{user_id}.png", tags=["image endpoints"], summary="user avatar", response_class=RedirectResponse)
@limiter.limit("100/minute")
async def user(request: fastapi.Request, user_id: str):
    """
    user avatar url<br>/avatar/424133185123647488.png<br>


    # return

    Image

    """
    ret = await user_info(token, user_id)
    return RedirectResponse(ret["avatar"])


@app.get("/strings", tags=["json endpoints"], summary="encoding info")
@limiter.limit("100/minute")
async def strings(request: fastapi.Request,
                  text: str,
                  from_: str = None,
                  to: str = None):
    """
    strings info<br>/strings?text=reset+api+is+the+best&from_=text&to=owo<br>

    # parameters
    - **text**: text to encode
    - **from_**: can be **text** or **morse**
    - **to**: can be **text** or **owo** or **morse**

    # return
    ```json
    {
        "text": "weset api is teh best"
    }
    ```
    """
    if from_ == "text" and to == "owo":
        return {"text": text_to_owo(text)}
    elif from_ == "text" and to == "morse":
        return {"text": morse_encode(text)}
    elif from_ == "morse" and to == "text":
        return {"text": morse_decode(text)}
    else:
        return {"text": text}


# endregion

# region [games endpoint]

# region [game endpoint][connect4]

current_playing = {}


@app.post("/game/connect-4/create",
          tags=["games endpoints"],
          summary="create c4 game")
async def create_game(request: fastapi.Request, game: c4_creator):
    """
    [POST] method

    create a new connect 4 game

    endpoint - /game/connect-4/create

    # returns
    ```json
    {
        "game_id": game-token
    }
    ```
    """
    game_id = uuid.uuid4()
    global current_playing
    current_playing[str(game_id)] = {
        "board": create_board(),
        "player1": game.player1,
        "player2": game.player2,
        "empty": game.empty
    }
    return {"game_id": str(game_id)}


@app.get("/game/connect-4/get-all-games", include_in_schema=False)
async def allGames():
    return {"data": current_playing}


@app.post("/game/connect-4/get-board",
          tags=["games endpoints"],
          summary="get c4 board")
async def get_board(request: fastapi.Request, game_id: c4_get_board):
    """
    [POST] method

    returns the current game board

    endpoint - /game/connect-4/get-board

    # parameters
    - **game_id** - game token


    # returns
    ```json
    {
        "board": "ready to use board"
    }
    ```
    """

    try:
        global current_board
        return {
            "board":
            current_board(current_playing[game_id.game_id]["board"],
                          current_playing[game_id.game_id]["player1"],
                          current_playing[game_id.game_id]["player2"],
                          current_playing[game_id.game_id]["empty"])
        }
    except:
        return {"eror": "game not found"}


@app.post("/game/connect-4/drop",
          tags=["games endpoints"],
          summary="c4 game drop")
async def droper(request: fastapi.Request, drop: c4_drop):
    """
    [POST] method

    drop a piece at a given column

    endpoint - /game/connect-4/drop

    # parameters
    - **game_id** - game token
    - **column** - column to drop piece at
    - **player** - player to drop piece as (1 or 2 only)

    # returns
    ```json
    {
        "winner":"if game is over",
        "board":"updated board"
    }
    ```
    """

    global current_playing
    board = current_playing[drop.game_id]["board"]
    col = int(drop.column)
    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(current_playing[drop.game_id]["board"], row, col,
                   int(drop.player))
    if winning_move(board, int(drop.player)):
        return {
            "winner":
            drop.player,
            "board":
            current_board(current_playing[drop.game_id]["board"],
                          current_playing[drop.game_id]["player1"],
                          current_playing[drop.game_id]["player2"],
                          current_playing[drop.game_id]["empty"])
        }
    else:
        return {
            "winner":
            "none",
            "board":
            current_board(current_playing[drop.game_id]["board"],
                          current_playing[drop.game_id]["player1"],
                          current_playing[drop.game_id]["player2"],
                          current_playing[drop.game_id]["empty"])
        }


# endregion

# endregion

# region [games endpoints][akinator]

akinator_currently_playing = {}


@app.post("/game/akinator/create",
          tags=["games endpoints"],
          summary="create akinator game")
async def akinator_create_game(request: fastapi.Request, le: AkinatorCreate):
    """
    [POST] method.
    
    create your akinator game.

    # parameter
    - **language** - language of the game (en,en_animals,en_objects,ar,cn,de,de_animals,fr,jp,etc)

    # return
    ```json
    {
        "game_id": game-token,
        "question": "question asked by akinator",
        "confidence": "confidence level of akinator"
    }
    ```
    """
    game_id = str(uuid.uuid4())
    global akinator_currently_playing
    akii = create_aki(le.language)
    akinator_currently_playing[str(game_id)] = {"game": akii}
    return {
        "game_id": str(game_id),
        "question": akii.question,
        "confidence": akii.progression
    }


@app.post("/game/akinator/close",
          tags=["games endpoints"],
          summary="akinator close")
async def akinator_game_close(request: fastapi.Request,
                              gam: AkinatorGameClose):
    """
    [POST] method.
    
    Close your game after completion.    

    # parameter
    - **game_id** - game token

    # return
    ```json
    {
        "message": "thank you for playing!"
    }
    ```
    """
    akii: Akinator = akinator_currently_playing[gam.game_id]["game"]
    akii.close()
    return {"message": "thanks for playing!"}


@app.post("/game/akinator/action",
          tags=["games endpoints"],
          summary="akinator action")
async def akinator_game_action(request: fastapi.Request,
                               gam: AkinatorGameAction):
    """
    [POST] method.
    
    interact with your akinator game.

    # parameter
    - **game_id** - game token
    - **action** - action to do (**y**[yes], **n**[no] ,**idk**[i dont know],**p** [probably],**pn** [probably not])

    # return
    ```json
    {
        "question": "question",
        "step": "question number",
        "confidence":"percentage of game completion",
        "image": "if game complete",
        "description": "if game complete",
        "name": "if game complete",
        "pseudo": "if game complete",
        "ranking": "if game complete"
    }
    ```
    """
    if gam.action not in ["y", "n", "idk", "p", "pn"]:
        return {"message": "wrong input"}
    akii: akinator.Akinator = akinator_currently_playing[gam.game_id]["game"]
    q = akii.answer(gam.action)
    data = {"question": q, "step": akii.step, "confidence": akii.progression}
    if akii.progression >= 80:
        akii.win()
        data["image"] = akii.first_guess["absolute_picture_path"]
        data["description"] = akii.first_guess["description"]
        data["name"] = akii.first_guess["name"]
        data["pseudo"] = akii.first_guess["pseudo"]
        data["ranking"] = akii.first_guess["ranking"]
    return data


# endregion

# region [image endpoints]


@app.get("/welcome",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="welcome card")
@limiter.limit("100/minute")
async def welcome_endpoint(request: fastapi.Request,
                           background,
                           message,
                           text,
                           avatar=None,
                           username=None,
                           userid=None):
    """
    welcome card<br>/welcome?background=https://cdn.discordapp.com/attachments/907213435358547968/974989177642950656/unknown.png&avatar=https://cdn.discordapp.com/attachments/907213435358547968/974989329858461766/unknown.png&message=welcome%20to%20my%20server&username=komi%20san&text=1000%20members%20now%20OWO<br>

    endpoint - /welcome

    # parameters
    - **background** - background image url
    - **avatar** - avatar image url
    - **message** - message to display
    - **text** - message to display in 3rd line
    - **username** - username to display
    - **userid** - userid to display (optional, use this and dont give username and avatar)

    # returns
    <img src="/asset/welcome.bmp">

    """
    if userid:
        info = await user_info(token, userid)
        avatar = info["avatar"]
        username = info["name"]

    a = await anyio.to_thread.run_sync(
        welcomer, {
            "background": background,
            "avatar": avatar,
            'username': username,
            'message': message,
            'text': text
        })
    return FileResponse(f"./trash/{a}.png")


@app.get("/level",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="level card")
@limiter.limit("100/minute")
async def level_endpoint(request: fastapi.Request,
                         background,
                         level: int,
                         current_exp: int,
                         max_exp: int,
                         avatar=None,
                         username=None,
                         userid=None,
                         bar_color="red",
                         text_color="white"):
    """
    level card<br>/level?background=https://media.discordapp.net/attachments/992703788865572874/993888491756859423/20220705_223748.jpg&avatar=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png&username=Reset&discriminator=1000&current_exp=276&max_exp=454&level=8&bar_color=%23FFA0D0&text_color=%23c2648d<br>    
 
    endpoint - /level

    # parameters
    - **background** - background image url
    - **avatar** - avatar image url
    - **username** - username to display
    - **current_exp** - current exp
    - **max_exp** - max exp
    - **level** - level
    - **bar_color** - bar color (color name or hex)
    - **text_color** - text color (color name or hex)

    # returns
    <img src="https://cdn.discordapp.com/attachments/907213435358547968/994620579816681572/unknown.png">

    """

    if userid:
        info = await user_info(token, userid)
        avatar = info["avatar"]
        username = info["name"]
    a = await anyio.to_thread.run_sync(
        level_maker, {
            'background': background,
            'level': level,
            'avatar': avatar,
            'username': username,
            'current_exp': current_exp,
            'max_exp': max_exp,
            'bar_color': bar_color,
            'text_color': text_color
        })
    return FileResponse(f"./trash/{a}.png")


@app.get("/rip",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="rip my g")
@limiter.limit("100/minute")
async def rip_endpoint(request: fastapi.Request, avatar):
    """
    rip avatar<br>/rip?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974990788972916766/unknown.png<br>

    endpoint - /rip

    # parameters
    - **avatar** - avatar image url


    # returns
    <img src="/asset/rip.bmp">

    """

    a = await anyio.to_thread.run_sync(rip_maker, avatar)
    return FileResponse(f"./trash/{a}.png")


@app.get("/wap",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="spongebob pray")
@limiter.limit("100/minute")
async def wap_endpoint(request: fastapi.Request, avatar):
    """
    spongebob pray<br>/wap?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974989177642950656/unknown.png<br>

    endpoint - /wap

    # parameters
    - **avatar** - avatar image url


    # returns
    <img src="/asset/wap.bmp">

    """

    a = await anyio.to_thread.run_sync(spongebobWAP, avatar)
    return FileResponse(f"./trash/{a}.png")


@app.get("/throwthechild",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="throw child")
@limiter.limit("100/minute")
async def throwchild_endpoint(request: fastapi.Request, avatar):
    """
    THROW THE CHILD!<br>/throwthechild?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974990788972916766/unknown.png<br>

    endpoint - /throwthechild

    # parameters
    - **avatar** - avatar image url

    # returns
    <img src="/asset/throw.bmp">
    """
    a = await anyio.to_thread.run_sync(throwthechild, avatar)
    return FileResponse(f"./trash/{a}.png")


burn = aioify(obj=burning)


@app.get("/burn",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="burn avatar")
@limiter.limit("100/minute")
async def burnchild(request: fastapi.Request, avatar):
    """
    BURN THE CHILD!<br>/burn?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974990788972916766/unknown.png<br>

    endpoint - /burn

    # parameters
    - **avatar** - avatar image url

    # returns
    <img src="/asset/burn.bmp">

    """

    a = await anyio.to_thread.run_sync(burning, avatar)
    return FileResponse(f"./trash/{a}.png")


@app.get("/tear",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="spongebob tear")
@limiter.limit("100/minute")
async def spongebobtear_endpoint(request: fastapi.Request, avatar1, avatar2):
    """
    tear of happiness<br>/tear?avatar1=https://cdn.discordapp.com/attachments/907213435358547968/974990788972916766/unknown.png&avatar2=https://cdn.discordapp.com/attachments/907213435358547968/974989329858461766/unknown.png<br>

    endpoint - /tear

    # parameters
    - **avatar1** - avatar image url
    - **avatar2** - avatar image url

    # returns
    <img src="/asset/tear.bmp">
    """
    a = await anyio.to_thread.run_sync(tear, {
        "avatar1": avatar1,
        "avatar2": avatar2
    })
    return FileResponse(f"./trash/{a}.png")


@app.get("/discordsays",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="discordsays")
@limiter.limit("100/minute")
async def discorsays_endpoint(request: fastapi.Request,
                              message,
                              userid=None,
                              avatar=None,
                              username=None,
                              hex=None,
                              color="#ededed",
                              time="Today at 03:00 AM"):
    """
    make fake discord messages<br>/discordsays?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974989329858461766/unknown.png&username=komi+san&message=i+like+tadano+san&time=Today+at+2%3A22+AM<br>

    endpoint - /discordsays

    # parameters
    - **avatar** - avatar image url
    - **username** - username
    - **message** - message
    - **time** - time (default: Today at 03:00 AM)
    - **hex** - hex color (default: #ededed)
    - **color** - color (default: #ededed)
    - **userid** - userid (optional)
    

    # returns
    <img src="/asset/discordsays.bmp">

    """
    if hex is not None:
        hex = "#" + hex
    if userid is not None:
        info = await user_info(token, userid)
        avatar = info["avatar"]
        username = info["name"]
    a = await anyio.to_thread.run_sync(
        discordsays, {
            'avatar': avatar,
            'username': username,
            'message': message,
            'color': (hex or color),
            'time': time
        })
    return FileResponse(f"./trash/{a}.png")


@app.get("/love-me",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="love calc")
@limiter.limit("100/minute")
async def lovemeeee_endpoint(request: fastapi.Request,
                             avatar1: str,
                             avatar2: str,
                             percentage: int = None):
    """
    random love calculator<br>/love-me?avatar1=https://cdn.discordapp.com/attachments/907213435358547968/974989329858461766/unknown.png&avatar2=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<br>

    endpoint - /love-me

    # parameters
    - **avatar1** - avatar image url
    - **avatar2** - avatar image url
    - **percentage** - fixed percentage
    

    # returns
    <img src="/asset/loveme.png">

    """
    a = await anyio.to_thread.run_sync(lover_me, {
        "avatar1": avatar1,
        "avatar2": avatar2,
        "percentage": percentage
    })
    return FileResponse(f"./trash/{a}.png")


@app.get("/coat",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="wear a coat")
@limiter.limit("100/minute")
async def coatcoat_endpoint(request: fastapi.Request, avatar: str):
    """
    make your avatar wear a cozy coat<br>/coat?avatar=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<br>

    endpoint - /coat

    # parameters
    - **avatar** - avatar image url
    

    # returns
    <img src="/asset/coatfinal.png">

    """
    a = await anyio.to_thread.run_sync(coat_maker, avatar)
    return FileResponse(f"./trash/{a}.png")


@app.get("/uwu",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="uwu")
@limiter.limit("100/minute")
async def uwu_avatar_endpoint(request: fastapi.Request, avatar: str):
    """
    uwu your avatar<br>/uwu?avatar=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<br>

    endpoint - /uwu

    # parameters
    - **avatar** - avatar image url
    
    # returns
    <img src="/asset/uwufinal.png">

    """
    a = await anyio.to_thread.run_sync(uwu_maker, avatar)
    return FileResponse(f"./trash/{a}.png")


@app.get("/leaderboard",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="leaderboard card")
@limiter.limit("100/minute")
async def leaderboard_endpoint(request: fastapi.Request,
                               background: str,
                               serverlogo: str,
                               pos1: str = None,
                               pos2: str = None,
                               pos3: str = None,
                               pos4: str = None,
                               pos5: str = None,
                               pos6: str = None,
                               pos7: str = None,
                               pos8: str = None,
                               pos9: str = None,
                               pos10: str = None):
    """
    leaderboard card for your leveling system<br>/leaderboard?background=https://cdn.discordapp.com/attachments/907213435358547968/994600232161656892/unknown.png&serverlogo=https://cdn.discordapp.com/attachments/907213435358547968/994595322917556344/unknown.png&pos1=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos2=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos3=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos4=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos5=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos6=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000&pos7=https://cdn.discordapp.com/attachments/907213435358547968/992384949401432094/fddf655fb40613d2.png<sep>resetxd<sep>level+1+%7C+exp+2000<br>

    endpoint - /leaderboard

    **note**: use of \<sep> is important

    # parameters
    - **serverlogo** - logo of the server *required 
    - **pos1** - content related to pos1 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos2** - content related to pos2 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos3** - content related to pos3 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos4** - content related to pos4 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos5** - content related to pos5 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos6** - content related to pos6 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos7** - content related to pos7 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos8** - content related to pos8 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos9** - content related to pos9 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 
    - **pos10** - content related to pos10 eg (avatarurl\<sep>username\<sep>level 1 | exp 100) 

    # returns
    <img src="/asset/leaderme.png">

    """
    a = await anyio.to_thread.run_sync(
        leaderboardCreator, {
            "background": background,
            "serverlogo": serverlogo,
            "pos1": pos1,
            "pos2": pos2,
            "pos3": pos3,
            "pos4": pos4,
            "pos5": pos5,
            "pos6": pos6,
            "pos7": pos7,
            "pos8": pos8,
            "pos9": pos9,
            "pos10": pos10
        })
    return FileResponse(f"./trash/{a}.png")


# endregion

# region [gif endpoints]


@app.get("/triggered.gif",
         response_class=FileResponse,
         tags=["gif endpoints"],
         summary="triggered")
@limiter.limit("100/minute")
async def triggered(request: fastapi.Request,
                    avatar: str,
                    intensity: int = 10):
    """
    make triggered gif meme with variable intensity<br>/triggered.gif?avatar=https://cdn.discordapp.com/avatars/424133185123647488/08d40e3db4b21b887720d649dacc0f5c.png?size=1024<br>

    endpoint - /triggered.gif

    # parameters
    - **avatar** - avatar image url
    - **intensity** - the intensity of trigger [not required]

    # returns
    <img src="/asset/triggered.gif">

    """
    avatar = avatar.replace(".gif", ".png")
    a = await anyio.to_thread.run_sync(trigger_maker, {
        "avatar": avatar,
        "intensity": intensity
    })
    return FileResponse(f"./trash/{a}.gif")


# endregion

# region [premium endpoints]


@app.get("/balance-card", response_class=FileResponse, include_in_schema=False)
@limiter.limit("100/minute")
async def prem_bal_card(request: fastapi.Request, id: str):
    with open("./tempdata/tempbalance.json", "r") as file:
        data = jsonlib.load(file)
        a = prem_balance(data[id])
    return FileResponse(f"./trash/{a}.png")


@app.post("/premium/balance-card",
          response_class=JSONResponse,
          tags=["premium endpoints"],
          summary="balance card")
@limiter.limit("100/minute")
async def premium_blance_card(request: fastapi.Request, bal: BalanceCard):
    with open("./tempdata/tempbalance.json", "r") as file:
        data = jsonlib.load(file)
        tok = secrets.token_urlsafe(16)
        data[tok] = {
            "avatar": bal.avatar,
            "background": bal.background,
            "username": bal.username,
            "balanceimage": bal.balanceimage,
            "balancetext": bal.balancetext,
            "balance": bal.balance,
            "banktext": bal.banktext,
            "bankimage": bal.bankimage,
            "bank": bal.bank,
            "totaltext": bal.totaltext,
            "totalimage": bal.totalimage,
            "total": bal.total
        }
    with open("./tempdata/tempbalance.json", "w") as file:
        jsonlib.dump(data, file, indent=4)

    return {"image": f"https://api.resetxd.xyz/balance-card?id={tok}"}


@app.get("/overlay-card", response_class=FileResponse, include_in_schema=False)
@limiter.limit("100/minute")
async def prem_bal_card(request: fastapi.Request, id: str):
    with open("./tempdata/tempbalance.json", "r") as file:
        data = jsonlib.load(file)
        a = prem_overlay(data[id])
    return FileResponse(f"./trash/{a}.png")


@app.post("/premium/overlays",
          response_class=JSONResponse,
          tags=["premium endpoints"],
          summary="overlays")
@limiter.limit("100/minute")
async def premium_overlays_card(request: fastapi.Request, ov: OverlayCards):
    """
    [POST] 
    
    add any overlay to your api and make your own memes with them!

    # parameters
    - **token** - token that can be registered through homepage
    - **avatar** - avatar image url
    - **overlay** - overlay image url, must have transparent background

    # returns
    this is an example of how the overlay card will look like but doesnt only restrict to this overlay <br>
    <img src= "/asset/overlayfinal.png">
    
    """
    with open("./tempdata/tempbalance.json", "r") as file:
        data = jsonlib.load(file)
        tok = secrets.token_urlsafe(16)
        data[tok] = {"avatar": ov.avatar, "overlay": ov.overlay}
    with open("./tempdata/tempbalance.json", "w") as file:
        jsonlib.dump(data, file, indent=4)

    return {"image": f"https://api.resetxd.xyz/overlay-card?id={tok}"}


@app.get("/fight",
         response_class=FileResponse,
         tags=["image endpoints"],
         summary="fight")
@limiter.limit("100/minute")
async def rip_endpoint(request: fastapi.Request, avatar):
    """
    We will fight under this Banner!!<br>/fight?avatar=https://cdn.discordapp.com/attachments/907213435358547968/974990788972916766/unknown.png<br>

    endpoint - /fight

    # parameters
    - **avatar** - avatar image url

    # returns
    <img src="/asset/fight.png">
    <img src="/asset/fight1.png">
    """

    a = await anyio.to_thread.run_sync(fight, avatar)
    return FileResponse(f"./trash/{a}.png")



# endregion
