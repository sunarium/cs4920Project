# Chess: The Gathering

import pygame
import time
import random
import threading
import os
#import testDraw

pygame.init()

gameFinishReg = 0
scoreReg = 1

white = (255, 255, 255)
black = (0, 0, 0)
red = (200, 0, 0)
light_red = (255, 0, 0)
green = (0, 155, 0)
light_green = (0, 255, 0)
blue = (0, 0, 255)
light_blue = (0, 0, 200)
yellow = (200, 200, 0)
light_yellow = (255,255,0)
goldenrod = (218,165,32)

display_width = 640
display_height = 480

game_name = 'Chess: The Gathering'

maxScore = 5

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption(game_name)

clock = pygame.time.Clock()

xsmallfont = pygame.font.SysFont("comicsansms", 15) #font size 25
smallfont = pygame.font.SysFont("comicsansms", 25) #font size 25
medfont = pygame.font.SysFont("comicsansms", 50) #font size 50
largefont = pygame.font.SysFont("comicsansms", 75) #font size 75

icon = pygame.image.load('../../assets/icon.png')
pygame.display.set_icon(icon)

tm_icon = pygame.image.load('../../assets/tm.png')

LEN_SPRT_X = 48
LEN_SPRT_Y = 48

FPS = 10

gameFinish = False
loadingImage = False

gameStarted = False

exitApp = False

highscoreName = []
highscoreScore = []
currentNumHighscore = 0

def text_objects(text, colour, size):
    if size == "small":
        textSurface = smallfont.render(text, True, colour)
    elif size == "medium":
        textSurface = medfont.render(text, True, colour)
    elif size == "large":
        textSurface = largefont.render(text, True, colour)
    elif size == "xsmall":
        textSurface = xsmallfont.render(text, True, colour)
        
    return textSurface, textSurface.get_rect()

def text_to_button(msg, colour, buttonx, buttony, buttonwidth, buttonheight, size = "small"):
    '''
    render text to the center of the button
    :param msg: text to be rendered
    :param colour:
    :param buttonx:
    :param buttony:
    :param buttonwidth:
    :param buttonheight:
    :param size:
    :return:
    '''
    textSurf, textRect = text_objects(msg, colour, size)
    textRect.center = ((buttonx+(buttonwidth/2)), buttony+(buttonheight/2))
    gameDisplay.blit(textSurf, textRect)

def message_to_screen(msg,colour, x_displace=0, y_displace=0, size = "small"):
    '''
    render text to current screen at coordinates
    :param msg: text need to be rendered
    :param colour: color of the text
    :param x_displace: coordinate, origin at center of the screen
    :param y_displace:
    :param size: size of the text
    :return: None
    '''
    textSurf, textRect = text_objects(msg, colour, size)
    textRect.center = (display_width/2) + x_displace, (display_height/2) + y_displace
    gameDisplay.blit(textSurf, textRect)

def message_to_screen_not_center(msg,colour, x_displace=0, y_displace=0, size = "small"):
    textSurf, textRect = text_objects(msg, colour, size)
    textRect.center = x_displace, y_displace
    gameDisplay.blit(textSurf, textRect)

def start_game_loop():
    print("Load game...")

