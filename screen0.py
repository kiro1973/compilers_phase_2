from cProfile import label
from cgitb import text
from pickle import DICT
from PIL import Image,ImageTk
from tkinter import *
from tkinter import ttk
import networkx as nx
import networkx as nx1
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt1
import re
import os
L=[]
rules=[]
nonterm_userdef=[]
term_userdef=[]
firsts = {}
follows = {}
diction = {}
start_symbol=None
rules1=[]
tree=[]
nodelist=[]
class node:
    def __init__(self,name):
        self.left=None
        self.right=None
        self.parent=None
        self.name=name
def traverse(list,parent,left_of_parent,right_of_parent):
    global nodelist
    arriveflag=0
    nod=None
    print("line 11")
    if len(list)==1:
        n=node(list[0])
        n.parent=parent
        n.left=None
        n.right=None
        if left_of_parent:
                parent.left=n
        elif right_of_parent:
                parent.right=n
        nodelist.append(n)
        print(list[0])
        return
    for i in range (len(list)) :
        if list[i]=="||":
            n=node("||")
            print("||")
            n.parent=parent
            arriveflag=1
            nod=n
            nodelist.append(n)
            traverse(list[:i],n,True,False)
            traverse(list[i+1:],n,False,True)
            if left_of_parent:
                parent.left=n
            elif right_of_parent:
                parent.right=n
            break
    i=0
    while i <len(list) and arriveflag==0:
        if list[i]=="&&":
            n=node("&&")
            print("&&")
            n.parent=parent
            arriveflag=1
            nod=n
            nodelist.append(n)
            traverse(list[:i],n,True,False)
            traverse(list[i+1:],n,False,True)
            if left_of_parent:
                parent.left=n
            elif right_of_parent:
                parent.right=n
        i+=1
    i=0
    while i <len(list) and arriveflag==0:
        if list[i]in ["<",">","="]:
            n=node(list[i])
            print(list[i])
            n.parent=parent
            arriveflag=1
            nod=n
            nodelist.append(n)
            traverse(list[:i],n,True,False)
            print(list[:i])
            traverse(list[i+1:],n,False,True)
            if left_of_parent:
                parent.left=n
            elif right_of_parent:
                parent.right=n
        i+=1
    i=0
    while i <len(list) and arriveflag==0:
        if list[i]=="!":
            n=node("!")
            n.parent=parent
            print("!")
            arriveflag=1
            nod=n
            nodelist.append(n)
            n.left=None
            #traverse(list[:i],n,True,False)
            traverse(list[i+1:],n,False,True)
            if left_of_parent:
                parent.left=n
            elif right_of_parent:
                parent.right=n
        i+=1
    i=0
def removeLeftRecursion(rulesDiction):
    # for rule: A->Aa|b
    # result: A->bA',A'->aA'|#

    # 'store' has new rules to be added
    store = {}

    # traverse over rules
    for lhs in rulesDiction:
        # alphaRules stores subrules with left-recursion
        # betaRules stores subrules without left-recursion
        alphaRules = []
        betaRules = []
        # get rhs for current lhs
        allrhs = rulesDiction[lhs]
        for subrhs in allrhs:
            if subrhs[0] == lhs:
                alphaRules.append(subrhs[1:])
            else:
                betaRules.append(subrhs)
        # alpha and beta containing subrules are separated
        # now form two new rules
        if len(alphaRules) != 0:
            # to generate new unique symbol
            # add ' till unique not generated
            lhs_ = lhs + "'"
            while (lhs_ in rulesDiction.keys()) \
                    or (lhs_ in store.keys()):
                lhs_ += "'"
            # make beta rule
            for b in range(0, len(betaRules)):
                betaRules[b].append(lhs_)
            rulesDiction[lhs] = betaRules
            # make alpha rule
            for a in range(0, len(alphaRules)):
                alphaRules[a].append(lhs_)
            alphaRules.append(['#'])
            # store in temp dict, append to
            # - rulesDiction at end of traversal
            store[lhs_] = alphaRules
    # add newly generated rules generated
    # - after removing left recursion
    for left in store:
        rulesDiction[left] = store[left]
    return rulesDiction


