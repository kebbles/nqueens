import os
import random
import time
import numpy as np
class NQueens:
    def __init__(self,n):
        self.n = n
        # instead of going through all queens multiple times to check for row, column, and diagonal conflicts, memoize them for easier conflict checks
        self.colConflicts = [0] * n          # This list keeps track of queens that conflict on the same column.
        self.diag1Conflicts = [0] * (2*n-1)  # /// direction
                                             # diag1Conflicts[0] is (0,0), diag1Conflicts[1] is (1,0),(0,1), diag1Conflicts[2] is (2,0),(1,1),(0,2) ... etc
        self.diag2Conflicts = [0] * (2*n-1)  # \\\ direction
                                             # diag2Conflicts[0] is (n,0), diag1Conflicts[1] is (n-1,0),(n,1), diag1Conflicts[2] is (n-2,0),(n-1,1),(n,2) ... etc

        self.board = np.zeros((n,n))
        self.queenPositions = []
        self.emptyColumns = set([ i for i in range(n) ])
        self.initialize(n)

    # use NASA paper algorithm to initially place queens
    def initialize(self,n):
        # for row in range(n):
        #     colToPlace = self.minConflicts(row)
        #     self.addQueen(row,colToPlace)

        # populate each subsequent row with a queen
        for row in range(n):
            bestPos = (-1,-1)
            found = False # if a "best" position is found

            # first look for 0 conflict positions (taken from NASA paper initialization type 2)
            sample = 0
            while not found and sample < n:
                col = random.choice(tuple(self.emptyColumns))
                conflicts = self.numConflicts((row,col))
                if conflicts == 0:
                    bestPos = (row,col)
                    found = True
                sample += 1
            
            # if not found, choose a random empty column (taken from NASA paper initialization type 2)
            if not found:
                col = random.choice(tuple(self.emptyColumns))
                bestPos = (row,col)

            assert bestPos != (-1,-1) # make sure a valid position was found
            self.addQueen(bestPos[0],bestPos[1])

    # Given a row and a column, return how many current queen's could reach that square.
    def numConflicts(self,pos):
        row, col = pos[0], pos[1]
        return self.colConflicts[col] + self.diag1Conflicts[(self.n-1)+(col-row)] + self.diag2Conflicts[col+row]

    def pickQueen(self):
        num_queens_conflicted = 0
        candidates = [] # possible queens to fix
        num_vios = 0 # The number of violations for a row/column position.
        for pos in self.queenPositions:
            num_vios = self.numConflicts(pos)
            if num_vios != 3: 
                candidates.append(pos)
        num_queens_conflicted = len(candidates)
        if num_queens_conflicted == 0:  # If the array of possible options is empty return -1,-1
            return (-1,-1)
        # choose random candidate queen who is in conflict
        return random.choice(candidates)

    # places a queen and adds conflicts resulting in placing the queen there
    def addQueen(self,row,col):
        assert self.board[row,col] == 0
        # above assert will fail if the position already has a queen

        self.board[row,col] = 1
        self.queenPositions.append((row,col))
        self.colConflicts[col] += 1
        self.diag1Conflicts[(self.n-1)+(col-row)] += 1
        self.diag2Conflicts[row+col] += 1
        self.emptyColumns.discard(col)

    # removes queen and takes away conflicts the queen originally caused
    def removeQueen(self,row,col):
        assert self.board[row,col] == 1
        assert self.colConflicts[col] > 0
        assert self.diag1Conflicts[(self.n-1)+(col-row)] > 0
        assert self.diag2Conflicts[row+col] > 0

        self.board[row,col] = 0
        self.queenPositions.remove((row,col))
        self.colConflicts[col] -= 1
        self.diag1Conflicts[(self.n-1)+(col-row)] -= 1
        self.diag2Conflicts[row+col] -= 1
        self.updateEmptyColumns(col)

    # moves queen from startPos to endPos
    def moveQueen(self,startPos,endPos):
        # print("Moving queen from",startPos,"to",endPos)
        self.removeQueen(startPos[0],startPos[1])
        self.addQueen(endPos[0],endPos[1])

    # same thing as availablePositions() except you only return those with empty columns
    def emptyColumnPositions(self,pos):
        availablePos = []
        if not self.emptyColumns:
            return []
        for x in self.emptyColumns:
            availablePos.append((pos[0],x))

        return availablePos

    # checks if the column where the queen moved from is now empty, if it is then update
    def updateEmptyColumns(self,col):
        if self.colConflicts[col] == 0:
            self.emptyColumns.add(col)

    # generic min-conflicts algorithm
    def minConflicts(self,row):
        minn = float('inf')
        candidates = []
        for col in range(self.n):
            conflicts = self.numConflicts((row,col))
            if conflicts < minn:
                minn = conflicts
                candidates = [col]
            elif conflicts == minn:
                candidates.append(col)
        choice = random.choice(candidates)
        return choice
    
    def printQueens(self):
        sortedPos = sorted(self.queenPositions, key = lambda x: x[0]) 
        result = []
        for pos in sortedPos:
            result.append(pos[1])
        return result
        

