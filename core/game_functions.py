import numpy as np
from typing import Optional
from tetris import BaseGame, Move, MoveKind, MoveDelta, PieceType
from tetris.engine import Gravity
import tetris


# region [game endpoint][tetris][functions]

tiles = {
    tetris.MinoType.I:"🟦",
    tetris.MinoType.J:"🟫",
    tetris.MinoType.L:"🟧",
    tetris.MinoType.O:"🟨",
    tetris.MinoType.S:"🟩",
    tetris.MinoType.T:"🟪",
    tetris.MinoType.Z:"🟥",
    tetris.MinoType.EMPTY:"⬜",
    tetris.MinoType.GHOST:"⬛"
}

def tetris_render_board(game):
    return game.render(tiles=tiles)

def tetris_next_piece(game):
    try:
        nex = game.queue[0]
        if nex == PieceType.I:
            return "I"
        elif nex == PieceType.J:
            return "J"
        elif nex == PieceType.L:
            return "L"
        elif nex == PieceType.O:
            return "O"
        elif nex == PieceType.S:
            return "S"
        elif nex == PieceType.T:
            return "T"
        elif nex == PieceType.Z:
            return "Z"
        else:
            return "none"
    except:
        return "none"

class PerMoveGravity(Gravity):
    TILES_PER_MOVE = 1
    MAX_MOVES_AFTER_TOUCH = 5

    def __init__(self, game: BaseGame):
        super().__init__(game)
        self.touched = False
        self.before_lock = 0

    def calculate(self, delta: Optional[MoveDelta] = None) -> None:
        if delta is not None:
            # We were called inside `push()`
            if delta.auto:
                return

            if delta.kind == MoveKind.hard_drop or delta.kind == MoveKind.swap:
                self.touched = False

            piece = self.game.piece
            if self.touched:
                self.before_lock -= 1

            elif self.game.rs.overlaps(minos=piece.minos, px=piece.x + 1, py=piece.y):
                # The piece is resting on a tile
                self.touched = True
                self.before_lock = self.MAX_MOVES_AFTER_TOUCH

            if self.touched and self.before_lock == 0:
                self.game.push(Move(kind=MoveKind.hard_drop, auto=True))
                self.touched = False

            self.game.push(Move(kind=MoveKind.soft_drop, x=self.TILES_PER_MOVE, auto=True))

# endregion



#from akinator.async_aki import Akinator
import akinator

ROW_COUNT = 6
COLUMN_COUNT = 7

def create_aki(lang):
    aki = akinator.Akinator()
    aki.start_game()
    return aki

def action_aki(aki:akinator.Akinator, answer):
    aki.answer(answer)




# region [game endpoint][connect4][functions]
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
 
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
 
    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
 
    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def create_board():
    board = [
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        ]
    return board

def drop_piece(board,row,col,piece):
    board[row][col]= piece

def is_valid_location(board,col):
    return board[5][col]==0

def get_next_open_row(board,col):
    for r in range(ROW_COUNT):
        if board[r][col]==0:
            return r
    
def current_board(board,player1,player2,empty):
    des = ""
    for x in np.flip(board,0):
        for y in x:
            y = int(y)
            if y == 0:
                des += empty
            elif y == 1:
                des += player1
            else:
                des += player2
        des += "\n"
    des += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
    return des

# endregion


# region [game][sokoban]

def is_winning(game):
    compelete = 0
    for x in game["goal"]:
        if game["map"][x[0]][x[1]] in [3]:
            compelete+=1
        else:
            return False
    return compelete == len(game["goal"])

def goal_render(game):
    for x in game["goal"]:
        if game["map"][x[0]][x[1]] in [0]:
            game["map"][x[0]][x[1]] = 4

def analyse(game):
    game["goal"] = []
    for x in range(len(game["map"])):
        for y in range(len(game["map"][x])):
            if game["map"][x][y] == 4:
                game["goal"].append([x, y])
    return game

async def name_checker(mongo, name):
    levelsdb = await mongo["sokoban"]["levels"].find_one({"_id": str(name)})
    return levelsdb == None