def LeftFactoring(rulesDiction):
    # for rule: A->aDF|aCV|k
    # result: A->aA'|k, A'->DF|CV

    # newDict stores newly generated
    # - rules after left factoring
    newDict = {}
    # iterate over all rules of dictionary
    for lhs in rulesDiction:
        # get rhs for given lhs
        allrhs = rulesDiction[lhs]
        # temp dictionary helps detect left factoring
        temp = dict()
        for subrhs in allrhs:
            if subrhs[0] not in list(temp.keys()):
                temp[subrhs[0]] = [subrhs]
            else:
                temp[subrhs[0]].append(subrhs)
        # if value list count for any key in temp is > 1,
        # - it has left factoring
        # new_rule stores new subrules for current LHS symbol
        new_rule = []
        # temp_dict stores new subrules for left factoring
        tempo_dict = {}
        for term_key in temp:
            # get value from temp for term_key
            allStartingWithTermKey = temp[term_key]
            if len(allStartingWithTermKey) > 1:
                # left factoring required
                # to generate new unique symbol
                # - add ' till unique not generated
                lhs_ = lhs + "'"
                while (lhs_ in rulesDiction.keys()) \
                        or (lhs_ in tempo_dict.keys()):
                    lhs_ += "'"
                # append the left factored result
                new_rule.append([term_key, lhs_])
                # add expanded rules to tempo_dict
                ex_rules = []
                for g in temp[term_key]:
                    ex_rules.append(g[1:])
                tempo_dict[lhs_] = ex_rules
            else:
                # no left factoring required
                new_rule.append(allStartingWithTermKey[0])
        # add original rule
        newDict[lhs] = new_rule
        # add newly generated rules after left factoring
        for key in tempo_dict:
            newDict[key] = tempo_dict[key]
    return newDict


# calculation of first
# epsilon is denoted by '#' (semi-colon)

# pass rule in first function
def first(rule):
    global rules, nonterm_userdef, \
        term_userdef, diction, firsts
    # recursion base condition
    # (for terminal or epsilon)
    if len(rule) != 0 and (rule is not None):
        if rule[0] in term_userdef:
            return rule[0]
        elif rule[0] == '#':
            return '#'

    # condition for Non-Terminals
    if len(rule) != 0:
        if rule[0] in list(diction.keys()):
            # fres temporary list of result
            fres = []
            rhs_rules = diction[rule[0]]
            # call first on each rule of RHS
            # fetched (& take union)
            for itr in rhs_rules:
                indivRes = first(itr)
                if type(indivRes) is list:
                    for i in indivRes:
                        fres.append(i)
                else:
                    fres.append(indivRes)

            # if no epsilon in result
            # - received return fres
            if '#' not in fres:
                return fres
            else:
                # apply epsilon
                # rule => f(ABC)=f(A)-{e} U f(BC)
                newList = []
                fres.remove('#')
                if len(rule) > 1:
                    ansNew = first(rule[1:])
                    if ansNew != None:
                        if type(ansNew) is list:
                            newList = fres + ansNew
                        else:
                            newList = fres + [ansNew]
                    else:
                        newList = fres
                    return newList
                # if result is not already returned
                # - control reaches here
                # lastly if eplison still persists
                # - keep it in result of first
                fres.append('#')
                return fres


# calculation of follow
# use 'rules' list, and 'diction' dict from above

