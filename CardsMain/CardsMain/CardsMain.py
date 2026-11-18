import pygame

from initializeDeck import *
from deck import *

gameDeck=initializeDeck()
print(gameDeck)

#print("Testing",gameDeck[0][0])

p1=player("Player1")
p2=player("Player2")
p3=player("Player3")
p4=player("Player4")
playerTurn=1
maxPlayers=4
pCount=1; #Track if card has been played for refresh

#Initialize hand for players
for i in range(1):
    p1.drawCard(gameDeck)
    print("Player1 hand",p1.hand)
print(gameDeck)
for i in range(2):
    p2.drawCard(gameDeck)
    print("Player2 hand",p2.hand)
print(gameDeck)
for i in range(3):
    p3.drawCard(gameDeck)
    print("Player3 hand",p3.hand)
print(gameDeck)
for i in range(4):
    p4.drawCard(gameDeck)
    print("Player3 hand",p4.hand)
print(gameDeck)

#Empty current deck
while len(gameDeck)>0:
    gameDeck.pop(0)
    print(gameDeck)

#Refresh deck + check for already drawn cards
if len(gameDeck)==0:
    gameDeck=initializeDeck()
    gameDeck=refreshDeck(gameDeck,p1.hand)
    gameDeck=refreshDeck(gameDeck,p2.hand)
    gameDeck=refreshDeck(gameDeck,p3.hand)
    gameDeck=refreshDeck(gameDeck,p4.hand)

print(gameDeck)



#Pygame start    
pygame.init()

screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Cards testing")

#(x, y, width, height)
drawButton = pygame.Rect(50, 75, 150, 50)
drawFont = pygame.font.Font("Assets/AmaticSC-Bold.ttf", 30)

changePlayerButton = pygame.Rect(250, 75, 300, 50)
changePlayerFont = pygame.font.Font("Assets/AmaticSC-Bold.ttf", 27)

cardDescBox = pygame.Rect(125, 200, 150, 50)
cardDescFont = pygame.font.Font("Assets/AmaticSC-Bold.ttf", 25)

running = True
while running:

    screen.fill((120, 17, 103))
    
    #Display draw card button
    pygame.draw.rect(screen, (255, 255, 255), drawButton)
    pygame.draw.rect(screen, (0, 0, 0), drawButton, 2)
    text = drawFont.render("Draw Card", True, (0, 0, 0))
    screen.blit(text, (drawButton.x + 20, drawButton.y + 12))

    #Check current player
    if playerTurn==1:
        currentPlayer = p1
    elif playerTurn==2:
        currentPlayer = p2
    elif playerTurn==3: 
        currentPlayer = p3
    elif playerTurn==4:
        currentPlayer = p4


    #Display change player simulation button
    pygame.draw.rect(screen, (255, 255, 255), changePlayerButton)
    text = changePlayerFont.render("Change Player | Current: "+str(currentPlayer.name), True, (0, 0, 0))
    screen.blit(text, (changePlayerButton.x + 20, changePlayerButton.y + 12))

    

    #Display current players hand
    currentPlayer.displayHand(screen, cardDescBox, cardDescFont)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        #Handle player change
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if changePlayerButton.collidepoint(event.pos):
                playerTurn+=1
                
                if playerTurn>4:
                    playerTurn=1
                if playerTurn==1:   
                    print("switching to player 1")
                if playerTurn==2:
                    print("Switching to player 2")
                if playerTurn==3:
                    print("Switching to player 3")
                if playerTurn==4:
                    print("Switching to player 4")

                    
              
            #Handle card drawing and deck refresh
            elif drawButton.collidepoint(event.pos):
                if len(gameDeck)==0 and pCount>=1:
                    gameDeck=initializeDeck()
                    gameDeck=refreshDeck(gameDeck,p1.hand)
                    gameDeck=refreshDeck(gameDeck,p2.hand)
                    gameDeck=refreshDeck(gameDeck,p3.hand)
                    gameDeck=refreshDeck(gameDeck,p4.hand)


                    if len(gameDeck)>0:
                        print("Deck refreshed",gameDeck)
                        pCount=0
                    else:
                        print("All cards in players hands")
                        pCount=0
                currentPlayer.drawCard(gameDeck)
            
            #Handle card playing
            else:
                for i, rect in enumerate(currentPlayer.cardRect):
                    if rect.collidepoint(event.pos):
                        currentPlayer.playCard(i)
                        pCount+=1
                        break


    pygame.display.flip()

pygame.quit()