import pygame

from initializeDeck import *
from deck import *


gameDeck=initializeDeck()
print(gameDeck)
print(gameDeck[1])

p1=player("Player1")
p2=player("Player2")
p1Status=True
p2Status=False

for i in range(3):
    p1.drawCard(gameDeck)
    print("Player1 hand",p1.hand)
print(gameDeck)
for i in range(3):
    p2.drawCard(gameDeck)
    print("Player2 hand",p2.hand)
print(gameDeck)


while len(gameDeck)>0:
    gameDeck.pop(0)
    print(gameDeck)


if len(gameDeck)==0:
    gameDeck=initializeDeck()
    gameDeck=refreshDeck(gameDeck,p1.hand)
    gameDeck=refreshDeck(gameDeck,p2.hand)

print(gameDeck)
    
pygame.init()

screen = pygame.display.set_mode((700, 600))
pygame.display.set_caption("Cards testing")

drawButton = pygame.Rect(50, 75, 150, 50)
font = pygame.font.SysFont(None, 30)

changePlayerButton = pygame.Rect(250, 75, 150, 50)
font = pygame.font.SysFont(None, 22)

running = True
while running:


    screen.fill((120, 17, 103))
    

    pygame.draw.rect(screen, (255, 255, 255), drawButton)
    text = font.render("Draw Card", True, (0, 0, 0))
    screen.blit(text, (drawButton.x + 20, drawButton.y + 12))

    pygame.draw.rect(screen, (255, 255, 255), changePlayerButton)
    text = font.render("Change Player", True, (0, 0, 0))
    screen.blit(text, (changePlayerButton.x + 20, changePlayerButton.y + 12))

    
    if p1Status:
        currentPlayer = p1
    else:
        currentPlayer = p2


    currentPlayer.displayHand(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if changePlayerButton.collidepoint(event.pos):
                p1Status = not p1Status
                p2Status = not p2Status
                
                if p1Status:   
                    print("switching 1")
                else:
                    print("Switching 2")
                    
       
        
                
            elif drawButton.collidepoint(event.pos):
                currentPlayer.drawCard(gameDeck)

            else:
                for i, rect in enumerate(currentPlayer.cardRect):
                    if rect.collidepoint(event.pos):
                        currentPlayer.playCard(i)
                        break
                    
        
      
    if len(gameDeck)==0:
        gameDeck=initializeDeck()
        gameDeck=refreshDeck(gameDeck,p1.hand)
        gameDeck=refreshDeck(gameDeck,p2.hand)



    pygame.display.flip()

pygame.quit()