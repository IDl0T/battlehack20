import random

from battlehack20.stubs import *

# agnostic memory
DEBUG = 1
team = None
opp_team = None
board_size = None
uninitialized = True

# pawn memory
turn_left_to_move = None
forward = None

# overlord memory
turn_number = None
base = None


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
    if try_check_space(r, c) == opp_team:
        capture(r, c)

def no_suicide():
    r, c = get_location()
    return not (try_check_space(r + 2 * forward, c - 1) == opp_team or try_check_space(r + 2 * forward, c + 1) == opp_team)

def pawn():
    # init
    global uninitialized, team, opp_team, forward, board_size, turn_left_to_move
    if uninitialized:
        uninitialized = False
        row, col = get_location()
        team = get_team()
        opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
        forward = 1 if team == Team.WHITE else -1
        board_size = get_board_size()
        turn_left_to_move = board_size // 2 - col // 2 - 1
    row, col = get_location()

    # decide
    if try_check_space(row + forward, col - 1):
        try_capture(row + forward, col - 1)
    elif try_check_space(row + forward, col + 1):
        try_capture(row + forward, col + 1)
    elif turn_left_to_move <= 0 and no_suicide():
        try_move_forward()
        turn_left_to_move = board_size // 2

    # exit
    turn_left_to_move -= 1
    dlog(str(turn_left_to_move))


def overlord():
    # init
    global uninitialized, team, opp_team, board_size, base, turn_number
    if uninitialized:
        uninitialized = False
        team = get_team()
        opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
        board_size = get_board_size()
        base = 0 if team == Team.WHITE else board_size - 1
        turn_number = 0

    # decide
    offset = turn_number // (board_size // 2) % 2
    col = (turn_number * 2 + offset) % board_size
    if try_check_space(base, col) == False:
        spawn(base, col)
        dlog("spawn sucessful")
    else:
        dlog("spawn unsucessful")

    # exit
    turn_number += 1


def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """

    team = get_team()
    robottype = get_type()
    dlog('Team: ' + str(team) + 'Type: ' + str(robottype))

    if robottype == RobotType.PAWN:
        pawn()
    else:
        overlord()

    bytecode = get_bytecode()
    dlog('Done! Bytecode left: ' + str(bytecode))
