import math
from battlehack20.stubs import *

#=================== GlOBAL CODE ===================#

board_size, ally, enemy, init = 0, None, None, False
board, prev_board = [], []

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


row, col, forward, age = 0, 0, 0, 0
push_wait_time = 25 # tunable
push_timer = push_wait_time
stationary = 0


def try_check_space(r, c, board_size):
    try:
        if r < 0 or c < 0 or c >= board_size or r >= board_size:
            return False
        out = check_space(r, c)
        return None if out == False else out
    except:
        return False  # shouldn't happen


def smart_move():
    global push_timer, stationary
    score, can_push, no_enemy = 0, False, True

    # prioritize capture
    if board[3][3] == enemy:  # up and right
        capture(row + forward, col + 1)
        return
    elif board[3][1] == enemy:  # up and left
        capture(row + forward, col - 1)
        return

    # calculate ally support - inferred enemy support
    # score > 0 means good chance to win the trade
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
        no_enemy = False
        if board[4][2] == ally or board[4][0] == ally:  # inference
            score += 1
    if board[4][3] == enemy:
        no_enemy = False
        score -= 3
        if board[4][2] == ally or board[4][4] == ally:
            score += 1

    # Don't move forward when acting as the only support
    if board[3][1] == ally and board[1][2] != ally:
        if board[4][2] == enemy or board[4][0] == enemy:
            score -= 10
    if board[3][3] == ally and board[1][2] != ally:
        if board[4][2] == enemy or board[4][4] == enemy:
            score -= 10
    
    # can push only with adequate support and good formation
    if score == 0 and board[1][2] == ally and board[0][2] == ally and \
            (board[3][1] == ally or board[3][1] == False) and \
            (board[3][3] == ally or board[3][3] == False):
        can_push = True

    # count down to push, or follow the ally
    if stationary >= 200: # tunable
        can_push, push_timer = True, 1 # if being stationaty too long, force move
    if can_push:
        push_timer -= 1
        stationary = 0
        if board[3][0] == ally and board[4][0] != ally and prev_board[3][0] != ally or \
            board[3][4] == ally and board[4][3] != ally and prev_board[3][4] != ally:  # ally push
            push_timer = 0  # follow
        if push_timer <= 0 and board[3][2] == None:
            move_forward()
            push_timer = push_wait_time
            return
    else:
        stationary += 1
        push_timer = push_wait_time  # reset timer

    # when can't push, be smart
    if (score > 0 or no_enemy) and board[3][2] == None:
        move_forward()


def pawn_init():
    global board_size, ally, enemy, forward, age, stationary
    board_size = get_board_size()
    ally = get_team()
    enemy = Team.WHITE if ally == Team.BLACK else Team.BLACK
    forward = 1 if ally == Team.WHITE else -1
    age, stationary = 0, 0
    prev_board = [[None for j in range(5)] for i in range(5)]


def pawn_turn():
    global board, row, col, init, age, push_timer, prev_board
    # Init

    if init == False:
        init = True
        pawn_init()

    # Position update
    row, col = get_location()
    age += 1
    prev_board = board
    board = [[try_check_space(r, c, board_size) for c in range(
        col-2, col+3)] for r in range(row-2, row+3)]
    if ally == Team.BLACK:
        board.reverse()

    # prioritize capture
    if col % 2 == 0:
        if board[3][3] == enemy:  # up and right
            capture(row + forward, col + 1)
        elif board[3][1] == enemy:  # up and left
            capture(row + forward, col - 1)
        else:
            smart_move()
    else:
        if board[3][1] == enemy:  # up and left
            capture(row + forward, col - 1)
        elif board[3][3] == enemy:  # up and right
            capture(row + forward, col + 1)
        else:
            smart_move()

    # exit

#=================== OVERLORD CODE ===================#


time = 0

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
    global board
    # calculate urgency
    cols = [[0, i] for i in range(board_size)]
    # better starter
    for c in range(0, board_size, 2):
        empty = True
        for r in range(board_size):
            if board[r][c] == ally:
                empty = False
                break
        if empty:
            cols[c][0] = cols[c][0] + 1000

    for c in range(board_size):
        cols[c][0] = cols[c][0] + 4

    for r in range(board_size):
        for c in range(board_size):
            if board[r][c] == ally:
                cols[c][0] = cols[c][0] - 1

    cols.sort(key=lambda a: a[0] * 2, reverse=True)
    base = 0 if ally == Team.WHITE else board_size - 1

    # spawn
    for _, c in cols:
        if try_spawn(base, c):
            return


def overlord_init():
    global board_size, ally, enemy, time, pillar_length
    board_size = get_board_size()
    ally = get_team()
    enemy = Team.WHITE if ally == Team.BLACK else Team.BLACK
    time, pillar_length = 0, 1


def overlord_turn():
    global board, board_size, ally, enemy, init, time, pillar_length
    # Init
    if init == False:
        init = True
        overlord_init()

    # update board
    board = get_board()
    if ally == Team.BLACK:
        board.reverse()

    smart_spawn()

    # exit
    # increase pillar length as time pass

    time += 1
    


#=================== TURN CODE ===================#

def turn():
    robottype = get_type()
    if robottype == RobotType.PAWN:
        pawn_turn()
    else:
        overlord_turn()
