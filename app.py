# Conway's Game of Life
# Nathaniel Moodie
# Project Originally Created On: Aug. 31, 2025
# Most Recently Updated On: Sep. 4, 2025

import math
import pygame
import random

# The project's current version
version = 3

# Life states (whether a tile is alive or dead)
DEAD = 0
ALIVE = 1
gameState=DEAD

# Window dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

# Tile size and gameplay area setup
TILE_SIZE = 25
GAMEPLAY_AREA_LEFT_EDGE = 2*TILE_SIZE
GAMEPLAY_AREA_RIGHT_EDGE = WINDOW_WIDTH - GAMEPLAY_AREA_LEFT_EDGE
GAMEPLAY_AREA_TOP_EDGE = 2*TILE_SIZE
GAMEPLAY_AREA_BOTTOM_EDGE = WINDOW_HEIGHT - GAMEPLAY_AREA_TOP_EDGE
GAMEPLAY_WIDTH = GAMEPLAY_AREA_RIGHT_EDGE - GAMEPLAY_AREA_LEFT_EDGE
GAMEPLAY_HEIGHT = GAMEPLAY_AREA_BOTTOM_EDGE - GAMEPLAY_AREA_TOP_EDGE
TILE_PADDING = 2
ACTUAL_TILE_SIZE = TILE_SIZE - 2*TILE_PADDING
X_COUNT = GAMEPLAY_WIDTH // TILE_SIZE
Y_COUNT =  GAMEPLAY_HEIGHT // TILE_SIZE
TILE_COUNT = X_COUNT * Y_COUNT

# The length of life state memory
LIFE_STATE_MEMORY_LENGTH = 8

# Frames per second
FPS = 2

# Font size
FONT_SIZE = math.floor(0.6*TILE_SIZE)-1

# Colors
colorPalettes = (("black", "gold"), ("gold","black"), ("orange","blue"), ("black", "deepskyblue1"), ("darkslateblue", "yellow"))
colorPalette = random.choice(colorPalettes)
bgColor=colorPalette[0]
highlightColor=colorPalette[1]

# Generation of the simulation
gen=0

# Whether the left mouse button is being clicked
left_click = False

# Tile data: position, life states, # of living neighbors, etc. 
tilePositions = []
lifeStates = str(DEAD)*TILE_COUNT
previousLifeStates = []
livingNeighborCounts = str(0)*TILE_COUNT
possibleAliveNeighborIDs = []
initiallyAliveTiles = []

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Conway's Game of Life")
pygame.display.set_icon(pygame.image.load("assets/img/triforce.ico"))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", FONT_SIZE)

# font surfaces
title_surface = font.render(f"Conway's Game of Life v{version}", True, highlightColor) 
copyright_surface = font.render("Created: John Conway, 1970 ~ Recreated: Nathaniel Moodie, 2025", True, highlightColor)
click_prompt_surface = font.render("Click any tile to switch it", True, highlightColor)
start_prompt_surface = font.render("Hold SPACE to start game", True, highlightColor)
stop_prompt_surface = font.render("Hold ESC to end game", True, highlightColor)
generation_surface = font.render(f"Generation {gen}", True, highlightColor)
random_button_surface = font.render("Random", True, highlightColor)
clear_button_surface = font.render("Clear", True, highlightColor)

# audio setup
pygame.mixer.init()
hoverSFX = pygame.mixer.Sound("assets/sfx/hover.mp3")
addTileSFX = pygame.mixer.Sound("assets/sfx/leftClick2.mp3")
deleteTileSFX = pygame.mixer.Sound("assets/sfx/rightClick.mp3")

# button rectangles
random_button_rect = pygame.Rect(WINDOW_WIDTH//2.05, 5, 
                                 round(TILE_SIZE*2.3), round(TILE_SIZE*0.9))
clear_button_rect = pygame.Rect(WINDOW_WIDTH//1.6, 5, 
                                 round(TILE_SIZE*2.3), round(TILE_SIZE*0.9))

# Whether the game is running or not
running=True


