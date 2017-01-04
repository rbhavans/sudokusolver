#! /usr/bin/python

import sys

#Class that defines a PuzzleCell. Each Cell has attributes like
# Value - if the value is either given or unequivocally deduced.
# possibleValues - if the value is not given, the computed array poss values 
class PuzzleCell :
	def __init__(self, value) :
		self.value = value
		self.possibleValues = []	   

	def printCell(self) :
		sys.stdout.write(self.value + " ")

	def copy(self, anotherCell) :
		anotherCell.value = self.value
		for i in range(len(self.possibleValues)) :
			anotherCell.possibleValues.append(self.possibleValues[i])
########## END OF CLASS PUZZLECELL##############################

#Class that defines the puzzle itself. It is for now populated by reading a
#file. Attributes include 
#puzzleCells - Array of PuzzleCells
#rowIndex - This is how many rows are expected to be in the puzzle = 9. 
#colIndex - This is how many columns are expected to be in the puzzle = 9. 
#newlyPatchedValues - Array of the i,j coordinates of the cells for which there
#											can only be one value. something like [[2,3], [4,5]] 
#											where the puzzleCells[2][3].possibleValues only has one
#											value and can is the Value of the cell.
#twoChoices - This is an array of i,j coordinates of the cells for which there
#							can be 2 possible values. This is of value, because, when we are
#							not able to deduce any values, we pick the first element of this
#							array and use the first possible value to see if we run into a 
#							contradiction. If so, we backtrack. If not, we are done.
class Puzzle :
	def __init__(self) :
			self.reset()

	def reset(self) :
			self.rowIndex = 0
			self.colIndex = 0
			self.puzzleCells = []
			self.newlyPatchedValues = []
			self.twoChoices = []
			self.twoChoicesIndex = 0
			self.patched = False


	def loadFile(self, filename) :
		with open(filename) as puzzleFileHdl :
			for line in puzzleFileHdl:
				self.colIndex = 0
				self.puzzleCells.append([])
				valuesArray = line.strip().split(' ')
				for value in valuesArray :
					self.puzzleCells[self.rowIndex].append(PuzzleCell(value))
					self.colIndex+=1
				self.rowIndex+=1

	def printPatchArray(self, array) :
		for i in range(len(array)) :
			sys.stdout.write("[" + str(array[i][0]) + ", " + str(array[i][1]) + \
					"]: " + str(self.puzzleCells[array[i][0]][array[i][1]].value) +" ")
		sys.stdout.write('\n')

	def printTwoChoiceArray(self, array) :
		for i in range(len(array)) :
			sys.stdout.write("[" + str(array[i][0]) + ", " + str(array[i][1]) + \
					"]: " + str(self.puzzleCells[array[i][0]][array[i][1]].possibleValues) +" ")
		sys.stdout.write('\n')

	def printPossibleValues(self, array) :
		sys.stdout.write("[");
		for i in range(self.rowIndex) :
			ch = 'x';
			if (i + 1 in array) :
				ch = i + 1;
			sys.stdout.write(ch + ",");
		sys.stdout.write("]");

	def printPuzzleDebug(self) :
		sys.stdout.write("Puzzle Rows: ");
		sys.stdout.write(str(self.rowIndex));
		sys.stdout.write(" Puzzle Cols: ");
		sys.stdout.write(str(self.colIndex));
		sys.stdout.write("\n");
		sys.stdout.write("newlyPatchedValues Array: ")
		self.printPatchArray(self.newlyPatchedValues)
		sys.stdout.write("length of newlyPatchedValues Array: " + str(len(self.newlyPatchedValues)));
		sys.stdout.write("\n");
		sys.stdout.write("patched: " + str(self.patched));
		sys.stdout.write("\n");
		sys.stdout.write("twoChoices Index" + str(self.twoChoicesIndex));
		sys.stdout.write("\n");
		sys.stdout.write("twoChoices Array");
		self.printTwoChoiceArray(self.twoChoices)

		for i in range(self.rowIndex) :
			for j in range (self.colIndex) :
				self.puzzleCells[i][j].printCell()
			sys.stdout.write('\n')

	def printPuzzle(self, indent) :
		for i in range(self.rowIndex) :
			for j in range(indent) :
				sys.stdout.write('\t')
			for j in range (self.colIndex) :
				self.puzzleCells[i][j].printCell()
			sys.stdout.write('\n')
	   

