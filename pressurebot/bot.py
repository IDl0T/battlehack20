import random

from battlehack20.stubs import *

# agnostic memory
DEBUG = 1
ally = None
enemy = None
board_size = None
uninitialized = True
base = None
enemybase = None

# pawn memory
age = None
forward = None
push = False

# overlord memory
turn_number = None
board = None

def dlog(str):
    if DEBUG > 0:
        log(str)

def random_index(rate):
    start = 0
    index = 0
    randnum = random.randint(1, sum(rate))
    for index, scope in enumerate(rate):
        start += scope
        if randnum <= start:
            break
    return index


def try_check_space(r, c):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return None
    # TODO: check sense range
    try:
        return check_space(r, c)
    except:
        return None

# ==================== pawn ========================

def try_move_forward():
    r, c = get_location()
    if try_check_space(r + forward, c) == False:
        move_forward()

def try_capture(r, c):
    if try_check_space(r, c) == enemy:
        capture(r, c)

def no_suicide():
    r, c = get_location()
    return not (try_check_space(r + 2 * forward, c - 1) == enemy or try_check_space(r + 2 * forward, c + 1) == enemy)

def has_backup():
    r, c = get_location()
    dlog(str(base))
    if r == base:
        return True
    return try_check_space(r - forward, c - 1) == ally or try_check_space(r - forward, c + 1) == ally

def mature():
    r, _ = get_location()
    r = r if ally == Team.WHITE else board_size - 1 -r
    mature_coef = 50 # tuneable
    return age - r >= mature_coef

def can_follow():
    r, c = get_location()
    return try_check_space(r + forward * 2, c) == ally

def smart_move():
    r, c = get_location()
    board = [[try_check_space(r + (i - 2) * forward, c + 2 - j) for i in range(5)] for j in range(5)]
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
        score -= 1
    if board[4][3] == enemy:
        score -= 1
    # if board[4][2] == ally:
    #     score += 100
    
    dlog("score = " + str(score))
    if score >= 0:
        try_move_forward()

def pawn():
    # init
    global uninitialized, ally, enemy, forward, board_size, age, base, enemybase, push
    if uninitialized:
        uninitialized = False
        row, col = get_location()
        board_size = get_board_size()
        ally = get_team()
        enemy = Team.WHITE if ally == Team.BLACK else ally.BLACK
        forward = 1 if ally == Team.WHITE else -1
        base = 0 if ally == Team.WHITE else board_size - 1
        enemybase = 0 if ally == Team.BLACK else board_size - 1
        age = 0
        push = False
    r, c = get_location()

    # decide
    if try_check_space(r + forward, c - 1) == enemy:
        try_capture(r + forward, c - 1)
    elif try_check_space(r + forward, c + 1) == enemy:
        try_capture(r + forward, c + 1)
    elif not push and can_follow():
        push = True
        smart_move()
    elif not push and mature():
        dlog("mature")
        push = True
    elif push or no_suicide():
        smart_move()

    # exit
    age += 1
    dlog("Age = " + str(age))

# =================== overlord ========================

def get_spawnrate():
    spawnrate = [0 for i in range(board_size)]
    for c in range(board_size):
        if board[enemybase][c] != ally:
            spawnrate[c] = 1
        for r in range(board_size):
            if board[r][c] == enemy:
                if c - 1 >= 0:
                    spawnrate[c - 1] = 1
                if c + 1 < board_size:
                    spawnrate[c + 1] = 1
                break # save computation

    return spawnrate

def overlord():
    # init
    global uninitialized, ally, enemy, board_size, base, enemybase, turn_number, board
    if uninitialized:
        uninitialized = False
        board_size = get_board_size()
        ally = get_team()
        enemy = Team.WHITE if ally == Team.BLACK else ally.BLACK
        base = 0 if ally == Team.WHITE else board_size - 1
        enemybase = 0 if ally == Team.BLACK else board_size - 1
        turn_number = 0
    board = get_board()

    # decide
    # spawn a pawn, no clogging
    spawnrate = get_spawnrate()
    n = 0
    while spawnrate[turn_number % board_size] == 0 or not try_check_space(base, turn_number % board_size) == False:
        n += 1
        turn_number += 1
        if n == board_size:
            break 
    if spawnrate[turn_number % board_size] > 0 and try_check_space(base, turn_number % board_size) == False:
        spawn(base, turn_number % board_size)

    # exit
    turn_number += 1


def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    robottype = get_type()
    if robottype == RobotType.PAWN:
        pawn()
    else:
        overlord()

    bytecode = get_bytecode()
    dlog('Done! Bytecode left: ' + str(bytecode))
