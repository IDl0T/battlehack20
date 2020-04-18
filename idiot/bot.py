import random, math

from battlehack20.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

board_size, team, opp_team, robottype, time = 0,0,0,0,0

DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        log(str)

def safeMove(row,col,forward):
    if not check_space_wrapper(row + forward, col, board_size):
        move_forward()


def check_space_wrapper(r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return None
    try:
        return check_space(r, c)
    except:
        return None

def pawn():

    #Test pawn lattice
    global board_size, team, opp_team, robottype, time
    row, col = get_location()

    #Generate local board
    #[row][col]
    board = [[check_space_wrapper(r,c,board_size) for c in range(col-2,col+3)] for r in range(row-2,row+3)]
    if team == Team.BLACK:
        board.reverse()
    
    for i in range(5):
        temp = board[i]
        #Map function not allowed
        for j in range(5):
            temp[j] = str(temp[j])
        dlog(" ".join(temp))
        

    if team == Team.WHITE:
        forward = 1
    else:
        forward = -1

    #Always capture, can't go wrong
    if board[3][3] == opp_team: # up and right
        capture(row + forward, col + 1)
        #dlog('Captured at: (' + str(row + forward) + ', ' + str(col + 1) + ')')
    elif board[3][1] == opp_team: # up and left
        capture(row + forward, col - 1)
        #dlog('Captured at: (' + str(row + forward) + ', ' + str(col - 1) + ')')
    # If there is a pawn on both left and right, then try to move forward
    elif board[2][1] == board[2][2] and board[2][2] == board[2][3]:
        safeMove(row,col,forward)
    #Or if there is a pawn behind
    elif board[1][2] == board[2][2]:
        safeMove(row,col,forward)
    

def overlord():
    global board_size, team, opp_team, robottype, time
    #Generate a map of the whole board
    board = get_board()
    if team == Team.BLACK:
        board.reverse()

    #Find if generate on even or odd
    #latticeColor = ((time-1)//(board_size//2)) % 2


    #Select a square to generate

    #Calculate a relative power for each column
    relativePower = [math.inf for col in range(board_size)]
    for column in range(board_size):
        if board[0][column] != None:
            continue
        relativePower[column] = 0.0
        for row in range(board_size):
            if board[row][column] == team:
                relativePower[column] = relativePower[column] + 1.0
            elif board[row][column] == opp_team:
                relativePower[column] = relativePower[column] - 1.0

    copyRelativePower = relativePower[:]
    for column in range(board_size): 
        if column > 0 and copyRelativePower[column-1] != math.inf:
            relativePower[column] = relativePower[column] + copyRelativePower[column-1] * 0.2
        if column < board_size-1 and copyRelativePower[column-1] != math.inf:
            relativePower[column] = relativePower[column] + copyRelativePower[column+1] * 0.2

    #Find a minimum relative power and generate there
    minimumPower = math.inf
    for power in relativePower:
        if power < minimumPower:
            minimumPower = power

    for column in range(board_size):
        if relativePower[column] == minimumPower:
            if team == Team.BLACK:
                spawn(board_size-1,column)
            else:
                spawn(0,column)
            break

def turn():
    global board_size, team, opp_team, robottype, time
    #dlog(str(time))
    time += 1
    board_size = get_board_size()
    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    robottype = get_type()

    if robottype == RobotType.PAWN:
        pawn()
    else:
        overlord()

    bytecode = get_bytecode()