# Return a row of the puzzle. if the 2nd argument, row, is 3, return 3rd row
	def puzzleRow(self, row) :
		returnColumn = []
		for j in xrange(9) :
			returnColumn.append(self.puzzleCells[row][j].value)
		return returnColumn

# Return a column of the puzzle. if the 2nd argument, column, is 3,
# return 3rd column`
	def puzzleColumn(self, column) :
		returnColumn = []
		for i in xrange(9) :
			returnColumn.append(self.puzzleCells[i][column].value)
		return returnColumn

# Return a list of elements in a box. you get the same list for
# row = 1, col = 1 and row =2, col = 1 etc.
	def puzzleBox(self, row, col) :
		rowRangeLower = row / 3 * 3
		rowRangeHigher = rowRangeLower + 3
		colRangeLower = col / 3 * 3
		colRangeHigher = colRangeLower + 3
		returnArray = []

		for i in xrange(rowRangeLower, rowRangeHigher) :
			for j in xrange(colRangeLower, colRangeHigher) :
				returnArray.append(self.puzzleCells[i][j].value)
		return returnArray

#Not a very good name, but what this does is that, given an array like
#[1, 3, 5] and row or column like [1 x x x 4 x 3 x x] it returns [5] since
#1 and 3 are in the first array and also in the second.
#This is used to determine
	def dropDuplicates(self, fullRow, puzzleRow) :
		fullRowCopy = fullRow
		for i in xrange(0, len(puzzleRow)) :
			if puzzleRow[i] != 'x' and puzzleRow[i]  in fullRow :
				fullRowCopy.remove(puzzleRow[i])
		return fullRowCopy

	def findCellsWithUniqueNumbersInARow(self) :
		canBeIn = dict([
										('1', []),
										('2', []),
										('3', []),
										('4', []),
										('5', []),
										('6', []),
										('7', []),
										('8', []),
										('9', [])
									])
		for ch in canBeIn.keys() :
			for i in range(self.rowIndex) :
				canBeIn[ch] = []
				for j in range(self.colIndex) :
					if ch in self.puzzleCells[i][j].possibleValues :
						canBeIn[ch].append([i,j])

				if len(canBeIn[ch]) == 1 :
#					print ch + "can only be in Row " + str(canBeIn[ch][0][0]) + ", " + \
#							 str(canBeIn[ch][0][1] )
					self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues = []
					self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues.append(ch)
					if canBeIn[ch][0] not in self.newlyPatchedValues :
						self.newlyPatchedValues.append(canBeIn[ch][0])

	def findCellsWithUniqueNumbersInAColumn(self) :
		canBeIn = dict([
										('1', []),
										('2', []),
										('3', []),
										('4', []),
										('5', []),
										('6', []),
										('7', []),
										('8', []),
										('9', [])
									])
		for ch in canBeIn.keys() :
			for j in range(self.colIndex) :
				canBeIn[ch] = []
				for i in range(self.rowIndex) :
					if ch in self.puzzleCells[i][j].possibleValues :
						canBeIn[ch].append([i,j])

				if len(canBeIn[ch]) == 1 :
