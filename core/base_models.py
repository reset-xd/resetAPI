from pydantic import BaseModel

# region [database]

class create_db(BaseModel):
    token:str
    name:str

class insert_db(BaseModel):
    token:str
    collection:str
    value:dict

class leaderboard_db(BaseModel):
    token:str
    collection:str
    key:str
    order:str

class update_db(BaseModel):
    token:str
    collection:str
    where:dict
    value:dict

class delete_entry(BaseModel):
    token:str
    collection:str
    value:dict

# endregion

# region [game][connect4]

class c4_creator(BaseModel):
    player1:str
    player2:str
    empty:str

class c4_get_board(BaseModel):
    game_id:str

class c4_drop(BaseModel):
    game_id:str
    column:int
    player:int

# endregion

# region [game][tetris]

class tetris_action(BaseModel):
    game_id: str
    action: str

# endregion

# region [premium]

class AkinatorGameAction(BaseModel):
    game_id: str
    action: str

class AkinatorGameClose(BaseModel):
    game_id: str

class AkinatorCreate(BaseModel):
    language: str
    
class BalanceCard(BaseModel):
    token: str
    avatar: str
    background: str
    username: str
    balancetext: str
    balanceimage: str
    balance: str
    banktext: str
    bankimage: str
    bank: str
    totaltext: str
    totalimage: str
    total: str

class OverlayCards(BaseModel):
    token: str
    avatar: str
    overlay: str

# endregion

# region [game][sokoban]

class sokobancreate(BaseModel):
    level: str

class sokobancreatelevelthing(BaseModel):
    level: str
    name: str
    author: str

class sokobanaction(BaseModel):
    game_id: str
    action: str

# endregion