# follow function input is the split result on
# - Non-Terminal whose Follow we want to compute
def follow(nt):
    global start_symbol, rules, nonterm_userdef, \
        term_userdef, diction, firsts, follows
    # for start symbol return $ (recursion base case)

    solset = set()
    if nt == start_symbol:
        # return '$'
        solset.add('$')

    # check all occurrences
    # solset - is result of computed 'follow' so far

    # For input, check in all rules
    for curNT in diction:
        rhs = diction[curNT]
        # go for all productions of NT
        for subrule in rhs:
            if nt in subrule:
                # call for all occurrences on
                # - non-terminal in subrule
                while nt in subrule:
                    index_nt = subrule.index(nt)
                    subrule = subrule[index_nt + 1:]
                    # empty condition - call follow on LHS
                    if len(subrule) != 0:
                        # compute first if symbols on
                        # - RHS of target Non-Terminal exists
                        res = first(subrule)
                        # if epsilon in result apply rule
                        # - (A->aBX)- follow of -
                        # - follow(B)=(first(X)-{ep}) U follow(A)
                        if '#' in res:
                            newList = []
                            res.remove('#')
                            ansNew = follow(curNT)
                            if ansNew != None:
                                if type(ansNew) is list:
                                    newList = res + ansNew
                                else:
                                    newList = res + [ansNew]
                            else:
                                newList = res
                            res = newList
                    else:
                        # when nothing in RHS, go circular
                        # - and take follow of LHS
                        # only if (NT in LHS)!=curNT
                        if nt != curNT:
                            res = follow(curNT)

                    # add follow result in set form
                    if res is not None:
                        if type(res) is list:
                            for g in res:
                                solset.add(g)
                        else:
                            solset.add(res)
    return list(solset)


def computeAllFirsts():
    global L,rules, nonterm_userdef, \
        term_userdef, diction, firsts
    for rule in rules:
        k = rule.split("->")
        # remove un-necessary spaces
        k[0] = k[0].strip()
        k[1] = k[1].strip()
        rhs = k[1]

        ##########################################

       # rhs.replace("||", "or")
       # print(rhs)
        multirhs = rhs.split('/')


       # rhs.replace("or", "||")

################################################3
       # multirhs = rhs.split('|')
        # remove un-necessary spaces
        for i in range(len(multirhs)):
            multirhs[i] = multirhs[i].strip()
            multirhs[i] = multirhs[i].split()
        diction[k[0]] = multirhs

    print(f"\nRules: \n")
    for y in diction:
        print(f"{y}->{diction[y]}")
    print(f"\nAfter elimination of left recursion:\n")

    diction = removeLeftRecursion(diction)
    for y in diction:
        print(f"{y}->{diction[y]}")
    print("\nAfter left factoring:\n")

    diction = LeftFactoring(diction)
    for y in diction:
        print(f"{y}->{diction[y]}")

    # calculate first for each rule
    # - (call first() on all RHS)
    for y in list(diction.keys()):
        t = set()
        for sub in diction.get(y):
            res = first(sub)
            if res != None:
                if type(res) is list:
                    for u in res:
                        t.add(u)
                else:
                    t.add(res)

        # save result in 'firsts' list
        firsts[y] = t

    print("\nCalculated firsts: ")
    key_list = list(firsts.keys())
    index = 0
    for gg in firsts:
        print(f"first({key_list[index]}) "
              f"=> {firsts.get(gg)}")
        index += 1


def computeAllFollows():
    global start_symbol, rules, nonterm_userdef, \
        term_userdef, diction, firsts, follows
    for NT in diction:
        solset = set()
        sol = follow(NT)
        if sol is not None:
            for g in sol:
                solset.add(g)
        follows[NT] = solset

    print("\nCalculated follows: ")
    key_list = list(follows.keys())
    index = 0
    for gg in follows:
        print(f"follow({key_list[index]})"
              f" => {follows[gg]}")
        index += 1