#					print ch + "can only be in column " + str(canBeIn[ch][0][0]) + ", " + \
#								 str(canBeIn[ch][0][1] )
					self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues = []
					self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues.append(ch)
					if canBeIn[ch][0] not in self.newlyPatchedValues :
						self.newlyPatchedValues.append(canBeIn[ch][0])

	def findCellsWithUniqueNumbersInABox(self) :
		canBeIn = dict([
										('1', []),
										('2', []),
										('3', []),
										('4', []),
										('5', []),
										('6', []),
										('7', []),
										('8', []),
										('9', [])
									])
		for boxRow in range(3) :
			iLower = boxRow / 3 * 3
			iUpper = iLower + 3
			for boxCol in range(3) :
				jLower = boxCol / 3 * 3
				jUpper = jLower + 3
				for ch in canBeIn.keys() :
					canBeIn[ch] = []
					for i in range(iLower, iUpper) :
						for j in range(jLower, jUpper) :
							if ch in self.puzzleCells[i][j].possibleValues :
								canBeIn[ch].append([i, j])

					if len(canBeIn[ch]) == 1 :
#						print ch + "can only be in box" + str(canBeIn[ch][0][0]) + ", " + \
#							 str(canBeIn[ch][0][1] )
						self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues = []
						self.puzzleCells[canBeIn[ch][0][0]][canBeIn[ch][0][1]].possibleValues.append(ch)
						if canBeIn[ch][0] not in self.newlyPatchedValues :
							self.newlyPatchedValues.append(canBeIn[ch][0])

	def puzzleRowPossibleValues(self, row) :
		returnList = []
		for j in xrange(9) :
			if len (self.puzzleCells[row][j].possibleValues) == 1 :
				returnList.append(self.puzzleCells[row][j].possibleValues[0])
		return returnList

	def puzzleColPossibleValues(self, col) :
		returnList = []
		for i in xrange(9) :
			if len (self.puzzleCells[i][col].possibleValues) == 1 :
				returnList.append(self.puzzleCells[i][col].possibleValues[0])
		return returnList

# Need to implement the following. Did not see the need so far. but will have 
# to do.

	def generatePossibleValues(self) :
		self.newlyPatchedValues  = []
		self.twoChoices = []
		self.patched  = False
		for i in xrange(self.rowIndex) :
			for j in xrange(self.colIndex) :
				if self.puzzleCells[i][j].value == 'x' :
					fullRow = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
					fullCol = self.dropDuplicates(fullRow, self.puzzleRow(i))
					fullBox = self.dropDuplicates(fullCol, self.puzzleColumn(j))
#					self.puzzleCells[i][j].possibleValues = self.dropDuplicates(fullBox, self.puzzleBox(i,j))
					temp1 = self.dropDuplicates(fullBox, self.puzzleBox(i,j))
					temp2 = self.dropDuplicates(temp1, self.puzzleRowPossibleValues(i))
					self.puzzleCells[i][j].possibleValues = self.dropDuplicates(temp2, self.puzzleColPossibleValues(j))
					if len(self.puzzleCells[i][j].possibleValues) == 0 :
						print "contradiction: i: " + str(i) + " j: " + str(j) + "\n";
						return False #contradiction
					elif len(self.puzzleCells[i][j].possibleValues) == 1 :
						self.newlyPatchedValues.append([i,j])
					elif len(self.puzzleCells[i][j].possibleValues) == 2 :
						self.twoChoices.append([i,j])

		return True

	def applyNewValues(self) :
		for i in xrange(len(self.newlyPatchedValues)) :
			row = self.newlyPatchedValues[i][0]
			col = self.newlyPatchedValues[i][1]
			self.patched = True
			self.puzzleCells[row][col].value = \
				self.puzzleCells[row][col].possibleValues[0]
			self.puzzleCells[row][col].possibleValues = []

	def done(self) :
		for i in range(self.rowIndex) :
			for j in range (self.colIndex) :
				if self.puzzleCells[i][j].value == 'x' :
					print "done: return False"
					return False
		print "done: return True"
		return True

	def copy(self, newPuzzle) :
		newPuzzle.rowIndex = self.rowIndex
		newPuzzle.colIndex = self.colIndex
		for i in range(self.rowIndex) :
			newPuzzle.puzzleCells.append([])
			for j in range(self.colIndex) :
				newPuzzle.puzzleCells[i].append(PuzzleCell(self.puzzleCells[i][j].value))
				self.puzzleCells[i][j].copy(newPuzzle.puzzleCells[i][j])
		for i in range(len(self.newlyPatchedValues)) :
			newPuzzle.newlyPatchedValues.append(self.newlyPatchedValues[i])
		for i in range(len(self.twoChoices)) :
			newPuzzle.twoChoices.append(self.twoChoices[i])
		newPuzzle.twoChoicesIndex = self.twoChoicesIndex
