import random

from battlehack20.stubs import *

# agnostic memory
DEBUG = 1
ally = None
enemy = None
board_size = None
uninitialized = True
base = None

# pawn memory
age = None
forward = None
push = False

# overlord memory
turn_number = None


def dlog(str):
    if DEBUG > 0:
        log(str)


def try_check_space(r, c):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return None
    # TODO: check sense range
    try:
        return check_space(r, c)
    except:
        return None


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
    mature_coef = 60 # tuneable
    return age - r >= mature_coef

def can_follow():
    r, c = get_location()
    return try_check_space(r + forward * 2, c) == ally

def pawn():
    # init
    global uninitialized, ally, enemy, forward, board_size, age, base, push
    if uninitialized:
        uninitialized = False
        row, col = get_location()
        ally = get_team()
        enemy = Team.WHITE if ally == Team.BLACK else ally.BLACK
        forward = 1 if ally == Team.WHITE else -1
        board_size = get_board_size()
        base = 0 if ally == Team.WHITE else board_size - 1
        age = 0
        push = False
    r, c = get_location()

    # decide
    if try_check_space(r + forward, c - 1) == enemy:
        try_capture(r + forward, c - 1)
    elif try_check_space(r + forward, c + 1) == enemy:
        try_capture(r + forward, c + 1)
    elif can_follow():
        push = True
        try_move_forward()
    elif mature():
        dlog("mature")
        push = True
        try_move_forward()
    elif push or no_suicide():
        try_move_forward()

    # exit
    age += 1
    # dlog("Age = " + str(age))


def overlord():
    # init
    global uninitialized, ally, enemy, board_size, base, turn_number
    if uninitialized:
        uninitialized = False
        ally = get_team()
        enemy = Team.WHITE if ally == Team.BLACK else ally.BLACK
        board_size = get_board_size()
        base = 0 if ally == Team.WHITE else board_size - 1
        turn_number = 0

    # decide
    # spawn a pawn, no clogging
    col = turn_number % board_size
    while try_check_space(base, col) != False:
        col = (col + 1) % board_size
        if col == turn_number % board_size:
            break
    if try_check_space(base, col) == False:
        spawn(base, col)

    # exit
    turn_number = col + 1


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
    # dlog('Done! Bytecode left: ' + str(bytecode))