# create parse table
def createParseTable():
    import copy
    global diction, firsts, follows, term_userdef
    print("\nFirsts and Follow Result table\n")
    # find space size
    mx_len_first = 0
    mx_len_fol = 0
    for u in diction:
        k1 = len(str(firsts[u]))
        k2 = len(str(follows[u]))
        if k1 > mx_len_first:
            mx_len_first = k1
        if k2 > mx_len_fol:
            mx_len_fol = k2

    print(f"{{:<{10}}} "
          f"{{:<{mx_len_first + 5}}} "
          f"{{:<{mx_len_fol + 5}}}"
          .format("Non-T", "FIRST", "FOLLOW"))
    for u in diction:
        print(f"{{:<{10}}} "
              f"{{:<{mx_len_first + 5}}} "
              f"{{:<{mx_len_fol + 5}}}"
              .format(u, str(firsts[u]), str(follows[u])))

    # create matrix of row(NT) x [col(T) + 1($)]
    # create list of non-terminals
    ntlist = list(diction.keys())
    terminals = copy.deepcopy(term_userdef)
    terminals.append('$')

    # create the initial empty state of ,matrix
    mat = []
    for x in diction:
        row = []
        for y in terminals:
            row.append('')
        # of $ append one more col
        mat.append(row)

    # Classifying grammar as LL(1) or not LL(1)
    grammar_is_LL = True

    # rules implementation
    for lhs in diction:
        rhs = diction[lhs]
        for y in rhs:
            res = first(y)
            # epsilon is present,
            # - take union with follow
            if '#' in res:
                if type(res) == str:
                    firstFollow = []
                    fol_op = follows[lhs]
                    if fol_op is str:
                        firstFollow.append(fol_op)
                    else:
                        for u in fol_op:
                            firstFollow.append(u)
                    res = firstFollow
                else:
                    res.remove('#')
                    res = list(res) + \
                          list(follows[lhs])
            # add rules to table
            ttemp = []
            if type(res) is str:
                ttemp.append(res)
                res = copy.deepcopy(ttemp)
            for c in res:
                xnt = ntlist.index(lhs)
                yt = terminals.index(c)
                if mat[xnt][yt] == '':
                    mat[xnt][yt] = mat[xnt][yt] \
                                   + f"{lhs}->{' '.join(y)}"
                else:
                    # if rule already present
                    if f"{lhs}->{y}" in mat[xnt][yt]:
                        continue
                    else:
                        grammar_is_LL = False
                        mat[xnt][yt] = mat[xnt][yt] \
                                       + f",{lhs}->{' '.join(y)}"

    # final state of parse table
    print("\nGenerated parsing table:\n")
    frmt = "{:>12}" * len(terminals)
    print(frmt.format(*terminals))

    j = 0
    for y in mat:
        frmt1 = "{:>12}" * len(y)
        print(f"{ntlist[j]} {frmt1.format(*y)}")
        j += 1

    return (mat, grammar_is_LL, terminals)


