
#Fill empty deck
def initializeDeck():
    iDeck=[
        ["Movement",0],["Movement",1],["Movement",2],["Movement",3],["Movement",4],
        ["Location",0],["Location",1],["Location",2],["Location",3],["Location",4],
        ["Success",0],["Success",1],["Success",2],["Success",3],["Success",4],
        ["Failure",0],["Failure",1],["Failure",2],["Failure",3],["Failure",4]
        ]
        
    return iDeck
        

#Check for cards already in players hands
def refreshDeck(cDeck,pHand):
    for x in pHand:
        if x in cDeck:
            cDeck.remove(x)
        
            
    return cDeck
    