def left(game):
    board = game["map"]
    for x in board:
        for y in x:
            if y == 2:
                player_pos = [board.index(x), x.index(y)]
    if board[player_pos[0]][player_pos[1]-1] in [0, 4]:
        board[player_pos[0]][player_pos[1]-1] = 2
        board[player_pos[0]][player_pos[1]] = 0

    elif board[player_pos[0]][player_pos[1]-1] == 3:
        if board[player_pos[0]][player_pos[1]-2] in [0, 4]:
            board[player_pos[0]][player_pos[1]-2] = 3
            board[player_pos[0]][player_pos[1]-1] = 2
            board[player_pos[0]][player_pos[1]] = 0
    goal_render(game)

    game["map"] = board
    return game

async def update_playcount(mongo, level):
    try:
        levelsdb = await mongo["sokoban"]["levels"].update_one({"_id": level}, {'$inc': {'played': 1}})
    except:
        pass

def raw_creator(string):
    ret = []
    string = string.split("/")
    for x in string:
        ret.append(list(map(lambda x: int(x), list(x))))
    return ret

def right(game):
    board = game["map"]
    for x in board:
        for y in x:
            if y == 2:
                player_pos = [board.index(x), x.index(y)]
    if board[player_pos[0]][player_pos[1]+1] in [0, 4]:
        board[player_pos[0]][player_pos[1]+1] = 2
        board[player_pos[0]][player_pos[1]] = 0
    elif board[player_pos[0]][player_pos[1]+1] == 3:
        if board[player_pos[0]][player_pos[1]+2] in [0, 4]:
            board[player_pos[0]][player_pos[1]+2] = 3
            board[player_pos[0]][player_pos[1]+1] = 2
            board[player_pos[0]][player_pos[1]] = 0  
    goal_render(game)
    game["map"] = board
    return game

def up(game):
    board = game["map"]
    for x in board:
        for y in x:
            if y == 2:
                player_pos = [board.index(x), x.index(y)]
    if board[player_pos[0]-1][player_pos[1]] in [0, 4]:
        board[player_pos[0]-1][player_pos[1]] = 2
        board[player_pos[0]][player_pos[1]] = 0

    elif board[player_pos[0]-1][player_pos[1]] == 3:
        if board[player_pos[0]-2][player_pos[1]] in [0, 4]:
            board[player_pos[0]-2][player_pos[1]] = 3
            board[player_pos[0]-1][player_pos[1]] = 2
            board[player_pos[0]][player_pos[1]] = 0

    goal_render(game)
    game["map"] = board
    return game

def down(game):
    board = game["map"]
    for x in board:
        for y in x:
            if y == 2:
                player_pos = [board.index(x), x.index(y)]
    try:
        if board[player_pos[0]+1][player_pos[1]] in [0, 4]:
            board[player_pos[0]+1][player_pos[1]] = 2
            board[player_pos[0]][player_pos[1]] = 0

        elif board[player_pos[0]+1][player_pos[1]] == 3:
            try:
                if board[player_pos[0]+2][player_pos[1]] in [0, 4]:
                    board[player_pos[0]+2][player_pos[1]] = 3
                    board[player_pos[0]+1][player_pos[1]] = 2
                    board[player_pos[0]][player_pos[1]] = 0
            except:
                board[player_pos[0]+1][player_pos[1]] = 2
                board[player_pos[0]][player_pos[1]] = 0

    except:
        pass
    goal_render(game)
    game["map"] = board
    return game

def render_perm(game):
    ret = ""
    for x in range(len(game["map"])):
        for y in range(len(game["map"][x])):
            if game["map"][x][y] == 0:
                ret += "⬛"
            elif game["map"][x][y] == 1:
                ret += "⬜"
            elif game["map"][x][y] == 2:
                ret += "😔"
            elif game["map"][x][y] == 3:
                ret += "🟫"
            elif game["map"][x][y] == 4:
                ret += "🟩"
        ret += "\n"
    return ret

async def create(level, levels):
    level = str(level)
    for x in levels:
        if x["_id"] == level:
            return x
    return levels[level]

async def all(mongo)->dict:
    levelsdb = mongo["sokoban"]["levels"].find({})
    levels = await levelsdb.to_list(1000)
    return levels


# endregion