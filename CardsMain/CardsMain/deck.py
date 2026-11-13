import random
import pygame

class player:
    def __init__(self,name):
        self.name=name
        self.hand=[]
        self.cardRect = []
        

    def drawCard(self,deck):
        if len(deck) >0:
            x=random.randint(0,len(deck)-1)
            self.hand.append(deck[x])
            deck.pop(x)
            print("Card Drawn")
        else :
            print("Deck is empty, cannot draw card.")

    def playCard(self,name):
        #name = index 
        #card = card text
        for i, card in enumerate(self.hand):
            if self.hand.index(card) == name:
                self.hand.remove(card)
            


    def displayHand(self, screen):
        self.cardRect = []

        for i, card in enumerate(self.hand):

            rect = pygame.Rect(40 + i * 150, 160, 120, 120)
            self.cardRect.append(rect)

            pygame.draw.rect(screen, (240, 240, 240), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

            font = pygame.font.SysFont(None, 24)
            text = font.render(str(card), True, (0, 0, 0))

            screen.blit(text, (rect.x + 10, rect.y + 20))