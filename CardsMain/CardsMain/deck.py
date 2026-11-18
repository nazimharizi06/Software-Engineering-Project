import random
import pygame
from movementCards import *
from locationCards import *
from successCards import *
from failureCards import *

class player:
    def __init__(self,name):
        self.name=name
        self.hand=[]
        self.cardRect = []
        self.cardHover = {}
      

    def drawCard(self,deck):
        if len(deck) >0:
            x=random.randint(0,len(deck)-1)
            self.hand.append(deck[x])
            print("Card Drawn",deck[x])
            deck.pop(x)
            print("Current Deck",deck)
        else:
            print("Deck is empty, cannot draw card.")


    def playCard(self,name):
        for i, card in enumerate(self.hand):
            if self.hand.index(card) == name:
                print("Playing",card)
                self.hand.remove(card)
            


    def displayHand(self, screen, cardDescBox, descFont):

        cWidth=120
        cHeight=150
        startX=40
        endX=750
        y=360
        
        #Card Spacing
        if len(self.hand) > 1:
            spacing = min(150, (endX - startX - cWidth) / (len(self.hand) - 1))
        else:
            spacing = 150

        fontSize = 30
        cardFont = pygame.font.Font("Assets/AmaticSC-Bold.ttf", fontSize)
        cardFont.set_bold(True)

      

        mousePos = pygame.mouse.get_pos()
        hoveredCard = -1

        #Check if cursor is over a card
        for i in range(len(self.hand) - 1, -1, -1):
            rect = pygame.Rect(startX + i * spacing, y, cWidth, cHeight)

            if rect.collidepoint(mousePos):
                hoveredCard = i
                break

        cardDesc = "No card selected"


        #Handles card display and cursor hover
        for i, card in enumerate(self.hand):
            if card[0]=="Movement":
                cImage=pygame.image.load("Assets/Mortenax.jpg").convert_alpha()
                cc=Movement(card[1])
                text = cardFont.render(str(cc[0]), True, (152, 255, 152))
                if i == hoveredCard:
                    cardDesc = "Test overflow of longer lines of test :" + str(cc[0]) +":" + str(cc[1])
         
            elif card[0]=="Location":
                cImage=pygame.image.load("Assets/Kafka.jpg").convert_alpha()
                cc=Location(card[1])
                text = cardFont.render(str(cc[0]), True, (152, 255, 152))
                if i == hoveredCard:
                    cardDesc = str(cc[0]) +":" + str(cc[1])
            
            elif card[0]=="Success":
                cImage=pygame.image.load("Assets/Firefly.jpg").convert_alpha()
                cc=Success(card[1])
                text = cardFont.render(str(cc[0]), True, (152, 255, 152))
                if i == hoveredCard:
                    cardDesc = str(cc[0]) +":" + str(cc[1])
            
            elif card[0]=="Failure":
                cImage=pygame.image.load("Assets/SilverWolf.jpg").convert_alpha()
                cc=Failure(card[1])
                text = cardFont.render(str(cc[0]), True, (152, 255, 152))
                if i == hoveredCard:
                    cardDesc = str(cc[0]) +":" + str(cc[1] + ":" + str(cc[2]))

            cImage = pygame.transform.scale(cImage, (cWidth, cHeight))
            rect = pygame.Rect(startX + i * spacing, y, cWidth, cHeight)
            self.cardRect.append(rect)

            #Set card hover amount 
            if i not in self.cardHover:
                self.cardHover[i] = y

            hoverAmt = y
            if i == hoveredCard:
                hoverAmt = y - 60
                

            #animate card position
            self.cardHover[i] += (hoverAmt - self.cardHover[i]) * 0.2

            rect.y = int(self.cardHover[i])

            
            screen.blit(cImage,rect)
            screen.blit(text, (rect.x + 10, rect.y + 40))
        #End of for loop


        pygame.draw.rect(screen, (255, 255, 255), cardDescBox)
        pygame.draw.rect(screen, (0, 0, 0), cardDescBox, 2)
        words = cardDesc.split()
        line = ""
        textY = cardDescBox.y + 10
        
        #Format card description text to fit in its area
        for word in words:
            fullLine = line + word + " "

            if descFont.size(fullLine)[0] > cardDescBox.width - 10:
                text = descFont.render(line, True, (0, 0, 0))
                screen.blit(text, (cardDescBox.x + 10, textY))
                line = word + " "
                textY += 25
            else:
                line = fullLine
                text = descFont.render(line, True, (0, 0, 0))
                screen.blit(text, (cardDescBox.x + 10, textY))
