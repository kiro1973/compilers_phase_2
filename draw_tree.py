#import pygraphviz as pgv

dict={'exp': ['t', "exp'"], 't': ['f', "t'"], 'f': ['op', "f'"], 'op': ['Id'], "f'": ['cop', 'op1', "f'1"], 'cop': ['<'], 'op1': ['Id1'], "f'1": ['#'], "t'": ['#1'], "exp'": ['#2']}
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt
G = nx.DiGraph()

for key,value in dict.items():
    G.add_node(key)
    for v in value:
        G.add_node(v)
        G.add_edge(key,v)
"""
G.add_node("ROOT")

for i in range(5):
    G.add_node("Child_%i" % i)
    G.add_node("Child_%i" % i)
    G.add_node("Grandchild_%i" % i)
    G.add_node("Greatgrandchild_%i" % i)

    G.add_edge("ROOT", "Child_%i" % i)
    G.add_edge("Child_%i" % i, "Grandchild_%i" % i)
    G.add_edge("Grandchild_%i" % i, "Greatgrandchild_%i" % i)
"""
# write dot file to use with graphviz
# run "dot -Tpng test.dot >test.png"
write_dot(G,'test.dot')

# same layout using matplotlib with no labels
plt.title('draw_networkx')
pos =graphviz_layout(G, prog='dot')
nx.draw(G, pos, with_labels=True, arrows=True)
plt.savefig('nx_test.png')