def validateStringUsingStackBuffer(parsing_table, grammarll1,
                                   table_term_list, input_string,
                                   term_userdef, start_symbol):
    global L
    global rules1
    global tree
    print(f"\nValidate String => {input_string}\n")

    # for more than one entries
    # - in one cell of parsing table
    if grammarll1 == False:
        return f"\nInput String = " \
               f"\"{input_string}\"\n" \
               f"Grammar is not LL(1)"

    # implementing stack buffer

    stack = [start_symbol, '$']
    buffer = []

    # reverse input string store in buffer
    input_string = input_string.split()
    input_string.reverse()
    buffer = ['$'] + input_string

    print("{:>20} {:>20} {:>20}".
          format("Buffer", "Stack", "Action"))
    while True:

        # end loop if all symbols matched
        if stack == ['$'] and buffer == ['$']:
            print("{:>20} {:>20} {:>20}"
                  .format(' '.join(buffer),
                          ' '.join(stack),
                          "Valid"))
            return "\nValid String!"
        elif stack[0] not in term_userdef:
            # take font of buffer (y) and tos (x)
            x = list(diction.keys()).index(stack[0])
            y = table_term_list.index(buffer[-1])
            if parsing_table[x][y] != '':
                # format table entry received
                entry = parsing_table[x][y]
                print("{:>20} {:>20} {:>25}".
                      format(' '.join(buffer),
                             ' '.join(stack),
                             f"T[{stack[0]}][{buffer[-1]}] = {entry}"))
                lhs_rhs = entry.split("->")
                lhs_rhs[1] = lhs_rhs[1].replace('#', '').strip()
                entryrhs = lhs_rhs[1].split()
                stack = entryrhs + stack[1:]
                #############################################
                print(stack[0])
                match stack[0]:
                    case "exp":
                        rules1.append("exp")
                        tree+=["t", "exp'"]

                    case "t":
                        rules1.append("t")
                        tree.append(["f","t'"])

                    case "f":
                        rules1.append("f")
                        tree+=[["op","f'"]]

                    case "cop":
                        rules1.append("cop")
                        tree+=[[buffer[-1]]]

                    case "op":
                         rules1.append("op")
                         if buffer[-1] =='!':
                             tree+=[["!" ,"op"]]
                         elif buffer[-1] =="Id":
                             tree+=[['Id']]

                    case "exp'":
                        rules1.append("exp'")
                        if buffer[-1] == '||':
                            tree+=[["||","t", "exp'"]]
                        elif buffer[-1] == "$":
                            tree+=[["#"]]

                    case "t'":
                        rules1.append("t'")
                        if buffer[-1] == '&&':
                            tree+=[["&&", "f", "t'"]]
                        elif buffer[-1] == "||":
                            tree+=[["#"]]
                        elif buffer[-1] == "$":
                            tree+=[["#"]]

                    case "f'":
                        rules1.append("f'")
                        if buffer[-1] == '&&':
                            tree+=[["#"]]
                        elif buffer[-1] == "||":
                            tree+=[["#"]]
                        elif buffer[-1] == ">":
                            tree+=["cop", "op", "f'"]
                        elif buffer[-1] == "=":
                            tree+=["cop" ,"op" ,"f'"]
                        elif buffer[-1] == "<":
                            tree+=["cop", "op", "f'"]
                        elif buffer[-1] == "$":
                            tree+=[["#"]]

                ###############################################
            else:
                return f"\nInvalid String! No rule at " \
                       f"Table[{stack[0]}][{buffer[-1]}]."

        else:
            ######################


            ######################
            # stack top is Terminal
            if stack[0] == buffer[-1]:

                print("{:>20} {:>20} {:>20}"
                      .format(' '.join(buffer),
                              ' '.join(stack),
                              f"Matched:{stack[0]}"))
#########################################################
                L.append(stack[0])
#####################################################
                buffer = buffer[:-1]
                stack = stack[1:]
                ######################
                x = list(diction.keys()).index(stack[0])
                y = table_term_list.index(buffer[-1])
                entry =parsing_table[x][y]
                lhs_rhs = entry.split("->")
                entryrhs = lhs_rhs[1].split()
                rules1.append(lhs_rhs[0])
                ######################
                tree.append(entryrhs)
            else:
                return "\nInvalid String! " \
                       "Unmatched terminal symbols"

