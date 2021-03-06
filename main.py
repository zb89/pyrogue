#!/usr/bin/python3

import random

from game import *
from console import *
from message import *
from tile import *
from item import *
from monster import *
from world import *
from player import *

# ---- map functions ----
def draw_map():
  for x, col in enumerate(currentmap.grid):
    for y, cell in enumerate(col):
      if cell.color > 6:
        cons.setbold()
      cons.setcolor(cell.color)
      cons.add_char(x, y, cell.char)
      cons.unsetcolor(cell.color)
      cons.unsetbold()

def flood(tile):
  currentmap.grid = [[ tile
    for y in range(currentmap.height) ]
      for x in range(currentmap.width) ]

def add_tile(tile, x, y):
  currentmap.grid[x][y] = tile

def spray(tile, n):
  for x in range(n):
    rx = random.randint(0, currentmap.width - 1)
    ry = random.randint(0, currentmap.height - 1)
    add_tile(tile, rx, ry)

def rect(tile, startx, starty, width, height):
  for x in range(startx, startx + width):
    for y in range(starty, starty + height):
      add_tile(tile, x, y)

def room(startx, starty, width, height):
  rect(tile_grass, startx - 1, starty - 1, width + 3, height + 3) # make accessible
  rect(tile_floor, startx, starty, width, height)                 # floor
  rect(tile_wall, startx, starty, width, 1)                       # top
  rect(tile_wall, startx, starty + height, width + 1, 1)          # bottom
  rect(tile_wall, startx, starty, 1, height)                      # left
  rect(tile_wall, startx + width, starty, 1, height)              # right
  add_tile(tile_door, startx + int(width / 2), starty + height)    # door
# ---- end map functions ----

# ---- message box functions ----
def draw_msgbox():
  if len(msgbox.messages) > (23 - currentmap.height):
    msgbox.messages.pop(0)
  for n, msg in enumerate(msgbox.messages):
    cons.add_str(0, n + msgbox.y, msg)

def say(msg):
  msgbox.messages.append(msg)

# ---- item functions ----
def draw_items():
  for i in currentmap.items:
    if i.color > 6:
      cons.setbold()
    cons.setcolor(i.color)
    cons.add_char(i.x, i.y, i.char)
    cons.unsetcolor(i.color)
    cons.unsetbold()
    
def check_items():
  for i in currentmap.items:
    if i.x == player.x and i.y == player.y:
      say("There is a " + i.name + " here.")
    
def add_item(x, y, item):
  currentmap.items.append(item)
  item.x = x
  item.y = y
  
# ---- player functions ----
def draw_player():
  if player.x in range(currentmap.width):
    if player.y in range(currentmap.height):
      if player.color > 6:
        cons.setbold()
      cons.setcolor(player.color)
      cons.add_char(player.x, player.y, player.char)
      cons.unsetcolor(player.color)
      cons.unsetbold()

def move_player(dx, dy):
  newx = player.x + dx
  newy = player.y + dy
  # check if coordinates are in bounds
  if newx in range(currentmap.width):
    if newy in range(currentmap.height):
      # check if coordinates are passable
      if currentmap.getchar(newx, newy) in ['.', '\\']:
        # set new player position
        player.x = newx
        player.y = newy
        # list items on floor (if any)
        check_items()
        # move action successful
        return 0
      # open door (if any)
      if currentmap.getchar(newx, newy) == '+':
        add_tile(tile_opendoor, newx, newy)
        say("You open the door.")
        # opening a door counts as a move
        return 0
  else:
    # move action failed
    return 1

def close_door():
  left = player.x - 1
  right = player.x + 1
  up = player.y - 1
  down = player.y + 1
  
  # close door if adjacent to player
  if currentmap.getchar(player.x, up)      == '\\':  # up
    add_tile(tile_door, player.x, up)
    return 0
  elif currentmap.getchar(player.x, down)  == '\\':  # down
    add_tile(tile_door, player.x, down)
    return 0
  elif currentmap.getchar(right, player.y) == '\\':  # right
    add_tile(tile_door, right, player.y)
    return 0
  elif currentmap.getchar(left, player.y)  == '\\':  # left
    add_tile(tile_door, left, player.y)
    return 0
  else:
    # close action failed
    return 1
    
def get_item():
  for i in currentmap.items:
    if i.x == player.x and i.y == player.y:
      player.inv.append(i)
      currentmap.items.remove(i)
      return 0
    else:
      return 1
    
def get_input():
  key = getch()
  if   key == ord('q'):         # quit
    game.end = True
  elif key is ord('k'):         # up
    if move_player(0, -1) == 0:
      game.turn += 1
  elif key is ord('j'):         # down
    if move_player(0, 1) == 0:
      game.turn += 1
  elif key is ord('l'):         # right
    if move_player(1, 0) == 0:
      game.turn += 1
  elif key is ord('h'):         # left
    if move_player(-1, 0) == 0:
      game.turn += 1
  elif key is ord('c'):         # close door
    if close_door() == 0:
      say("You close the door.")
      game.turn += 1
    else:
      say("There's nothing there to close.")
  elif key is ord(','):
    if get_item() == 0:
      say("Taken.")
      game.turn += 1
    else:
      say("There's nothing here.")
  else:
    say("Invalid command.")
# ---- end player functions ----
      
      
# ---- initalize everything ----

# init game engine 
cons = Console()
game = Game()
currentmap = World()

# init message window
msgbox = Message(0, currentmap.height + 1)

# init all map tiles in the game
tile_grass    = Tile('grass', '.', 3)
tile_dirt     = Tile('dirt',  '.', 2)
tile_tree     = Tile('tree',  'Y', 2)
tile_floor    = Tile('floor', '.', 0)
tile_wall     = Tile('wall',  '#', 0)
tile_door     = Tile('door',  '+', 2)
tile_opendoor = Tile('open door', '\\', 2)

# init all items
item_staff = Item('wooden staff', '|', 2)
item_sword = Item('iron sword', '/', 0)
item_bow   = Item('longbow', ')', 1)
item_book  = Item('spell book', '?', 6)
item_ring  = Item('gold ring', '=', 9)

# init all monsters
monster_zombie   = Monster('walking corpse', 'z', 11)
monster_imp      = Monster('lesser demon', '4', 8)
monster_demon    = Monster('greater demon', '3', 6)
monster_spider   = Monster('giant spider', 'X', 2)
monster_skeleton = Monster('walking skeleton', 'z', 7)
monster_thing    = Monster('abomination', '&', 13)

# init player
player   = Player('player', '@', 4)
player.x = 15
player.y = 10

# generate a map
flood(tile_grass)
spray(tile_tree, 16)
spray(tile_dirt, 64)
room(12, 4, 7, 4)

# add some items
add_item(15, 6, item_sword)
add_item(7, 9, item_ring)
add_item(30, 8, item_bow)

# print a message
say("Welcome to the game!")

# ---- end initialization ----

# ---- main game loop ----
while game.end == False:
  # clear the screen
  cons.clear()
  
  # render everything
  draw_map()
  draw_msgbox()
  draw_items()
  #draw_monsters()
  draw_player()
  
  # debug stuff
  cons.add_str(currentmap.width + 1, 0, "Turns: "    + str(game.turn))
  cons.add_str(currentmap.width + 1, 1, "Player X: " + str(player.x))
  cons.add_str(currentmap.width + 1, 2, "Player Y: " + str(player.y))
  
  # handle input
  get_input()

# ---- end main game loop ----

# close window
cons.close()
