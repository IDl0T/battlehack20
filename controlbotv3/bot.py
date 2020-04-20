import math
from battlehack20.stubs import *



#=================== GlOBAL CODE ===================#

board_size, team, opp_team, robottype, latticeThickness, init = 0,0,0,0,0,0
board = []

DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        log(str)

def dlogArray(arr):
    for i in range(len(arr)):
        arr[i] = str(arr[i])
    dlog(" ".join(arr))

#=================== PAWN CODE ===================#

row, col, forward = 0,0,1

def pawnCheckSpace(r, c, board_size):

    try:
        #dlog(str(r))
        #dlog(str(c))
        if r < 0 or c < 0 or c >= board_size or r >= board_size:
            return False
        res = check_space(r, c)
        if res == False:
            return None
        else:
            return res
    except:
        return False

def safeMove():
    global board

    #Don't move forward if not possible
    if board[3][2] != None:
        return False

    numSupport = 0
    numDanger = 0
    #Compare personal support and danger
    if board[4][1] == opp_team:
        numDanger+=1
    if board[4][3] == opp_team:
        numDanger+=1
    if board[2][1] == team:
        numSupport +=1
    if board[2][3] == team:
        numSupport +=1
    if numDanger > numSupport:
        return False

    #Don't move forward when acting as support
    if board[3][1] == team:
        if board[4][2] == opp_team or board[4][0] == opp_team:
            return False
    if board[3][3] == team:
        if board[4][2] == opp_team or board[4][4] == opp_team:
            return False

    move_forward()
    return True
    
def pawnInit():
    global board_size, team, opp_team, robottype, forward
    board_size = get_board_size()
    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    robottype = get_type()
    if team == Team.BLACK:
        forward = -1

def pawnTurn():
    global board,board_size, team, opp_team, robottype, row, col, init, forward
    #Init
    if init == 0:
        init == 1
        pawnInit()

    #Position update
    row, col = get_location()
    myRow = row
    board = [[pawnCheckSpace(r,c,board_size) for c in range(col-2,col+3)] for r in range(row-2,row+3)]
    if team == Team.BLACK:
        board.reverse()
        myRow = board_size-myRow-1

    #Attack first, questions later
    #TODO: Smarter algorithm determining combat
    if board[3][3] == opp_team: # up and right
        capture(row + forward, col + 1)
        return
    elif board[3][1] == opp_team: # up and left
        capture(row + forward, col - 1)
        return
    
    safeMove()
    

#=================== OVERLORD CODE ===================#

time, spawnRow = 0, 0

def trySpawn(row,col):
    #Make sure that not spawning on dangerous position
    if row == 0:
        if col > 0:
            if check_space(1,col-1) == opp_team:
                return False
        if col < board_size-1:
            if check_space(1,col+1) == opp_team:
                return False
    if row == board_size-1:
        if col > 0:
            if check_space(board_size-2,col-1) == opp_team:
                return False
        if col < board_size-1:
            if check_space(board_size-2,col+1) == opp_team:
                return False

    try:
        spawn(row,col)
        return True
    except:
        return False

def overlordInit():
    global board_size, team, opp_team, robottype, time, spawnRow
    board_size = get_board_size()
    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    robottype = get_type()
    if team == Team.BLACK:
        spawnRow = board_size-1

def overlordTurn():
    global board_size, team, opp_team, robottype, init, time, spawnRow
    #Init
    if init == 0:
        init == 1
        overlordInit()
    
    time += 1

    #Position updates
    board = get_board()
    if team == Team.BLACK:
        board.reverse()
    
    

    
 
    
    
    
    

#=================== TURN CODE ===================#

def turn():

    global robottype
    robottype = get_type()
    if robottype == RobotType.PAWN:
        pawnTurn()
    else:
        overlordTurn()