#		 for i in range(len(self.threeChoices)) :
#			 newPuzzle.threeChoices.append(self.threeChoices[i])
#		 newPuzzle.threeChoicesIndex = self.threeChoicesIndex
		newPuzzle.patched = self.patched

	def tryOneOfTwoChoices(self, idx) :
		if len(self.twoChoices) == 0 :
			return False

		#check for the value here being sane
		row = self.twoChoices[self.twoChoicesIndex][0]
		col = self.twoChoices[self.twoChoicesIndex][1]
		self.puzzleCells[row][col].value = self.puzzleCells[row][col]\
			.possibleValues[idx]
		self.puzzleCells[row][col].possibleValues = []

	def tryTheNextTwoChoice(self) :
		self.twoChoicesIndex +=1

####################### END CLASS Puzzle ############################
def doTheObvious(puzzle) :
	i = 0;
	while True :
		i += 1;
		if puzzle.generatePossibleValues() == False :
			return False
		puzzle.findCellsWithUniqueNumbersInARow()
		puzzle.findCellsWithUniqueNumbersInAColumn()
		puzzle.findCellsWithUniqueNumbersInABox()
		puzzle.applyNewValues()
		if puzzle.patched == False :
			return True # end of the road
   
def solve(puzzle) :
	global recursionLevel
	recursionLevel += 1
	print "Recursion Level = " + str(recursionLevel)
	if	puzzle.done() == False :
		if doTheObvious(puzzle) == False : #contradiction
			print "Contradiction! Need to back up a level and take a different path!"
			recursionLevel -= 1
			return False
		print "After doing the obvious: "
		puzzle.printPuzzle(recursionLevel)
		#puzzle.printPuzzleDebug()

		anotherPuzzle = Puzzle()
		puzzle.copy(anotherPuzzle)
		anotherPuzzle.tryOneOfTwoChoices(0)
		print "Trying one of two choices: " + str(recursionLevel)

		if solve(anotherPuzzle) == False : #contradiction
			anotherPuzzle.reset()
			puzzle.copy(anotherPuzzle)
			anotherPuzzle.tryOneOfTwoChoices(1)
			#anotherPuzzle.tryTheNextTwoChoice()
			print "Trying second of two choices: " + str(recursionLevel)
			anotherPuzzle.printPuzzle(recursionLevel)
			if (solve(anotherPuzzle) == False) :
				print ("The second choice resulted in a contradiction. Backtracking!\n")
				recursionLevel -= 1
				return False;
			elif anotherPuzzle.done() == False : #inconclusive
				print ("The second choice was inconclusive. Will try the next 2 choice\n")
				anotherPuzzle.tryTheNextTwoChoice()
				solve(anotherPuzzle)
		elif anotherPuzzle.done() == False : #inconclusive
			print ("The first choice was inconclusive. Will try the next 2 choice\n")
			anotherPuzzle.tryTheNextTwoChoice()
			solve(anotherPuzzle)
		   
	recursionLevel -= 1
	return True;

	   

		 
	   

recursionLevel = 0
puzzle = Puzzle()
puzzle.loadFile("puzzle.txt")
solve(puzzle)
sys.exit("I am Done!")