# This function is to display the button helper (above each button if you want to add)
# Action (button ID / name) has to be unique
def button_helper(text, x, y, width, height, action = None):
    if action == "new":
        message_to_screen_not_center("Start a new game.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "local":
        message_to_screen_not_center("Start a local game.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "join":
        message_to_screen_not_center("Join an online game.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "credits":
        message_to_screen_not_center("Display credits.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "highscore":
        message_to_screen_not_center("Display highscore.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "controls":
        message_to_screen_not_center("Display controls.", red, x+width/2, y-height/2+10, "xsmall")
    elif action == "back":
        message_to_screen_not_center("Go back to main menu.", red, x+width/2, y-height/2+10, "xsmall")
        # sheet = pygame.image.load('C:\YOURFILE') #Load the sheet
    
# sheet.set_clip(pygame.Rect(SPRT_RECT_X, SPRT_RECT_Y, LEN_SPRT_X, LEN_SPRT_Y)) #Locate the sprite you want
# draw_me = sheet.subsurface(sheet.get_clip()) #Extract the sprite you want
#screen.blit(draw_me,backdrop) 

# display credits screen
def display_credits():
    display = True
    i = 0
    while display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(goldenrod)

        message_to_screen("Credits:",
                           black,
                           0,
                           -180 - (i),
                           "large")    
        
        message_to_screen("Developed by:",
                           black,
                           0,
                           -80 - (i),
                           "small")
                           
        message_to_screen("Henry",
                           black,
                           0,
                           -30 - (i),
                           "small")
                           
        message_to_screen("Josfer",
                           black,
                           0,
                           20 - (i),
                           "small")

        message_to_screen("Kevin",
                           black,
                           0,
                           70 - (i),
                           "small")

        message_to_screen("Georgia",
                           black,
                           0,
                           120 - (i),
                           "small")

        message_to_screen("Abbas",
                           black,
                           0,
                           170 - (i),
                           "small")

        
        
        message_to_screen("With thanks to:",
                           black,
                           0,
                           270 - (i),
                           "small")
            
        message_to_screen("Alfred",
                           black,
                           0,
                           320 - (i),
                           "small")
    
        message_to_screen("Tutorial Class",
                           black,
                           0,
                           370 - (i),
                           "small")
                           
        i += 5
        button("back", 480,400,110,50, red, light_red, action = "back")
        pygame.display.update()
        clock.tick(10)
        print(i)
        if i == 630:
            start_menu()

# Display control screen
def display_controls():
    display = True
    while display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(goldenrod)

        message_to_screen("Controls:",
                           black,
                           0,
                           -180,
                           "large")    
        
        message_to_screen("-> Click and drag chess pieces.",
                           black,
                           0,
                           -80,
                           "small")
                           
        message_to_screen("(whatever)",
                           black,
                           0,
                           20,
                           "small")
                           
        message_to_screen("(whatever)",
                           black,
                           0,
                           120,
                           "small")
        
        button("back", 480,400,110,50, red, light_red, action = "back")
        pygame.display.update()
        clock.tick(10)
        
def takeSecond(elem):
    return elem[1]

def checkScore(score):
    i = 0
    global currentNumHighscore
    print("currentNumHighScore = " + str(currentNumHighscore))

    if currentNumHighscore < maxScore:
        currentNumHighscore += 1
        highscoreScore.append(score)
    else:
        while i < len(highscoreScore): #assume highscoreScore is already sorted
            if score > highscoreScore[i]:
                
                return 1 #upon returning 1, enter name and save score
            i += 1

def retrieve_name(score):
    pass

def display_failHighscore():
    pass

def display_score(names):
    global gameFinish
    global highscoreName

    display = True

    array = []
    
    highscoreName.sort(reverse = False, key = takeSecond)
    
    while display:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
        gameDisplay.fill(goldenrod)
        message_to_screen("Highscore",
                           black,
                           0,
                           -170,
                           "medium")
                           
        message_to_screen("Player name",
                           black,
                           -150,
                           -90,
                           "small")
                           
        message_to_screen("Time taken",
                           black,
                           50,
                           -90,
                           "small")

        j = 0;
        for to_display in highscoreName:
            #print ("len of highscoreName = " + str(len(highscoreName)))
            #display name
            message_to_screen(str(to_display[0]),
                           black,
                           -150,
                           -50 + 60*(j),
                           "small")
            #display score               
            message_to_screen(str(to_display[1]) + " s",
                           black,
                           50,
                           -50 + 60*(j),
                           "small")
            j += 1
        
        button("back", 480,400,110,50, red, light_red, action = "back")

        pygame.display.update()
        clock.tick(10)

def start_menu():
    intro = True
    global gameFinish

    while intro:
        #gameDisplay.blit(background, (0,0))
        gameDisplay.fill(goldenrod)
        gameDisplay.blit(tm_icon,(560,85))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    intro = False
                if event.key == pygame.K_q:
                    quit_game()
    
        message_to_screen(game_name,
                           black,
                           0,
                           -120,
                           "medium")
        message_to_screen("The objective is to conquer opponent's King piece.",
                          green,
                          0,
                          -30)
        message_to_screen("(to add if needed).",
                          green,
                          0,
                          10)
        
        #This is how you create buttons
        button("new", 70,300,110,50, green, light_green, action = "new")
        button("local",270,300,110,50, yellow, light_yellow, action = "local")
        button("join", 470,300,110,50, red, light_red, action = "join")

        button("controls", 70,400,110,50, green, light_green, action = "controls")
        button("credits",270,400,110,50, yellow, light_yellow, action = "credits")
        button("highscore", 470,400,110,50, red, light_red, action = "highscore")
        
        if gameFinish == True:
            gameFinish = False
            score = 100 # testing
            #checkScore(score)
            retrieve_name(score)
        pygame.display.update()
        clock.tick(15)

def quit_game():
    global exitApp

    exitApp = True
    pygame.quit()
    quit()

# This is where you create buttons
# call all the required functions here for each buttons
def button(text, x, y, width, height, inactive_colour, active_colour, action = None):
    cur = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    global gameFinish
    global enemyButtonArray
    global gameStarted 

    if x + width >= cur[0] >= x and y + height >= cur[1] >= y:
        pygame.draw.rect(gameDisplay, active_colour, (x,y,width,height))
        if click[0] == 1 and action != None:

            if action == "new":
                print(action + " button is pressed")
                time.sleep(0.25)                
                display_new()

            elif action == "local":
                print (action + " button is pressed")
                time.sleep(0.25)                
                display_local()             

            elif action == "join":
                print (action + " button is pressed")
                time.sleep(0.25)                
                display_join()

            elif action == "highscore":
                print (action + " button is pressed")
                time.sleep(0.25)
                display_score(maxScore)
            
            elif action == "controls":
                print(action + " button is pressed")
                time.sleep(0.25)
                display_controls()
                #display_failHighscore()
            
            elif action == "credits":
                print(action + " button is pressed")
                time.sleep(0.25)
                display_credits()
                #to add
                #start_game_loop()

# TO DO HERE
# ADD BUTTONS here for the game and tie it to methods
# Below are examples
            #elif action == "enemy":
            #    print(action + " button is pressed")
            #    time.sleep(0.25)
            #    enemy_button(ENEMY_1) #the method


            elif action == "back":
                print(action + " button is pressed")
                time.sleep(0.25)
                gameFinish = False
                start_menu()

        button_helper(text, x, y, width, height, action)


    else:
        pygame.draw.rect(gameDisplay, inactive_colour, (x,y,width,height))

    text_to_button(text, black, x, y, width, height)
    
# new button screen
# DO STUFF HERE
def display_new():
    display = True
    while display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)
        
        #Insert code here to display the game / board etc

        message_to_screen("Insert game screen here",
                           black,
                           0,
                           -180,
                           "medium")    

        button("back", 480,400,110,50, red, light_red, action = "back")
        pygame.display.update()
        clock.tick(10)

# local button screen
# DO STUFF HERE
def display_local():
    display = True
    while display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)

        message_to_screen("Insert local screen here",
                           black,
                           0,
                           -180,
                           "medium")    

        
        button("back", 480,400,110,50, red, light_red, action = "back")
        pygame.display.update()
        clock.tick(10)


# join button screen
# DO STUFF HERE
def display_join(word = ""):

    display = True
    
    while display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    word = word[:-1]
                elif event.key == pygame.K_RETURN:
                    #save name
                    print ("enter is pressed")
                    loadingImage = True
                    print("IP address = " + str(word))
                    

                    #if correct IP address ==  True:
                    #   # do stuff with IP here
                    #
                    #else: #if wrong IP is entered, need to enter IP again
                    #    print("Incorrect IP address entered.")
                    #    message_to_screen("Incorrect IP address.",
                    #       red,
                    #       0,
                    #       -60,
                    #       "small")
                    #    pygame.display.update()
                    #    time.sleep(1.5)
                    #    display_join(word)

                    # call function here to insert IP
                    # function(word)

                    time.sleep(0.1)
                    # call function for back-end here (or above)
                elif event.unicode != " ":
                    word += event.unicode


        gameDisplay.fill(goldenrod)

        message_to_screen("Enter IP8 address:",
                           black,
                           0,
                           -180,
                           "medium")    

        #displaying IP8 address here
        message_to_screen(word,
                           black,
                           0,
                           0,
                           "small")
                           
        button("back", 480,400,110,50, red, light_red, action = "back")
        
        button("back", 480,400,110,50, red, light_red, action = "back")
        pygame.display.update()
        clock.tick(10)

start_menu()