# solver
def solveBoard(size):
    n = size
    NQ = NQueens(n) # create initial board of size nxn
    moves = 0
    print("Starting...")
    while True:
        # print(moves)
        if moves > 100:
            print("Resetting...")
            moves = 0
            NQ = NQueens(n) # reset board since on average a board can be solved in around 50 moves, prevents getting stuck

        # General Note: when finding possible places to move the randomly picked queen, we retrict their search to the row that they're currently in
        # this means queens cannot move from one row to another nor should they consider this when checking for possible candidate positinos
        # since every queen occupies a unique row

        # pick the queen to be moved
        pickedQueen = NQ.pickQueen()

        # if there is no queen to fix, break and end
        # success
        if pickedQueen == (-1,-1):
            break

        # set initial value
        minConflictPosition = (-1,-1)

        found = False #skip the next rest of the search heuristics if a position has been found

        # look first for 0 conflict positions using "emptyColumns" (taken from NASA paper)
        emptyColPositions = NQ.emptyColumnPositions(pickedQueen)
        for pos in emptyColPositions:
            assert NQ.board[pos[0],pos[1]] == 0
        for pos in emptyColPositions:
            newNumberOfConflicts = NQ.numConflicts(pos)
            if newNumberOfConflicts == 0:
                # print("found empty column")
                found = True
                minConflictPosition = pos
                break
        
        # if 0 conflict positions cannot be found, then randomly sample for 1 conflict positions
        # usually found pretty quickly though theoretically can go on forever (taken from NASA paper)
        samples = 0
        while not found and samples < n:
            randomIndex = random.randint(0,n-1)
            pos = (pickedQueen[0],randomIndex) # possible positions are only in your pickedQueen's row and a random column
            newNumberOfConflicts = NQ.numConflicts(pos)
            if newNumberOfConflicts == 1:
                # print("found 1 conflict column")
                found = True
                minConflictPosition = pos
            samples += 1

        #normal search through all positions (while staying in the same row)
        if not found:
            # print("used min-conflict")
            colToPut = NQ.minConflicts(pickedQueen[0])
            minConflictPosition = (pickedQueen[0],colToPut)

        assert minConflictPosition != (-1,-1)
        NQ.moveQueen(pickedQueen,minConflictPosition)# move queen to least conflict spot
        moves+=1

    return NQ.printQueens()

def main():
    cwd = os.getcwd().replace('\\', '/') # gets the current working directory of this python file

    f1 = open(cwd + "/nqueens.txt", mode='r') # opens the nqueens file to read the n's from
    nums = [line.rstrip('\n') for line in f1]
    print(nums)

    f2 = open(cwd + "/nqueens_out.txt", mode='w+') # creates an output file for the matrices to be placed in

    # writes the solution to each size n to the output file
    for n in nums:
        start = time.time()
        print(n)
        positions = solveBoard(int(n))
        f2.write(str(positions))
        end = time.time()
        print("Took " + str(end-start) + " seconds to execute")
    f2.close()

main()