def length_of_int(n:int):

    if n==0:

        # Return 0 to avoid error
        return 0
    
    # Calculates int length
    return math.floor(math.log10(n))+1


def set_screen():

    global lifeStates

    lifeStates = str(DEAD)*TILE_COUNT

    # Loops through every tile
    for n in range(0,TILE_COUNT):

        # Determines row and column based on index
        row = (n % X_COUNT) + 1
        column = (n // X_COUNT) + 1

        # Determines x and y position based on row and column number
        x = GAMEPLAY_AREA_LEFT_EDGE + (TILE_SIZE * row) - TILE_SIZE/2
        y = GAMEPLAY_AREA_TOP_EDGE + (TILE_SIZE * column) - TILE_SIZE/2

        # Append position to tile positions
        tilePositions.append(pygame.Vector2(x,y))

    # If n is alive 
    for tileID in initiallyAliveTiles:

        # Add ALIVE to lifestate 
        lifeStates = mutated_string(lifeStates, str(ALIVE), tileID)


def start_game():
    global gameState
    global gen
    global livingNeighborCounts
    
    # Empties lists to give a fresh start (making them relevant to this round)
    previousLifeStates.clear()
    initiallyAliveTiles.clear()

    # by default, every tile has 0 neighbours
    livingNeighborCounts = str(0)*TILE_COUNT
    
    # Loops through every tile
    for n in range(0,TILE_COUNT):
        
        # if current tile is alive
        if lifeStates[n] == str(ALIVE):

            # Adds current tile to list of initially alive tiles
            initiallyAliveTiles.append(n)

    # Sets gen to 0
    gen = 0

    # Starts the game
    gameState = ALIVE


def end_game():
    global gameState
    global lifeStates

    # Ends game
    gameState=DEAD

    # Clears tile positions and life states
    tilePositions.clear()
    lifeStates = str(DEAD)*TILE_COUNT

    # Re adjusts the screen
    set_screen()


def get_tile_at_mouse_pos():

    # Gets click pos
    x = click_pos[0]
    y = click_pos[1]

    # If the click pos is outside the gameplay area
    if (x < GAMEPLAY_AREA_LEFT_EDGE) or (x > GAMEPLAY_AREA_RIGHT_EDGE) or (y < GAMEPLAY_AREA_TOP_EDGE) or (y > GAMEPLAY_AREA_BOTTOM_EDGE):

        # Return void
        return -1

    # Calculate row and column from click pos x and y
    row = 1 + round((x - (GAMEPLAY_AREA_LEFT_EDGE + 0.5*TILE_SIZE)) / TILE_SIZE)
    column = 1 + round((y - (GAMEPLAY_AREA_TOP_EDGE + 0.5*TILE_SIZE)) / TILE_SIZE)
    
    # Calculates and returns tile id
    return row + X_COUNT*(column-1) - 1


def count_all_live_neighbors(altTileID):

    tileID = altTileID + 1

    global livingNeighborCounts

    # Clear all possible neighbor id list
    possibleAliveNeighborIDs.clear()

    # Sets the live neighbor count to 0
    livingNeighborCounts = mutated_string(livingNeighborCounts, "0", tileID-1)

    # 
    onFarLeft = (tileID%X_COUNT == 1)
    onFarRight = (tileID%X_COUNT == 0)
    onTopRow = tileID < (X_COUNT+1)
    onBottomRow = tileID > (TILE_COUNT-X_COUNT)

    # Determines locations of potential alive neighbors
    if not onFarLeft:
        possibleAliveNeighborIDs.append(tileID-1)
    if not onFarRight:
        possibleAliveNeighborIDs.append(tileID+1)
    if not onTopRow:
        possibleAliveNeighborIDs.append(tileID-X_COUNT)
    if not onBottomRow:
        possibleAliveNeighborIDs.append(tileID+X_COUNT)
    if (not onFarLeft) and (not onTopRow):
        possibleAliveNeighborIDs.append(tileID - X_COUNT - 1)
    if (not onFarRight) and (not onTopRow):
        possibleAliveNeighborIDs.append(tileID - X_COUNT + 1)
    if (not onFarLeft) and (not onBottomRow):
        possibleAliveNeighborIDs.append(tileID + X_COUNT - 1)
    if (not onFarRight) and (not onBottomRow):
        possibleAliveNeighborIDs.append(tileID + X_COUNT + 1)

    # Counts up alive neighbors  
    for n in range(0, len(possibleAliveNeighborIDs)):

        if lifeStates[possibleAliveNeighborIDs[n]-1] == str(ALIVE):

            # Increments living neighbor count for that specific tile
            livingNeighborCounts = mutated_string(livingNeighborCounts, str(int(livingNeighborCounts[tileID-1]) + 1), tileID-1)
        


def update_simulation():
    global gen
    global generation_surface
    global lifeStates

    # Adds current life state string to previous life state list
    previousLifeStates.append(lifeStates)

    # If the game's memory limit has been exceeded
    if len(previousLifeStates) > LIFE_STATE_MEMORY_LENGTH:

        # Delete the 1st item in the list
        del previousLifeStates[0]

    # Loops through every tile
    for n in range(0, TILE_COUNT):

        # Counts the amount of live neighbors each tile has  
        count_all_live_neighbors(n)

    # Loops through every tile
    for n in range(TILE_COUNT):
        
        # If a tile is dead
        if lifeStates[n] == str(DEAD):
            
            # If it has 3 living neighbors
            if int(livingNeighborCounts[n]) == 3:

                # Makes the tile alive
                lifeStates = mutated_string(lifeStates, str(ALIVE), n)
        
        else:
            # If a tile has less than 2 or more than 3 neighbors
            if (int(livingNeighborCounts[n]) > 3) or (int(livingNeighborCounts[n]) < 2):

                # Kills tile
                lifeStates = mutated_string(lifeStates, str(DEAD), n)
    
    # If every tile is dead OR the game is in the exact same state as up to LIFE_STATE_MEMORY_LENGTH gen's ago
    if (lifeStates.count(str(DEAD)) == len(lifeStates)) or \
        (len(previousLifeStates) == LIFE_STATE_MEMORY_LENGTH and previousLifeStates[LIFE_STATE_MEMORY_LENGTH-1] in previousLifeStates[0:LIFE_STATE_MEMORY_LENGTH-1]):

        # Ends game
        end_game()

    # Increments generation
    gen += 1

    # Updates generation text UI
    generation_surface = font.render(f"Generation {gen}", True, highlightColor)
    

def set_random_screen():
    global lifeStates

    # Loops through every tile
    for n in range(0, TILE_COUNT):

        # If the roll of a die from 1-9 is 1 or 8
        if random.randint(1,10) in (1,8):

            # Makes the cell alive
            lifeStates = mutated_string(lifeStates, str(ALIVE), n)

        else:
            # Makes the cell dead
            lifeStates = mutated_string(lifeStates, str(DEAD), n)


def point_in_rect(point, rect):

    # If the point is within the rectangle's boundaries
    if (rect.x <= point[0] <= rect.x + rect.width and 
        rect.y <= point[1] <= rect.y + rect.height):
        
        return True
    
    return False


def mutated_string(string:str, object:str, new_pos:int):

    # Convert the string to a list
    character_list = list(string)

    # Replaces the character at position x with the object
    character_list[new_pos] = object

    # Converts the new list to a string and returns it
    return "".join(character_list)


# Sets the screen
set_screen()


while running:

    # 
    left_click = False

    # poll for events
    for event in pygame.event.get():

        # If user clicked exit
        if event.type == pygame.QUIT:

            # Exits the game
            running = False

        # If the user clicked mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
                      
            # If user left clicked
            if event.button == 1:

                # Saves click pos
                click_pos = event.pos

                # If the user clicks the "Random" button
                if point_in_rect(click_pos, random_button_rect):

                    # Randomizes the life state of every tile
                    set_random_screen()

                # If the user clicks the "clear" button
                elif point_in_rect(click_pos, clear_button_rect):

                    # Clears the screen
                    lifeStates = str(DEAD)*TILE_COUNT

                # Broadcasts that the user has left clicked
                left_click = True

        # If the user moves their mouse
        elif event.type == pygame.MOUSEMOTION:

            # Retrieves the mouse's pos
            mouse_pos = pygame.mouse.get_pos()

    # draw the background
    screen.fill(bgColor)

    # RENDER YOUR GAME HERE

    # Gets all keys pressed
    keys = pygame.key.get_pressed()

    # If the game is dead (simulation not active)
    if gameState == DEAD:

        # If user holds down space
        if keys[pygame.K_SPACE]:

            # Starts the game
            start_game()

        # If user presses mouse
        if left_click and pygame.mouse.get_focused():
            
            # Finds tile ID based on mouse pos
            calculatedTileID = get_tile_at_mouse_pos()

            # If the calculated tile id isn't void (-1)
            if (calculatedTileID != -1):

                # Inverts the life state of the tile with given ID                
                lifeStates = mutated_string(lifeStates, str((int(lifeStates[calculatedTileID])+1) % 2), calculatedTileID)
                
                # If the tile is alive
                if lifeStates[calculatedTileID] == str(ALIVE):

                    # Plays tile addition sfx
                    addTileSFX.play()
                else:

                    # Plays tile deletion sfx
                    deleteTileSFX.play()

                # Delay
                pygame.time.delay(100)

        # Draws random button
        pygame.draw.rect(screen, highlightColor, random_button_rect,2)
        screen.blit(random_button_surface, (random_button_rect.x+5, random_button_rect.y+5))

        # Draws clear button
        pygame.draw.rect(screen, highlightColor, clear_button_rect,2)
        screen.blit(clear_button_surface, (clear_button_rect.x+5, clear_button_rect.y+5))
        
        # Writes text
        screen.blit(title_surface, (5, WINDOW_HEIGHT - 2*(FONT_SIZE) - 5))
        screen.blit(copyright_surface, (5, WINDOW_HEIGHT - FONT_SIZE - 5))
        screen.blit(click_prompt_surface, (5, 5))
        screen.blit(start_prompt_surface, (5, FONT_SIZE + 5))

    else:

        # If the user holds escape
        if keys[pygame.K_ESCAPE]:

            # Ends game
            end_game()

        else:

            # Updates the game
            update_simulation()

            # Writes exit prompt text
            screen.blit(stop_prompt_surface, (5,5))

            hoverSFX.play()


    # Loops through every tile
    for n in range(0,TILE_COUNT):

        # If the tile is alive
        if lifeStates[n]==str(ALIVE):
            
            # Retrieves the tile's position
            x = tilePositions[n].x
            y = tilePositions[n].y
        
            # Draws the tile
            pygame.draw.rect(screen,
                            highlightColor,
                            (x-ACTUAL_TILE_SIZE/2, y-ACTUAL_TILE_SIZE/2, ACTUAL_TILE_SIZE, ACTUAL_TILE_SIZE))

    # Draws a grid to house all the tiles
    for n in range(0,X_COUNT+1):

        # Draws vertical lines
        pygame.draw.rect(screen,
                        highlightColor,
                        (GAMEPLAY_AREA_LEFT_EDGE + TILE_SIZE*n - 1, GAMEPLAY_AREA_TOP_EDGE, 2, GAMEPLAY_HEIGHT))
    for n in range(0,Y_COUNT+1):
        
        # Draws horizontal lines
        pygame.draw.rect(screen,
                        highlightColor,
                        (GAMEPLAY_AREA_LEFT_EDGE, GAMEPLAY_AREA_TOP_EDGE + TILE_SIZE*n - 1, GAMEPLAY_WIDTH, 2))
    
    # Broadcasts the current generation
    screen.blit(generation_surface, (WINDOW_WIDTH - (FONT_SIZE/15)*(110 + 4*length_of_int(gen)),5))

    # Updates the display
    pygame.display.flip()

    # Defines FPS
    clock.tick(FPS)

# Ends the game
pygame.quit()
