#SquareClicker
from tkinter import ttk
from tkinter import *
from datetime import datetime
import random
import os

class GameWindow(ttk.Frame):
    ''' Is the game window to play SquareClicker. '''
    def __init__(self):
        ''' GameWindow() -> obj GameWindow
Creates a window to play SquareClicker in. '''
        #Basic window initialization
        ttk.Frame.__init__(self)
        self.grid()
        self.master.title('SquareClicker')
        self.master.resizable(0, 0)

        #Set constants
        self.SAVE_FILE_NAME = 'square_clicker_save_file.sav'
        self.UPGRADES_FILE_NAME = 'square_clicker_upgrades.data'
        self.SQUARE_COLORS = {'basic': 'red', 'camouflage': '#959595', 'multi': 'blue', 'moving': 'yellow', 'teleporting': 'green'}
        self.MAX_UNLOCKS = {'basic': 5, 'camouflage': 3, 'multi': 3, 'moving': 3, 'teleporting': 2}
        self.DEFAULT_SQUARE_COLOR = 'dark gray'
        self.SQUARE_TYPES = ('basic', 'camouflage', 'multi', 'moving', 'teleporting')
        self.VALUE_COST_RATIO = 1.3
        self.VALUE_INITIAL_COSTS = {'basic': 5, 'camouflage': 25, 'multi': 150, 'moving': 2000, 'teleporting': 15000}
        self.VALUE_BOOST_RATIO = 1.1
        self.NUMBER_SUFFIXES = ('', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S', 'O', 'N', 'D', 'U')
        self.RESET_TIMER_START = 3
        #Squares to click in the grid
        self.SQUARE_GRID_HEIGHT = 12
        self.SQUARE_GRID_WIDTH = 12
        self.SQUARE_SIZE = 30

        #Initialize file (replace with load save later)
        self.protocolVersion = 1
        self.loadSave()

        #GUI at bottom
        self.moneyLabel = ttk.Label(self, text = 'Money: ' + str(int(self.money)))
        self.moneyLabel.grid(row = 1, column = 0)
        self.infoLabel = ttk.Label(self, text = '', wraplength = self.SQUARE_GRID_WIDTH * self.SQUARE_SIZE)
        self.infoLabel.grid(row = 2, column = 0)
        
        #Tab control stuff
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row = 0, column = 0)
        self.tabs.bind('<<NotebookTabChanged>>', self.update)
        #Squares to click
        self.squarePage = ttk.Frame(self.tabs)
        self.tabs.add(self.squarePage, text = 'Squares.')
        self.squares = {}
        for row in range(self.SQUARE_GRID_HEIGHT):
            for column in range(self.SQUARE_GRID_WIDTH):
                self.squares[(row, column)] = Canvas(self.squarePage,\
                                                     width = self.SQUARE_SIZE,\
                                                     height = self.SQUARE_SIZE,\
                                                     bg = self.DEFAULT_SQUARE_COLOR)
                self.squares[(row, column)].grid(row = row, column = column)
                self.squares[(row, column)].bind('<Button-1>',\
                                                 lambda dummy, pos = (row, column): self.squareClick(pos[0], pos[1]))
        #Upgrades page
        self.upgradesPage = ttk.Frame(self.tabs)
        self.tabs.add(self.upgradesPage, text = 'Upgradues')
        #A fancy box to hold the upgrades
        self.upgradesBox = ttk.Labelframe(self.upgradesPage, text = 'Research')
        self.upgradesBox.grid(row = 0, column = 0)
        self.upgradeSquares = {}
        for row in range(2):
            for column in range(self.SQUARE_GRID_WIDTH):
                self.upgradeSquares[(row, column)] = Canvas(self.upgradesBox,\
                                                            width = self.SQUARE_SIZE,\
                                                            height = self.SQUARE_SIZE,\
                                                            bg = self.DEFAULT_SQUARE_COLOR)
                self.upgradeSquares[(row, column)].grid(row = row, column = column)
                self.upgradeSquares[(row, column)].bind('<Button-1>',\
                                                 lambda dummy, pos = (row, column): self.upgradeClick(pos[0], pos[1]))
                self.upgradeSquares[(row, column)].bind('<Enter>',\
                                                        lambda dummy, pos = (row, column): self.upgradeMouseEvent(pos[0], pos[1], 'enter'))
                self.upgradeSquares[(row, column)].bind('<Leave>',\
                                                        lambda dummy, pos = (row, column): self.upgradeMouseEvent(pos[0], pos[1], 'leave'))
        #Upgrade info stuff
        self.upgradeName = ttk.Label(self.upgradesPage, text = '', wraplength = self.SQUARE_GRID_WIDTH * self.SQUARE_SIZE)
        self.upgradeName.grid(row = 1, column = 0)
        self.upgradeCost = ttk.Label(self.upgradesPage, text = '', wraplength = self.SQUARE_GRID_WIDTH * self.SQUARE_SIZE)
        self.upgradeCost.grid(row = 2, column = 0)
        self.upgradeDescription = ttk.Label(self.upgradesPage, text = '', wraplength = self.SQUARE_GRID_WIDTH * self.SQUARE_SIZE)
        self.upgradeDescription.grid(row = 3, column = 0)
        self.drawUpgrades()
        #Value Upgrades page
        self.valuePage = ttk.Frame(self.tabs)
        self.tabs.add(self.valuePage, text = 'Value City')
        self.valueTitle = ttk.Label(self.valuePage, text = 'Value Upgrades', font = ('TkDefaultFont', 18))
        self.valueTitle.grid(row = 0, column = 0, columnspan = 5)
        #Labels on top of rows
        self.valueSquareType = ttk.Label(self.valuePage, text = 'Square')
        self.valueSquareType.grid(row = 1, column = 0)
        self.valueCost = ttk.Label(self.valuePage, text = 'Cost')
        self.valueCost.grid(row = 1, column = 2)
        self.valueOldValue = ttk.Label(self.valuePage, text = 'Old value')
        self.valueOldValue.grid(row = 1, column = 3)
        self.valueNewValue = ttk.Label(self.valuePage, text = 'New value')
        self.valueNewValue.grid(row = 1, column = 4)
        self.valueLevel = ttk.Label(self.valuePage, text = 'Level')
        self.valueLevel.grid(row = 1, column = 5)
        self.valueWidgets = {}
        for i in range(len(self.SQUARE_TYPES)):
            squareType = self.SQUARE_TYPES[i]
            self.valueWidgets[squareType] = []
            #Type of square
            self.valueWidgets[squareType].append(ttk.Label(self.valuePage,\
                                                           text = squareType.title()))
            #Upgrade button
            self.valueWidgets[squareType].append(Canvas(self.valuePage,\
                                                        width = self.SQUARE_SIZE,\
                                                        height = self.SQUARE_SIZE,\
                                                        bg = self.SQUARE_COLORS[squareType]))
            #Cost
            self.valueWidgets[squareType].append(ttk.Label(self.valuePage,\
                                                           text = str(self.VALUE_INITIAL_COSTS[squareType])))
            #Old value
            self.valueWidgets[squareType].append(ttk.Label(self.valuePage,\
                                                           text = str(self.squareWorth[squareType])))
            #New value
            self.valueWidgets[squareType].append(ttk.Label(self.valuePage,\
                                                           text = str(max(self.squareWorth[squareType] + 1, int(self.squareWorth[squareType] * self.VALUE_BOOST_RATIO)))))
            #Level
            self.valueWidgets[squareType].append(ttk.Label(self.valuePage,\
                                                           text = str(self.valueUpgrades[squareType])))
            self.valueWidgets[squareType][1].bind('<Button-1>', lambda dummy, squareType = squareType: self.increaseValue(squareType))
            for j in range(len(self.valueWidgets['basic'])):
                self.valueWidgets[squareType][j].grid(row = i + 2, column = j)
        self.updateValue()
        #Stats Page
        self.statsPage = ttk.Frame(self.tabs)
        self.tabs.add(self.statsPage, text = 'AP Statistics')
        self.totalMoneyLabel = ttk.Label(self.statsPage, text = 'Total Monies: ' + str(self.totalMoney))
        self.totalMoneyLabel.grid(row = 0, column = 0)
        self.clicksBox = ttk.Labelframe(self.statsPage, text = 'Clicks')
        self.clicksBox.grid(row = 1, column = 0)
        self.clicksTypeTitle = ttk.Label(self.clicksBox, text = 'Square')
        self.clicksTypeTitle.grid(row = 0, column = 0, columnspan = 2)
        self.clicksNumTitle = ttk.Label(self.clicksBox, text = '# of Clicks')
        self.clicksNumTitle.grid(row = 0, column = 2)
        self.clicksWidgets = {}
        for i in range(len(self.SQUARE_TYPES)):
            squareType = self.SQUARE_TYPES[i]
            self.clicksWidgets[squareType] = []
            self.clicksWidgets[squareType].append(ttk.Label(self.clicksBox,\
                                                            text = squareType.title()))
            self.clicksWidgets[squareType].append(Canvas(self.clicksBox,\
                                                        width = self.SQUARE_SIZE,\
                                                        height = self.SQUARE_SIZE,\
                                                        bg = self.SQUARE_COLORS[squareType]))
            self.clicksWidgets[squareType].append(ttk.Label(self.clicksBox,\
                                                            text = str(self.clicks[squareType])))
            for j in range(3):
                self.clicksWidgets[squareType][j].grid(row = i + 1, column = j)
        self.totalClicksLabel = ttk.Label(self.clicksBox, text = 'Total')
        self.totalClicksLabel.grid(row = len(self.SQUARE_TYPES) + 1, column = 0, columnspan = 2)
        self.totalClicksNum = ttk.Label(self.clicksBox, text = str(sum(self.clicks[squareType] for squareType in self.SQUARE_TYPES)))
        self.totalClicksNum.grid(row = len(self.SQUARE_TYPES) + 1, column = 2)
        #Settings page
        self.settingsPage = ttk.Frame(self.tabs)
        self.tabs.add(self.settingsPage, text = '$ettings')
        self.resetButton = ttk.Button(self.settingsPage, text = 'RESET')
        self.resetButton.grid(row = 0, column = 0)
        self.resetButton.bind('<ButtonPress-1>', self.startReset)
        self.resetButton.bind('<ButtonRelease-1>', self.endReset)
        self.resetting = False
        self.resetTimer = self.RESET_TIMER_START

        #Actual game stuff
        self.squareLocations = {}
        for squareType in self.SQUARE_TYPES:
            for i in range(self.unlockedSquares[squareType]):
                #Generate intial square positions
                self.squareLocations[squareType + '_' + str(i)] = random.choice(self.getEmptySquares())
        self.multiSquareHealth = {}
        for i in range(self.MAX_UNLOCKS['multi']):
            self.multiSquareHealth['multi_' + str(i)] = self.multiSquareDefaultHealth
        self.update()
        self.moveMovingSquares()
        self.moveTeleportingSquares()

        #Save upon closing
        self.master.protocol('WM_DELETE_WINDOW', self.saveAndClose)

    #Save/load file stuff
    def loadSave(self):
        ''' GameWindow.loadSave()
Tries to load the save file that should be in the same folder.
If it isn't there, starts a new game with a fresh save file. '''
        try:
            gameFile = open(self.SAVE_FILE_NAME, 'r')
            saveData = gameFile.read().split('\n')
            version = int(saveData[0].split('|&|')[-1])
            if version == 1:
                for line in saveData[1:]:
                    line = line.split('|&|')
                    header = line[0]
                    data = line[1]
                    if header == 'Unlocked squares':
                        self.unlockedSquares = eval(data)
                    elif header == 'Square worth':
                        self.squareWorth = eval(data)
                    elif header == 'Money':
                        self.money = float(data)
                    elif header == 'Total money':
                        self.totalMoney = float(data)
                    elif header == 'Clicks':
                        self.clicks = eval(data)
                    elif header == 'Moving delay':
                        self.movingDelay = int(data)
                    elif header == 'Teleporting delay':
                        self.teleportingDelay = int(data)
                    elif header == 'Multi square health':
                        self.multiSquareDefaultHealth = int(data)
                    elif header == 'Multi click value':
                        self.multiClickValue = float(data)
                    elif header == 'Upgrades':
                        self.boughtUpgrades = eval(data)
                    elif header == 'Value upgrades':
                        self.valueUpgrades = eval(data)
                    else:
                        raise ValueError('Save file may be corrupted.')
        except FileNotFoundError:
            gameFile = open(self.SAVE_FILE_NAME, 'w') #Create the file
            self.newGame()
        except ValueError: #Restart the game if the file is blank
            if len(gameFile.read()) == 0:
                self.newGame()
        gameFile.close()
        self.loadUpgrades()

    def newGame(self):
        ''' GameWindow.newGame()
Starts a new game with fresh stats. '''
        #Start with default values
        self.unlockedSquares = {'basic': 1, 'camouflage': 0, 'multi': 0, 'moving': 0, 'teleporting': 0}
        self.squareWorth = {'basic': 1, 'camouflage': 25, 'multi': 70, 'moving': 900, 'teleporting': 10000}
        self.money = 0
        self.totalMoney = 0
        self.clicks = {'basic': 0, 'camouflage': 0, 'multi': 0, 'moving': 0, 'teleporting': 0}
        self.movingDelay = 350 #Delay before moving squares move (in milliseconds)
        self.teleportingDelay = 550 #Delay before teleporting squares move
        self.multiSquareDefaultHealth = 5 #Amount of clicks it takes to kill a multi square
        self.multiClickValue = 0 #Percentage of multi-square value awarded for all clicks, not just final ones
        self.boughtUpgrades = {}
        for ID in self.upgrades.keys():
            self.boughtUpgrades[ID] = False
        self.valueUpgrades = {}
        for squareType in self.SQUARE_TYPES:
            self.valueUpgrades[squareType] = 0

    def saveGame(self):
        ''' GameWindow.save()
Updates the save file, or creates a new one if it doesn't exist.
File format is:
Protocol version
Unlocked squares
Square worth
Money
Total money
Clicks on each type of square
Moving square delay
Teleporting square delay
Multi square health
Multi click value
Upgrades (separated by commas)
Square levels (value upgrades)

May add encryption later.
'''
        result = 'Protocol version|&|' + str(self.protocolVersion) + '\n'
        result += 'Unlocked squares|&|' + repr(self.unlockedSquares) + '\n'
        result += 'Square worth|&|' + repr(self.squareWorth) + '\n'
        result += 'Money|&|' + str(self.money) + '\n'
        result += 'Total money|&|' + str(self.totalMoney) + '\n'
        result += 'Clicks|&|' + repr(self.clicks) + '\n'
        result += 'Moving delay|&|' + str(self.movingDelay) + '\n'
        result += 'Teleporting delay|&|' + str(self.teleportingDelay) + '\n'
        result += 'Multi square health|&|' + str(self.multiSquareDefaultHealth) + '\n'
        result += 'Multi click value|&|' + str(self.multiClickValue) + '\n'
        result += 'Upgrades|&|' + repr(self.boughtUpgrades) + '\n'
        result += 'Value upgrades|&|' + repr(self.valueUpgrades)
        
        file = open(self.SAVE_FILE_NAME, 'w')
        file.write(result)
        file.close()

    def saveAndClose(self):
        ''' GameWindow.saveAndClose()
Saves the game in a save file, and then closes the window.
Pretty self-explanatory. '''
        self.saveGame()
        self.master.destroy()

    def loadUpgrades(self):
        ''' GameWindow.loadUpgrades()
Loads all the available upgrades from a file
and puts them into a convenient dictionary. '''
        #Open the upgrades file
        file = open(self.UPGRADES_FILE_NAME, 'r')
        upgradeFile = file.readlines()
        upgradeFile = [x.replace('\n', '') for x in upgradeFile] #Remove all trailing newlines
        upgradeFile = [x for x in upgradeFile if x] #Remove all blank lines
        upgradeFile = [x for x in upgradeFile if x[0] != '#'] #Remove all comments
        if '<end>' in upgradeFile:
            upgradeFile = upgradeFile[:upgradeFile.index('<end>')]
        #Parse the upgrade data
        self.upgrades = {}
        for i in range(0, len(upgradeFile), 7):
            NAME, ID, DEPENDENCIES, COST, DESCRIPTION, ACTION, AFFILIATION = (eval(x[x.index('=') + 1:]) for x in upgradeFile[i:i+7])
            self.upgrades[ID] = {'name': NAME, 'dependencies': DEPENDENCIES, 'cost': self.evalNumber(COST), 'description': DESCRIPTION, 'action': ACTION, 'affiliation': AFFILIATION}
            if not ID in self.boughtUpgrades.keys():
                self.boughtUpgrades[ID] = False
        file.close()

    def startReset(self, *args):
        ''' GameWindow.startReset()
Starts the 3-second countdown for resetting the game.
After 3 seconds, it resets the game.
The *args is to accept the event arguments from the event binding.'''
        self.resetting = True
        self.resetTimer = self.RESET_TIMER_START
        self.updateReset()

    def endReset(self, *args):
        ''' GameWindow.startReset()
Aborts the 3-second countdown for resetting the game.
The *args is to accept the event arguments from the event binding.'''
        self.resetting = False
        self.resetTimer = self.RESET_TIMER_START
        self.resetButton['text'] = 'RESET'

    def updateReset(self):
        ''' GameWindow.updateReset()
Decrements the counter, and actually resets when the counter hits 0. '''
        if self.resetting:
            if self.resetTimer <= 0:
                self.reset()
                self.resetButton['text'] = 'RESETTED'
            else:
                self.resetButton['text'] = str(self.resetTimer).ljust(4, '0')
                self.resetTimer -= 0.01
                self.resetTimer = round(self.resetTimer, 2)
                self.after(10, self.updateReset)

    def reset(self, *args):
        ''' GameWindow.reset()
Resets the game, permanently, and destroys the save file.
The *args is to accept the event arguments from the event binding. '''
        if os.path.isfile(self.SAVE_FILE_NAME):
            os.remove(self.SAVE_FILE_NAME)
        self.loadSave()
        self.update()
        
    #Game event handlers
    def squareClick(self, row, column):
        ''' GameWindow.squareClick(row, column)
Handles the event of the square at position (row, column)
being clicked by the player. '''
        for squareType in self.unlockedSquares.keys():
            for i in range(self.unlockedSquares[squareType]):
                squareName = squareType + '_' + str(i)
                if self.squareLocations[squareName] == (row, column):
                    squareType = squareName[:squareName.index('_')] #Get the type of square
                    if squareType == 'multi':
                        self.multiSquareHealth[squareName] -= 1
                        if self.multiSquareHealth[squareName] <= 0:
                            self.multiSquareHealth[squareName] = self.multiSquareDefaultHealth
                        else:
                            self.money += int(self.squareWorth['multi'] * self.multiClickValue/100)
                            continue
                    self.money += self.squareWorth[squareType]
                    self.totalMoney += self.squareWorth[squareType]
                    self.clicks[squareType] += 1
                    self.squareLocations[squareName] = random.choice(self.getEmptySquares()) #Teleport square to new spot
                    #Update the stuff (money + new square location)
        self.drawSquares()
        self.updateMoney()

    def upgradeClick(self, row, column):
        ''' GameWindow.upgradeClick(row, column)
Handles the player clicking one of the upgrade boxes. '''
        upgradeNumber = row * self.SQUARE_GRID_WIDTH + column
        ID = self.drawnUpgrades[upgradeNumber]
        price = self.upgrades[ID]['cost']
        if self.money >= price: #Check that the player has enough money
            self.money -= price
            self.makeUpgrade(self.upgrades[ID]['action'])
            self.boughtUpgrades[ID] = True
        self.update()

    def upgradeMouseEvent(self, row, column, event):
        ''' GameWindow.upgradeMouseEvent(row, column, event)
Displays and/or hides the info for upgrades when the user
mouses over the ugprade icon. '''
        if event == 'leave':
            self.upgradeName['text'] = ''
            self.upgradeCost['text'] = ''
            self.upgradeDescription['text'] = ''
        else:
            upgradeNumber = row * self.SQUARE_GRID_WIDTH + column
            if upgradeNumber < len(self.drawnUpgrades):
                ID = self.drawnUpgrades[upgradeNumber]
                self.upgradeName['text'] = self.upgrades[ID]['name']
                self.upgradeCost['text'] = self.dispNum(self.upgrades[ID]['cost'])
                self.upgradeDescription['text'] = self.upgrades[ID]['description']

    def increaseValue(self, squareType):
        ''' GameWindow.increaseValue(squareType)
Upgrades the value of a squareType square. '''
        price = int(self.VALUE_INITIAL_COSTS[squareType] * (self.VALUE_COST_RATIO ** self.valueUpgrades[squareType]))
        if self.money >= price:
            self.money -= price
            self.valueUpgrades[squareType] += 1
            self.squareWorth[squareType] = max(self.squareWorth[squareType] + 1, self.squareWorth[squareType] * self.VALUE_BOOST_RATIO)
            self.updateMoney()
            self.updateValue()

    def moveMovingSquares(self):
        ''' GameWindow.moveMovingSquares()
Causes the moving squares to move to another (adjacent) location. '''
        for i in range(self.unlockedSquares['moving']):
            empty = self.getEmptySquares()
            squareName = 'moving_' + str(i)
            position = self.squareLocations[squareName]
            possibilities = []
            for (rOffset, cOffset) in (position[0] - 1, position[1]),\
                (position[0] + 1, position[1]),\
                (position[0], position[1] - 1),\
                (position[0], position[1] + 1):
                if (0 <= rOffset <= self.SQUARE_GRID_HEIGHT) and\
                   (0 <= cOffset <= self.SQUARE_GRID_WIDTH) and\
                   (rOffset, cOffset) in empty:
                    possibilities.append((rOffset, cOffset))
            if possibilities: #Check that possiblities isn't empty
                self.squareLocations[squareName] = random.choice(possibilities)
        self.drawSquares() #Draw the squares in their new location
        self.after(self.movingDelay, self.moveMovingSquares) #Move again after a set amount of time

    def moveTeleportingSquares(self):
        ''' GameWindow.moveTeleportingSquares()
Causes the teleporting squares to teleport to another location. '''
        for i in range(self.unlockedSquares['teleporting']):
            #Go to a random empty square
            self.squareLocations['teleporting_' + str(i)] = random.choice(self.getEmptySquares())
        self.drawSquares() #Draw the squares in their new location
        self.after(self.teleportingDelay, self.moveTeleportingSquares) #Move again after a set amount of time

    #Utility functions
    def getEmptySquares(self):
        ''' GameWindow.getEmptySquares() -> list
Returns a list of all the empty squares in the grid. '''
        #Initialize the possibilities dictionary
        possibilities = {}
        for row in range(self.SQUARE_GRID_HEIGHT):
            for column in range(self.SQUARE_GRID_WIDTH):
                possibilities[(row, column)] = True
        #Set to false all the locations of the squares
        for squareType in self.unlockedSquares.keys():
            for i in range(self.unlockedSquares[squareType]):
                possibilities[self.squareLocations.get(squareType + '_' + str(i), None)] = False
        return [(r, c) for r in range(self.SQUARE_GRID_HEIGHT) for c in range(self.SQUARE_GRID_WIDTH) if possibilities[(r, c)]]

    def evalNumber(self, num):
        ''' GameWindow.evalNumber(num) -> int
Evaluates numbers in the form 10K or 2.25M into regular integers. '''
        try: #Check if number is regular integer
            num = int(num)
            return num
        except:
            #Split number into regular part ("10" or "2.25") and the suffix ("K" or "M")
            total = ''
            for i in range(len(num)):
                if num[i] in '0123456789.':
                    total += num[i]
                else:
                    suffix = num[i:]
                    break
            return int(float(total) * 1000**(self.NUMBER_SUFFIXES.index(suffix)))

    def dispNum(self, num, sigfigs = 3):
        ''' GameWindow.dispNum(num) -> str
Takes a big number, like 10000 or 2250000, and converts them with suffixes,
such as 10K or 2.25M. Gives [sigfigs] significant digits. '''
        num = int(num)
        suffix = (len(str(num)) - 1)//3
        prefix = num/1000**suffix
        sigfigsSoFar = 0
        total = ''
        for char in str(prefix):
            if char in '0123456789':
                sigfigsSoFar += 1
            total += char
            if sigfigsSoFar >= sigfigs:
                break
        #Remove trailing 0's because they're annoying
        if '.' in total:
            if set(total[total.index('.') + 1:]) == {'0'}:
                total = total[:total.index('.')]
        return total + self.NUMBER_SUFFIXES[suffix]

    def hasDependency(self, dependency):
        ''' GameWindow.hasDependency() -> bool
Returns whether or not a given dependency is satisfied.
Upgrades can require other upgrades, or a certain amount
or level of a certain type of square. '''
        dependency = dependency.lower().split('_')
        if dependency[0] == 'upgrade':
            return self.boughtUpgrades.get(int(dependency[1]), False)
        elif dependency[0] == 'level':
            if dependency[2] == 'all':#All square types have at least dependency[1] levels
                return min(self.valueUpgrades[squareType] for squareType in self.SQUARE_TYPES) >= int(dependency[1])
            elif dependency[2] == 'total': #All square types together have at least dependency[1] levels (there's a difference)
                return sum(self.valueUpgrades[squareType] for squareType in self.SQUARE_TYPES) >= int(dependency[1])
            return self.valueUpgrades[dependency[2]] >= int(dependency[1])
        elif dependency[0] == 'amount':
            if dependency[2] == 'all':
                return min(self.unlockedSquares[squareType] for squareType in self.SQUARE_TYPES) >= int(dependency[1])
            elif dependency[2] == 'total':
                return sum(self.unlockedSquares[squareType] for squareType in self.SQUARE_TYPES) >= int(dependency[1])
            return self.unlockedSquares[dependency[2]] >= int(dependency[1])
        else:
            return True

    def availableUpgrades(self):
        ''' GameWindow.availableUpgrades() -> list
Gets a list of the all unbought upgrades that are
currently available to the player. '''
        available = []
        for ID in self.upgrades.keys():
            if not self.boughtUpgrades[ID]:
                flag = True
                for d in self.upgrades[ID]['dependencies']:
                    if not self.hasDependency(d):
                        flag = False
                        break
                if not flag:
                    continue
                available.append(ID)
        return sorted(available, key = lambda ID: self.upgrades[ID]['cost'])

    def resetUpgrades(self):
        ''' GameWindow.resetUpgrades()
Resets the upgrade screen. '''
        for row in range(2):
            for column in range(self.SQUARE_GRID_WIDTH):
                self.upgradeSquares[(row, column)]['highlightbackground'] = '#f0f0ed'
                self.upgradeSquares[(row, column)]['bg'] = '#f0f0ed'
        self.upgradeName['text'] = ''
        self.upgradeCost['text'] = ''
        self.upgradeDescription['text'] = ''

    def drawUpgrades(self):
        ''' GameWindow.drawUprades()
Draws the upgrades with their appropriate colors in the upgrade screen. '''
        self.resetUpgrades()
        available = self.availableUpgrades()
        for i in range(min(len(available), 2 * self.SQUARE_GRID_WIDTH)):
            position = (i // self.SQUARE_GRID_WIDTH, i % self.SQUARE_GRID_WIDTH)
            self.upgradeSquares[position]['bg'] = self.SQUARE_COLORS.get(self.upgrades[available[i]]['affiliation'], '#f0f0ed')
            if self.upgrades[available[i]]['cost'] <= self.money:
                self.upgradeSquares[position]['highlightbackground'] = 'white'
            else:
                self.upgradeSquares[position]['highlightbackground'] = 'gray'
        self.drawnUpgrades = available[:min(len(available), 2 * self.SQUARE_GRID_WIDTH)]

    def makeUpgrade(self, upgrade):
        ''' GameWindow.makeUpgrade()
Applies the ACTION attribute of an upgrade. '''
        upgrade = upgrade.lower().split('_')
        if upgrade[0] == 'unlock':
            squareType = upgrade[1]
            #Generate intial square position
            self.squareLocations[squareType + '_' + str(self.unlockedSquares[squareType])] = random.choice(self.getEmptySquares())
            self.unlockedSquares[squareType] += 1
        elif upgrade[0] == 'value':
            target = upgrade[1]
            if upgrade[2] == 'times':
                if target == 'all':
                    for squareType in self.SQUARE_TYPES:
                        self.squareWorth[squareType] *= float(upgrade[3])
                else:
                    self.squareWorth[target] *= float(upgrade[3])
        elif upgrade[0] == 'clickvalue':
            if upgrade[1] == 'multi':
                self.multiClickValue = int(upgrade[2])

    #Graphic stuff
    def resetSquares(self):
        ''' GameWindow.resetSquares()
Resets the color of all square in the grid. '''
        for row in range(self.SQUARE_GRID_HEIGHT):
            for column in range(self.SQUARE_GRID_WIDTH):
                self.squares[(row, column)]['bg'] = self.DEFAULT_SQUARE_COLOR

    def resetValue(self):
        ''' GameWindow.resetValue()
Removes all widgets on the value upgrades page. '''
        for squareType in self.SQUARE_TYPES:
            for i in range(len(self.valueWidgets['basic'])):
                self.valueWidgets[squareType][i].grid_forget() #Remove the widget

    def resetStats(self):
        ''' GameWindow.resetStats()
Resets the #of clicks section of the statistics page. '''
        for squareType in self.SQUARE_TYPES:
            for i in range(len(self.clicksWidgets['basic'])):
                self.clicksWidgets[squareType][i].grid_forget()
                
    def drawSquare(self, squareType, row, column):
        ''' GameWindow.drawSquare(squareType, row, column)
Colors in a specific square in the given color. '''
        self.squares[(row, column)]['bg'] = self.SQUARE_COLORS[squareType]

    def drawSquares(self):
        ''' GameWindow.drawSquares()
Colors in all the squares in the grid. '''
        self.resetSquares()
        for squareType in self.unlockedSquares.keys():
            for i in range(self.unlockedSquares[squareType]):
                position = self.squareLocations[squareType + '_' + str(i)]
                self.drawSquare(squareType, position[0], position[1])

    def updateMoney(self):
        ''' GameWindow.updateMoney()
Updates the label displaying how much money the
player has, rounded down to the nearest unit. '''
        self.moneyLabel['text'] = 'Money: ' + self.dispNum(int(self.money))

    def updateValue(self):
        ''' GameWindow.updateValue()
Updates all the numbers on the value window. '''
        self.resetValue()
        for i in range(len(self.SQUARE_TYPES)):
            squareType = self.SQUARE_TYPES[i]
            if self.unlockedSquares[squareType]:
                for j in range(len(self.valueWidgets['basic'])):
                    self.valueWidgets[squareType][j].grid(row = i + 2, column = j)
                self.valueWidgets[squareType][2]['text'] = self.dispNum(int(self.VALUE_INITIAL_COSTS[squareType] * (self.VALUE_COST_RATIO ** self.valueUpgrades[squareType])))
                self.valueWidgets[squareType][3]['text'] = self.dispNum(self.squareWorth[squareType])
                self.valueWidgets[squareType][4]['text'] = self.dispNum(max(self.squareWorth[squareType] + 1, int(self.squareWorth[squareType] * self.VALUE_BOOST_RATIO)))

    def updateStats(self):
        ''' GameWindow.updateStats()
Updates the numbers in the statistics window. '''
        self.totalMoneyLabel['text'] = 'Total Monies: ' + str(int(self.totalMoney))
        self.resetStats()
        for i in range(len(self.SQUARE_TYPES)):
            squareType = self.SQUARE_TYPES[i]
            if self.unlockedSquares[squareType]:
                for j in range(len(self.clicksWidgets['basic'])):
                    self.clicksWidgets[squareType][j].grid(row = i + 1, column = j)
                self.clicksWidgets[squareType][2]['text'] = self.dispNum(self.clicks[squareType])
        self.totalClicksNum['text'] = self.dispNum(sum(self.clicks[squareType] for squareType in self.SQUARE_TYPES))

    def update(self, dummy = None):
        ''' GameWindow.update(dummy)
General update function that updates the money counter,
the squares on the grid, and the upgrade squares, among others.
dummy is a dummy variable to take care of event input. '''
        self.updateMoney()
        self.drawSquares()
        self.drawUpgrades()
        self.updateValue()
        self.updateStats()

game = GameWindow()
game.mainloop()
