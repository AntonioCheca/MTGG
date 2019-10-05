# Author: Antonio Checa
# Script to collect data from data.csv about MtG cards and their basic properties (what they generate and what they benefit from) and creates a graph. Each node is a card and each edge means there is a synergy between that two cards, one generates what the other benefits from. It writes two gexf files, one with all the cards and other with a max clique Networkx finds in the graph. 

import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.approximation import clique
import csv

G = nx.Graph()

dict = {}
def rgbToColor(r, g, b):
    return {'color': {'r': r, 'g': g, 'b': b, 'a': 0}}

whiteColor = rgbToColor(255, 255, 255)
goldenColor = rgbToColor(255, 215, 0)
blueColor = rgbToColor(0, 191, 255)
redColor = rgbToColor(230, 0, 0)
greenColor = rgbToColor(50, 205, 50)
blackColor = rgbToColor(0,0,0)

# TODO: It would be best to have all the data of interactions in a csv file

# This dictionary has all the interaction between mechanics.
# For example, "DiscardOpp" places one or more card from your opponent's hand to the graveyard. So "DiscardOpp" implies "GraveyardOpp" as their graveyard makes bigger.
mechanicsInteractions = {}
mechanicsInteractions["DiscardOpp"] = ["GraveyardOpp", "LittleHandOpp"]
mechanicsInteractions["Discard"] = ["Graveyard", "LittleHand"]
mechanicsInteractions["DestroyCreature"] = ["GraveyardOpp"]
mechanicsInteractions["DestroyPlaneswalker"] = ["GraveyardOpp"]
mechanicsInteractions["DestroyArtifact"] = ["GraveyardOpp"]
mechanicsInteractions["DestroyEnchantment"] = ["GraveyardOpp"]
mechanicsInteractions["Damage"] = ["DamageCreature", "DamagePlaneswalker", "DamageOpp", "DestroyCreature", "DestroyPlaneswalker", "GraveyardOpp"]
mechanicsInteractions["Food"] = ["Artifact", "Token", "SacrificeArtifact"]
mechanicsInteractions["TokenCreature"] = ["Token", "Creature"]
mechanicsInteractions["SacrificeCreature"] = ["Graveyard"]
mechanicsInteractions["SacrificeCreatureOpp"] = ["GraveyardOpp"]

with open("data.csv", newline="") as csvfile:
    r = csv.reader(csvfile, delimiter=',', quotechar='\'')
    line = 0
    for card in r:
        if(line % 3 == 0):
            name = card[0]
            generate = card[2:]
            generate.append(name) # We need to add the name for cards like Seven Dwarves, Rowan's Stalwarts or Oko's Hospitality
            benefits = []
        elif(line % 3 == 1):
            generate.extend(card[1:])
        elif(line % 3 == 2):
            benefits.extend(card[1:])
            generate = [x for x in generate if x != '']
            for x in generate:
                if(x in mechanicsInteractions.keys()):
                    generate.extend(mechanicsInteractions[x])

            benefits = [x for x in benefits if x != '']
            if("White" in generate and "Creature" in generate):
                generate.append("WhiteCreature")
            G.add_node(name)
            if("Golden" in generate):
                G.node[name]['viz'] = goldenColor
                G.node[name]['colAtr'] = "Golden"
            elif("White" in generate):
                G.node[name]['viz'] = whiteColor
                G.node[name]['colAtr'] = "White"
            elif("Blue" in generate):
                G.node[name]['viz'] = blueColor
                G.node[name]['colAtr'] = "Blue"
            elif("Black" in generate):
                G.node[name]['viz'] = blackColor
                G.node[name]['colAtr'] = "Black"
            elif("Red" in generate):
                G.node[name]['viz'] = redColor
                G.node[name]['colAtr'] = "Red"
            elif("Green" in generate):
                G.node[name]['viz'] = greenColor
                G.node[name]['colAtr'] = "Green"
            dict[name] = [generate, benefits]

        line +=1


for x in dict:
    for y in dict:
        for b in dict[x][1]:
            l = b.split("&")
            cond_met = True
            for cond in l:
                if(cond[0] == "!"):
                    cond_met = cond_met and (not (cond[1:] in dict[y][0]))
                else:
                    cond_met = cond_met and (cond in dict[y][0])
            if(cond_met):
                G.add_edge(x,y)
                G.edges[x,y]['atr'] = b


# If you run this script, there will be two gexf files created in the folder you're working right now. If you don't want this to happen, comment this lines.

nx.write_gexf(G, "test.gexf")
h = clique.max_clique(G)
H = G.subgraph(h)
print(H.nodes)
nx.write_gexf(H, "clique.gexf")
