
def initializeDeck():
    movement=[1,2,3,4,5]
    location=["Room1","Room2","Room3"]
    successItem=[["iName",1,"bonus",5]
                 ,["iName2",2,"bonus",4]
                 ,["iName3",3,"bonus",6]]
    failureItem=[["fText",3]
                 ,["fText2",4]
                 ,["fText3",2]]

    y=[movement,location,successItem,failureItem]
  
   #flattens subsections into single array
    deck = [x for row in y for x in row]

    return deck

def refreshDeck(cDeck,pHand):
    for x in pHand:
        if x in cDeck:
            cDeck.remove(x)
    print("Deck refreshed")
    return cDeck
    