def parse ():
    global textEntry,root,rules,nonterm_userdef,term_userdef,firsts,follows,diction,start_symbol,rules1,tree,textEntry,nodelist
    sample_input_string = None#,img,image_label
    button1.place_forget()
    nodelist=[]
    dicts={}
    #textEntry.place_forget()
    # sample set 1 (Result: Not LL(1))
    # rules=["A -> S B | B",
    #        "S -> a | B c | #",
    #        "B -> b | d"]
    # nonterm_userdef=['A','S','B']
    # term_userdef=['a','c','b','d']
    # sample_input_string="b c b"

    # sample set 2 (Result: LL(1))
    # rules=["S -> A | B C",
    #        "A -> a | b",
    #        "B -> p | #",
    #        "C -> c"]
    # nonterm_userdef=['A','S','B','C']
    # term_userdef=['a','c','b','p']
    # sample_input_string="p c"

    # sample set 3 (Result: LL(1))
    # rules=["S -> A B | C",
    #        "A -> a | b | #",
    #        "B-> p | #",
    #        "C -> c"]
    # nonterm_userdef=['A','S','B','C']
    # term_userdef=['a','c','b','p']
    # sample_input_string="a c b"

    # sample set 4 (Result: Not LL(1))
    # rules = ["S -> A B C | C",
    #          "A -> a | b B | #",
    #          "B -> p | #",
    #         "C -> c"]
    # nonterm_userdef=['A','S','B','C']
    # term_userdef=['a','c','b','p']
    # sample_input_string="b p p c"

    # sample set 5 (With left recursion)
    # rules=["A -> B C c | g D B",
    #        "B -> b C D E | #",
    #        "C -> D a B | c a",
    #        "D -> # | d D",
    #        "E -> E a f | c"
    #       ]
    # nonterm_userdef=['A','B','C','D','E']
    # term_userdef=["a","b","c","d","f","g"]
    # sample_input_string="b a c a c"

    # sample set 6
    # rules=["E -> T E'",
    #        "E' -> + T E' | #",
    #        "T -> F T'",
    #        "T' -> * F T' | #",
    #        "F -> ( E ) | id"
    # ]
    # nonterm_userdef=['E','E\'','F','T','T\'']
    # term_userdef=['id','+','*','(',')']
    # sample_input_string="id * * id"
    # example string 1
    # sample_input_string="( id * id )"
    # example string 2
    # sample_input_string="( id ) * id + id"

    # sample set 7 (left factoring & recursion present)
    tree =[]
    
    rules1=[]

    rules = ["exp -> exp || t / t",
            "t -> t && f / f",
            "f -> f cop op / op",
            "cop -> > / = / <",
    "op -> ! op / Id"]

    nonterm_userdef = ['t', 'f', 'cop', 'op']
    term_userdef = ['&&', '||', '>', '=', '<', '!','Id']
    ##############################################
    x=textEntry.get()
    
    inp = re.findall(r"([(]|[)]|<=|=>|&&|[|]{2}|[<>=!]|[\w]+)", x)

    for i in range (len(inp)):
        if  re.findall(r'[A-Za-z][\w]*', inp[i]):
         inp[i]="Id"
    print(inp)

    strin = ' '.join(str(item) for item in inp)
    print(strin)


    #################################################
    sample_input_string = strin

    # sample set 8 (Multiple char symbols T & NT)
    # rules = ["S -> NP VP",
    #          "NP -> P | PN | D N",
    #          "VP -> V NP",
    #          "N -> championship | ball | toss",
    #          "V -> is | want | won | played",
    #          "P -> me | I | you",
    #          "PN -> India | Australia | Steve | John",
    #          "D -> the | a | an"]
    #
    # nonterm_userdef = ['S', 'NP', 'VP', 'N', 'V', 'P', 'PN', 'D']
    # term_userdef = ["championship", "ball", "toss", "is", "want",
    #                 "won", "played", "me", "I", "you", "India",
    #                 "Australia","Steve", "John", "the", "a", "an"]
    # sample_input_string = "India won the championship"

    # diction - store rules inputed
    # firsts - store computed firsts
    diction = {}
    firsts = {}
    follows = {}

    # computes all FIRSTs for all non terminals
    computeAllFirsts()
    # assuming first rule has start_symbol
    # start symbol can be modified in below line of code
    start_symbol = list(diction.keys())[0]
    # computes all FOLLOWs for all occurrences
    computeAllFollows()
    # generate formatted first and follow table
    # then generate parse table

    (parsing_table, result, tabTerm) = createParseTable()

    # validate string input using stack-buffer concept
    if sample_input_string != None:
        validity = validateStringUsingStackBuffer(parsing_table, result,
                                                tabTerm, sample_input_string,
                                                term_userdef, start_symbol)
        print(validity)
    else:
        print("\nNo input String detected")



    listcounter={}
    listcounter["exp"]=0
    listcounter["t"]=0
    listcounter["f"]=0
    listcounter["cop"]=0
    listcounter["op"]=0
    listcounter["exp'"]=0
    listcounter["t'"]=0
    listcounter["f'"]=0
    #'&&', '||', '>', '=', '<', '!','Id'
    listcounter["&&"]=0
    listcounter["||"]=0
    listcounter[">"]=0
    listcounter["="]=0
    listcounter["<"]=0
    listcounter["!"]=0
    listcounter["Id"]=0
    listcounter["#"]=0
    strng=""
    Tree =tree
    Tree.insert(0,['t',"exp'"])
    t_counter=-1
    for t in Tree:
        t_counter+=1
        element_counter=-1
        for element in t :
            element_counter+=1
            strng+=element
            if strng[-1].isnumeric():
                continue
            else :
                if strng.count(element)>1:
                    listcounter[element]=listcounter[element]+1
                    element += str(listcounter[element])
                    print(element)
                    Tree[t_counter][element_counter]=element

    #counter=0
    counter1=0
    dicts = {}
    discounter={}
    discounter["exp"]=0
    discounter["t"]=0
    discounter["f"]=0
    discounter["cop"]=0
    discounter["op"]=0
    discounter["exp'"]=0
    discounter["t'"]=0
    discounter["f'"]=0

    strn =""
    print ("rules1")
    print(rules1)
    rules1_1=rules1
    rules1_1.insert(0,'exp')
    for i in rules1_1:
        strn += i
        if strn[-1].isnumeric():
            continue
        else:
            if strn.count(i)>1:
                discounter[i]=discounter[i]+1
                i += str(discounter[i])
                #counter = counter + 1
            dicts[i] = Tree[counter1]
            counter1=counter1+1

    print(dicts)
    print()
    print()
    print(tree)
    print()
    print(rules1)
    print("Tree")
    print(Tree)

    
    newlist= re.findall(r"(=|<|>|&&|[|]{2}|[!]|[A-Za-z][\w]*)", x)
    print (newlist)
    
    traverse(newlist,None,False,False)
    print("node\tleft\tright")
    children=[]
    parents=[]
    for n in nodelist:
        if n.left==None and n.right==None:
            print(n.name+"\tidentifier with no children")
        elif n.left==None:
            parents.append(n.name)
            children.append([n.right.name])
            print(n.name+"\tno left"+"\t"+n.right.name)
        elif n.right==None:
            parents.append(n.name)
            children.append([n.left.name])
            print(n.name+"\t"+n.left.name+"\tno right")
        else:
            parents.append(n.name)
            children.append([n.left.name,n.right.name])
            print(n.name+"\t"+n.left.name+"\t"+n.right.name)
    listcounter_1={}
    listcounter_1["&&"]=0
    listcounter_1["||"]=0
    listcounter_1[">"]=0
    listcounter_1["="]=0
    listcounter_1["<"]=0
    listcounter_1["!"]=0

    t_counter=-1
    strng=nodelist[0].name
    for c in children:
        t_counter+=1
        element_counter=-1
        for element in c :
            if element not in listcounter_1:
                listcounter_1[element]=0
            element_counter+=1
            strng+=element
            if strng[-1].isnumeric():
                continue
            else :
                if strng.count(element)>1:
                    listcounter_1[element]=listcounter_1[element]+1
                    element += str(listcounter_1[element])
                    #print(element)
                    children[t_counter][element_counter]=element
    counter1=0
    dicts_1={}
    discounter_1={}
    discounter_1["&&"]=0
    discounter_1["||"]=0
    discounter_1[">"]=0
    discounter_1["="]=0
    discounter_1["<"]=0
    discounter_1["!"]=0
    p_counter=-1
    strn=""               
    for p in parents:
        strn += p
        if strn[-1].isnumeric():
            continue
        else:
            if strn.count(p)>1:
                discounter_1[p]=discounter_1[p]+1
                p += str(discounter_1[p])
                #counter = counter + 1
            dicts_1[p] = children[counter1]
            counter1=counter1+1                 
    print("children  ****:")                    
    print(children)
    print("dicts_1   ******")
    print(dicts_1)
    
    dict={}
    for n in nodelist:
        if n.left==None and n.right==None:
            continue
        if n.left==None:
            dict[n.name]=[n.right.name]
        elif n.right==None:
            dict[n.name]=[n.left.name]
        else:
            dict[n.name]=[n.left.name,n.right.name]
    print (dict)


    os.remove('nx_test.png')
    os.remove('test.dot')
    
    G = nx.DiGraph()
    F = nx1.DiGraph()
    #plt.figure(1)
    plt.clf()
    for key,value in dicts.items():
        G.add_node(key)
        for v in value:
            if "#" in v:
                v=v.replace("#",'\u03B5')
            G.add_node(v)
            G.add_edge(key,v)

    write_dot(G,'test.dot')
    plt.title('draw_PARSE TREE')
    pos =graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True, arrows=False,node_size=640)
    plt.savefig('nx_test.png')
    print("k")
    #img=PhotoImage(file='nx_test.png')
    #image_label=Label(root,image=img)
    #img.config(file='nx_test.png')
    #image_label.config(image=img)
    from PIL import Image
    img= (Image.open(r"nx_test.png"))
    resized_image= img.resize((400,300), Image.ANTIALIAS)
    new_image= ImageTk.PhotoImage(resized_image)
    image_label.config(image=new_image)
    image_label.image=new_image
    image_label.place(x=700,y=10)
    leaves=[]
    #for x in G.nodes():
        #if G.out_degree(x)==0 and G.in_degree(x)==1:
            #leaves.append()
    G.clear()
   # F.clear()
    plt.clf()
    
    os.remove('nx_syntax.png')
    os.remove('syntax.dot')
    #plt1.figure(2)
    for key,value in dicts_1.items():
        F.add_node(key)
        for v in value:
            
            F.add_node(v)
            F.add_edge(key,v)
   
    # write dot file to use with graphviz
    # run "dot -Tpng test.dot >test.png"
    write_dot(F,'syntax.dot')
    
    # same layout using matplotlib with no labels
    plt1.title('Abstract syntax Tree')
    pos =graphviz_layout(F, prog='dot')
    nx1.draw(F, pos, with_labels=True, arrows=True)
    plt1.savefig('nx_syntax.png')
    plt1.clf()
    F.clear()
    print ("dict: "+str(dict))
    print ("dicts: "+str(dicts))
    #img_2.config(file='nx_syntax.png')
    #image_label_2.config(image=img_2)
    img_2= (Image.open(r"nx_syntax.png"))
    resized_image_2= img_2.resize((400,300), Image.ANTIALIAS)
    new_image_2= ImageTk.PhotoImage(resized_image_2)
    image_label_2.config(image=new_image_2)
    image_label_2.image=new_image_2
    image_label_2.place(x=700,y=350)
    dicts_1={}
    children=[]
    nodelist=[]
    dicts={}
    dict={}
