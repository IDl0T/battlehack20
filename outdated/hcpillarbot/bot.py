import math
from battlehack20.stubs import *



#=================== GlOBAL CODE ===================#

board_size, team, opp_team, robottype, latticeThickness, init = 0,0,0,0,0,0
defenseLattice,board = [],[]

DEBUG = 1
def dlog(str):
    if DEBUG > 0:
        log(str)

def dlogArray(arr):
    for i in range(len(arr)):
        arr[i] = str(arr[i])
    dlog(" ".join(arr))

def dlogPowerArray(arr):
    new = []
    for col in arr:
        new.append(col[0])
    dlogArray(new)

#Returns a 2 - 3 thick lattice depending on the map size
def generateDefenseLattice():
    global latticeThickness
    res = [[False for c in range(board_size)]for r in range(board_size)]

    #Thic lattice
    for row in range(1,3):
        for col in range(board_size):
            res[row][col] = True
    
    return res


#=================== PAWN CODE ===================#

row, col, forward = 0,0,1
pawnState = "Defending"

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
    if numDanger > 0 and numSupport == 0:
        return False

    #Don't move forward when acting as support
    if board[3][1] == team and board[4][2] == opp_team:
        return False
    if board[3][3] == team and board[4][2] == opp_team:
        return False

    move_forward()
    return True
    

def pawnInit():
    global board_size, team, opp_team, robottype, defenseLattice, forward
    board_size = get_board_size()
    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    robottype = get_type()
    defenseLattice = generateDefenseLattice()
    if team == Team.BLACK:
        forward = -1

def pawnTurn():
    global board,board_size, team, opp_team, robottype, row, col, init, forward, pawnState
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

    #Decisions
    if myRow >= 3:
        pawnState="Attacking"
    
    if pawnState =="Defending":
        if defenseLattice[myRow+1][col] == True or defenseLattice[myRow+2][col] == True:
            safeMove()
            return
        if board[0][2] == team and board[1][2] == team:
            safeMove()
            return
    
    if pawnState =="Attacking":
        if board[1][2] == team and board[0][2] == team:
            safeMove()
            return
    

#=================== OVERLORD CODE ===================#

time = 0

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
    global board_size, team, opp_team, robottype, time, defenseLattice
    board_size = get_board_size()
    team = get_team()
    opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
    robottype = get_type()
    defenseLattice = generateDefenseLattice()

def overlordTurn():
    global board_size, team, opp_team, robottype, init, time
    #Init
    if init == 0:
        init == 1
        overlordInit()
    
    time += 1

    #Position updates
    board = get_board()
    if team == Team.BLACK:
        board.reverse()

    #Calculate a relative power for each column
    relativePower = [[math.inf,col] for col in range(board_size)]
    for column in range(board_size):
        if board[0][column] != None:
            continue
        relativePower[column][0] = 0.0
        for row in range(board_size):
            if board[row][column] == team:
                relativePower[column][0] = relativePower[column][0] + 1.0
            elif board[row][column] == opp_team:
                relativePower[column][0] = relativePower[column][0] - 1.0

    #dlogPowerArray(relativePower)

    copyRelativePower = []
    for i in relativePower:
        copyRelativePower.append(i[0])

    for column in range(board_size): 
        if column > 0 and copyRelativePower[column-1] != math.inf:
            relativePower[column][0] = relativePower[column][0] + copyRelativePower[column-1] * 1
        if column < board_size-1 and copyRelativePower[column+1] != math.inf:
            relativePower[column][0] = relativePower[column][0] + copyRelativePower[column+1] * 1
    
    #dlogPowerArray(relativePower)

    #In order of minimum power, check if defense lattice is not finished.
    relativePower.sort()

    if team == Team.BLACK:
        r = board_size-1
    else:
        r = 0

    for column in relativePower:
        col = column[1]
        numMissing = 0
        numDefenders = 0
        for row in range(0,3):
            if defenseLattice[row][col]:
                numMissing += 1
            if board[row][col] == team:
                numDefenders += 1
        
        if numDefenders >= numMissing:
            continue

        if (trySpawn(r,col)):
            return
    
    #If defense lattice has been finished, build attack pillar on right half of the map
    #Hence name, half court bot
    targetColumn = 1
    for column in relativePower:
        col = column[1]
        if col >= board_size//2-1:
            trySpawn(r,col)
    
    #And just build somewhere if somehow that fails
    for col in range(board_size):
        trySpawn(r,col)
    

#=================== TURN CODE ===================#

def turn():

    global robottype
    robottype = get_type()
    if robottype == RobotType.PAWN:
        pawnTurn()
    else:
        overlordTurn()

