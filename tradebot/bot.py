import math
from battlehack20.stubs import *

#=================== GlOBAL CODE ===================#

board_size, ally, enemy, init = 0, None, None, False
board = []

DEBUG = 1


def dlog(str):
    if DEBUG > 0:
        log(str)


def dlog_array(arr):
    cache = []
    for i in range(len(arr)):
        cache.append(str(arr[i]))
    dlog(" ".join(cache))


def argmax(arr):
    maximum, out = -math.inf, 0
    for i, v in enumerate(arr):
        if maximum < v:
            maximum, out = v, i
    return out

#=================== PAWN CODE ===================#


row, col, forward = 0, 0, 0


def try_check_space(r, c, board_size):
    try:
        if r < 0 or c < 0 or c >= board_size or r >= board_size:
            return False
        out = check_space(r, c)
        return None if out == False else out
    except:
        return False  # shouldn't happen


def smart_move():
    score = 0
    if board[2][1] == ally:
        score += 1
        if board[1][1] == ally:
            score += 1
            if board[0][1] == ally:
                score += 1
    if board[2][3] == ally:
        score += 1
        if board[1][3] == ally:
            score += 1
            if board[0][3] == ally:
                score += 1
    if board[4][1] == enemy:
        score -= 3
        if board[4][2] == ally or board[4][0] == ally:  # inference
            score += 1
    if board[4][3] == enemy:
        score -= 3
        if board[4][2] == ally or board[4][4] == ally:
            score += 1
    if score == 0 and board[1][2] == ally and board[0][2] == ally:
        score += 1


    # Don't move forward when acting as support
    if board[3][1] == ally:
        if board[4][2] == enemy or board[4][0] == enemy:
            score -= 20
    if board[3][3] == ally:
        if board[4][2] == enemy or board[4][4] == enemy:
            score -= 20


    # keep position
    stage = row if ally == Team.WHITE else board_size - 1 - row
    if stage >= board_size / 2 - 1 + col % 2:
        score -= 100

    if score >= 0 and board[3][2] == None:
        move_forward()


def pawn_init():
    global board_size, ally, enemy, forward, age
    board_size = get_board_size()
    ally = get_team()
    enemy = Team.WHITE if ally == Team.BLACK else Team.BLACK
    forward = 1 if ally == Team.WHITE else -1
    age = 0


def pawn_turn():
    global board, board_size, ally, enemy, row, col, init, forward, age
    # Init
    if init == False:
        init == True
        pawn_init()

    # Position update
    row, col = get_location()
    board = [[try_check_space(r, c, board_size) for c in range(
        col-2, col+3)] for r in range(row-2, row+3)]
    if ally == Team.BLACK:
        board.reverse()

    # prioritize capture
    if board[3][3] == enemy:  # up and right
        capture(row + forward, col + 1)
    elif board[3][1] == enemy:  # up and left
        capture(row + forward, col - 1)
    else:
        smart_move()

    # exit
    age += 1

#=================== OVERLORD CODE ===================#


time, pillar_length = 0, 0


def try_spawn(row, col):
    # Make sure that not spawning on dangerous position
    if row == 0:
        if col > 0:
            if check_space(1, col-1) == enemy:
                return False
        if col < board_size-1:
            if check_space(1, col+1) == enemy:
                return False
    if row == board_size-1:
        if col > 0:
            if check_space(board_size-2, col-1) == enemy:
                return False
        if col < board_size-1:
            if check_space(board_size-2, col+1) == enemy:
                return False

    try:
        spawn(row, col)
        return True
    except:
        return False


def smart_spawn():
    global board, pillar_length
    # calculate urgency
    cols = [(0., i) for i in range(board_size)]
    # better starter
    for c in range(0, board_size, 2):
        empty = True
        for r in range(board_size):
            if board[r][c] == ally:
                empty = False
                break
        if empty:
            cols[c] = (cols[c][0] + 1000, c)

    for c in range(board_size):
        if c % 2 == 1:  # attack col
            cols[c] = (4., c)
    for r in range(board_size):
        for c in range(board_size):
            if board[r][c] == ally:
                if c % 2 == 0:  # defense col
                    cols[c] = (cols[c][0] - 17, c)
                else:  # attack col
                    cols[c] = (cols[c][0] - 1, c)

            elif board[r][c] == enemy:
                cols[c//2*2] = (cols[c//2*2][0] + 10, c//2*2)
    cols.sort(key=lambda a: a[0], reverse=True)
    base = 0 if ally == Team.WHITE else board_size - 1

    # spawn
    for v, c in cols:
        if try_spawn(base, c):
            break


def overlord_init():
    global board_size, ally, enemy, time, pillar_length
    board_size = get_board_size()
    ally = get_team()
    enemy = Team.WHITE if ally == Team.BLACK else Team.BLACK
    time, pillar_length = 0, 0


def overlord_turn():
    global board, board_size, ally, enemy, init, time, pillar_length
    # Init
    if init == False:
        init == True
        overlord_init()

    # update board
    board = get_board()
    if ally == Team.BLACK:
        board.reverse()

    # Build pawns in weak columns
    smart_spawn()

    # exit
    time += 1


#=================== TURN CODE ===================#

def turn():
    robottype = get_type()
    if robottype == RobotType.PAWN:
        pawn_turn()
    else:
        overlord_turn()