def show_parsing_table():
    global img_3,button1,parse_table_btn
    image_label.place_forget()
    image_label_2.place_forget()
    image_label_3.place(x=500,y=100)
    button1.place_forget()
    #parse_table_btn.place_forget()
def new_test():
    global button1,image_label,textEntry
    image_label.place_forget()
    image_label_2.place_forget()
    image_label_3.place_forget()
    textEntry.place(x=13,y=250,height=28)
    button1.place(x=10,y=300)

root =Tk()
root.minsize(400,200)
root.state('zoom')
mylabel=Label()
button1 = ttk.Button(root, text ="test",command = parse)
new_test_button = ttk.Button(root, text ="new_test",
        command = new_test)
button1.place(x=10,y=300)
new_test_button.place(x=300,y=500)
parse_table_btn= ttk.Button(root, text ="show parsing table",command = show_parsing_table)
parse_table_btn.place(x=100,y=600)
name = StringVar()
textEntry=Entry(root,textvariable=name,width=40,font=('Georgia 12'))
textEntry.place(x=13,y=250,height=28)
#img=PhotoImage()
image_label=Label(root)
#img_2=PhotoImage()
image_label_2=Label(root)

img_3=PhotoImage(file="parsing_table.PNG")
image_label_3=Label(root,image=img_3)
root.mainloop()