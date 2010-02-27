from __future__ import division
import copy
import types
import sys
import time
import operator


NORTH = 1
EAST  = 2
SOUTH = 3
WEST  = 4

FLOOR = ' '
WALL  = '#'
ME    = '1'
THEM  = '2'

DIRECTIONS = (NORTH, EAST, SOUTH, WEST)

voronoi_calls = 0

tabx = {NORTH: 0, SOUTH: 0, EAST: 1, WEST: -1}
taby = {NORTH: -1, SOUTH: +1, EAST: 0, WEST: 0}

class Board(object):
    def __init__(self, width, height, board, me, them):
        self.board = board
        self.height = height
        self.width = width
        self.players = {}
        self.players[ME] = me
        self.players[THEM] = them
        self.utility = {}
        self.utility[ME] = 0
        self.utility[THEM] = 0
        self.game_done = False
        self.childboards = []
        self.depth = 0
        self.has_terminated = False
        self.utl = None
        self.game_done = False

    def __copy__(self):
        boardcopy = [None]*self.height
        for y in xrange(self.height):
            boardcopy[y] = self.board[y][:]
        #print boardcopy
        #print self.board

        result = Board(self.width, self.height, boardcopy, self.players[ME], self.players[THEM])
        
        result.to_move = self.to_move
        result.game_done = self.game_done
        if self.game_done:
            result.utility = self.utility
        result.depth = self.depth
        result.has_terminated = self.has_terminated
        return result

    def __getitem__(self, coords):
        """Retrieve the object at the specified coordinates.

        Use it like this:

            if board[3, 2] == tron.THEM:
                # oh no, the other player is at (3,2)
                run_away()

        Coordinate System:
            The coordinate (x, y) corresponds to row y, column x.
            The top left is (0, 0) and the bottom right is
            (board.height - 1, board.width - 1). Out-of-range
            coordinates are always considered walls.

        Items on the board:
            tron.FLOOR - an empty square
            tron.WALL  - a wall or trail of a bot
            tron.ME    - your bot
            tron.THEM  - the enemy bot
        """

        x, y = coords
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return WALL
        return self.board[y][x]

    def __setitem__(self, coords, val):
        x, y = coords
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self.board[y][x] = val

    def passable(self, coords):
        """Determine if a position in the board is passable.

        You can only safely move onto passable tiles, and only
        floor tiles are passable.
        """
        return self[coords] == FLOOR

    def rel(self, direction, origin):
        """Calculate which tile is in the given direction from origin.

        The default origin is you. Therefore, board.rel(tron.NORTH))
        is the tile north of your current position. Similarly,
        board.rel(tron.SOUTH, board.them()) is the tile south of
        the other bot's position.
        """

        x, y = origin
        return x+tabx[direction], y+taby[direction]

        #if direction == NORTH:
            #return x, y - 1
        #elif direction == SOUTH:
            #return x, y + 1
        #elif direction == EAST:
            #return x + 1, y
        #elif direction == WEST:
            #return x - 1, y
        #else:
            #raise KeyError("not a valid direction: %s" % direction)

    def adjacent(self, origin):
        """Calculate the four tiles that are adjacent to origin.

        Particularly, board.adjacent(board.me()) returns the four
        tiles to which you can move to this turn. This does not
        return tiles diagonally adjacent to origin.
        """
        x,y = origin
        return [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
        #return [self.rel(dir, origin) for dir in DIRECTIONS]

    def antidir(self, origin, pos):
        """Calculate which tile is in the given direction from origin.

        The default origin is you. Therefore, board.rel(tron.NORTH))
        is the tile north of your current position. Similarly,
        board.rel(tron.SOUTH, board.them()) is the tile south of
        the other bot's position.
        """

        x, y = origin
        a, b = pos
        
        if a == x and b == y - 1:
            return NORTH
        if a == x and b == y + 1:
            return SOUTH
        if a == x + 1 and b == y:
            return EAST
        if a == x - 1 and b == y:
            return WEST
        else:
            raise KeyError("not a valid diffstuff: %s, %s" % origin, pos)
            

    def moves(self):
        """Calculate which moves are safe to make this turn.

        Any move in the returned list is a valid move. There
        are two ways moving to one of these tiles could end
        the game:

            1. At the beginning of the following turn,
               there are no valid moves off this tile.
            2. The other player also moves onto this tile,
               and you collide.
        """
        #possible = dict((dir, self.rel(dir, self.to_move)) for dir in DIRECTIONS)
        #passable = [dir for dir in possible if self.passable(possible[dir])]
        #print "passable", passable
        #if not passable:
            # it seems we have already lost
            #return [NORTH]
        #return passable
        return [dir for dir in DIRECTIONS]

    def validmoves(self, goodmove):
        playerpos = self.players[self.to_move]
        list = []
        if self[self.rel(goodmove, playerpos)] != WALL:
            list.append(goodmove)
        for dir in DIRECTIONS:
            if dir != goodmove:
                dest = self.rel(dir, playerpos)
                if self[dest] != WALL:
                    list.append(dir)
        return list
        #d = dict((dir, self.rel(dir, player)) for dir in DIRECTIONS)
        #return self.getPassableMoves( self.players[self.to_move] )

    def getPassableMoves(self, player):
        possible = dict((dir, self.rel(dir, player)) for dir in DIRECTIONS)
        passable = [dir for dir in possible if self[possible[dir]] != WALL]
        return passable

    def validDests(self, pos):
        possible = dict((dir, pos) for dir in DIRECTIONS)
        passable = [dir for dir in possible if self[possible[dir]] != WALL]
        return passable

    #def distance(self, a, b):
        #return abs(a[0] - b[0]) + abs(a[1] - b[1])

    #def countSquares(self, player):
        #opponent = THEM if player == ME else ME
        #playerSquares = 0
        #opponentSquares = 0
        #for y in xrange(self.height):
            #for x in xrange(self.width):
                #if self[(x,y)] == FLOOR:
                    #mydist = self.distance(self.players[player], (x,y))
                    #theirdist = self.distance(self.players[opponent], (x,y))
                    #if mydist < theirdist:
                        #playerSquares += 1
                    #else:
                        #opponentSquares +=1
        #return playerSquares - opponentSquares

    
    def voronoi(self):
        global voronoi_calls
        voronoi_calls += 1
        #print voronoi_calls
        #print "voronoi"
        #self.print_board()
        #cb = [None]*self.height
        #for y in xrange(self.height):
            #cb[y] = self.board[y][:]
        cb = [self.board[y][:] for y in xrange(self.height)]
        #print cb
        iter = 0
        found = False
        start = self.players[ME]
        queue = [('X', self.players[ME], 0)] #, ('Y', self.players[THEM], 0)]
        count = {}
        while queue:
            iter += 1
            player, pos, depth = queue.pop(0)
            x, y = pos
            cb[y][x] = (player, depth)
            #print "mark", pos, player, depth
            #print (player, pos, depth)
#            opponent = 'Y' if player == 'X' else 'Y'
            #return [self.rel(dir, origin) for dir in DIRECTIONS]
            list = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            for dest in list:
            #for dest in self.adjacent(pos):
                x, y = dest
                if x > 0 and y > 0 and x < self.width and y < self.height:
                    #print dest, x, y, cb[y][x]
                    if cb[y][x] == THEM:
                        found = True
                    if cb[y][x] == FLOOR:
                        cb[y][x] = (player, -1)
                        if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                            count[player+"red"] = count.get(player+"red", 1) + 1
                        else:
                            count[player+"black"] = count.get(player+"black", 1) + 1

                        #count[player] = count.get(player, 1) + 1
                        
                        queue.append((player, dest, depth+1))
                        #print "appended", (player, dest, depth+1)


        #print "x done"
        #print "first iters:", iter
        iter = 0
        queue = [('Y', self.players[THEM], 0)]
        while queue:
            iter += 1
            player, pos, depth = queue.pop(0)
            x, y = pos
            cb[y][x] = (player, depth)
            #print "mark", pos, player, depth
            
            list = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            #for dest in self.adjacent(pos):
            for dest in list:
                x, y = dest
                #if x > 0 and y > 0 and x < self.width and y < self.height:
                if 0 <= x < self.width and 0 <= y < self.height:
                    if cb[y][x] == FLOOR:
                        cb[y][x] = (player, -1)
                        #count[player] = count.get(player, 1) + 1
                        if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                            count[player+"red"] = count.get(player+"red", 1) + 1
                        else:
                            count[player+"black"] = count.get(player+"black", 1) + 1
                        queue.append((player, dest, depth+1))
                        #print "appended", (player, dest, depth+1)
                    elif type(cb[y][x]) == types.TupleType:
                        #print cb[y][x], depth
                        opponent = 'Y' if player == 'X' else 'X'
                        p, d = cb[y][x]
                        
                        if p == opponent:
                            # taking over a square
                            if depth+1 < d:
                                #count[p] = count.get(p, 1) - 1
                                if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                                    count[p+"red"] = count.get(p+"red", 1) - 1
                                else:
                                    count[p+"black"] = count.get(p+"black", 1) - 1

                                #count[player] = count.get(player, 1) + 1
                                if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                                    count[player+"red"] = count.get(player+"red", 1) + 1
                                else:
                                    count[player+"black"] = count.get(player+"black", 1) + 1
                                cb[y][x] = ('Y', -1)
                                queue.append((player, dest, depth+1))
                                #print "appended", (player, dest, depth+1)
                            # sharing a square
                            if d == depth+1:
                                #count[p] = count.get(p, 1) - 1
                                if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                                    count[p+"red"] = count.get(p+"red", 1) - 1
                                else:
                                    count[p+"black"] = count.get(p+"black", 1) - 1
                                #count[player] = count.get(player, 1) + 1
                                #count['equal'] = count.get("equal", 1) + 1
                                cb[y][x] = ('XY', -1)
                                queue.append(('XY', dest, depth+1))
                                #print "appended", ('XY', dest, depth+1)

        #for line in cb:
            #print line

        #for y in xrange(self.height):
            #for x in xrange(self.width):

                #if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
                    #cb[y][x] = 'R'
                #else:
                    #cb[y][x] = 'B'

        #for line in cb:
            #print line

        #print count
        #print "second iters:", iter
        #print found
        x, y = self.players[ME]
        #Xcount = abs(count.get('Xblack', 0) - count.get('Xred', 0))
        if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
            # red
            Xcount = (count.get('Xblack', 0) - 1) + count.get('Xred', 0)
        else:
            # black
            Xcount = (count.get('Xblack', 0)) + (count.get('Xred', 0) - 1)

        x, y = self.players[THEM]
        if (x % 2 == 1 and y % 2 == 1) or (x % 2 == 0 and y % 2 == 0):
            # red
            Ycount = (count.get('Yblack', 0) - 1) + count.get('Yred', 0)
        else:
            # black
            Ycount = (count.get('Yblack', 0)) + (count.get('Yred', 0) - 1)
        #Ycount = abs(count.get('Yblack', 0) - count.get('Yred', 0))

        #print Xcount - Ycount
        
        return (Xcount - Ycount, found)
        #return ((count.get('X',0) - count.get('Y',0)), found)

    def simpleVoronoi(self):

        def signum(val):
            if val < 0: return -1
            elif val > 0: return 1
            else: return val

        cb = [self.board[y][:] for y in xrange(self.height)]
        #print cb
        start = self.players[ME]
        queue = [('X', self.players[ME], 0)] #, ('Y', self.players[THEM], 0)]
        count = {}
        while queue:
            player, pos, depth = queue.pop(0)
            x, y = pos
            #cb[y][x] = (player, depth)
            #return [self.rel(dir, origin) for dir in DIRECTIONS]
            for dest in [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]:
                x, y = dest
                if 0 < x < self.width and 0 < y < self.height:
                    #print dest, x, y, cb[y][x]
                    if cb[y][x] == FLOOR:
                        cb[y][x] = depth+1 #(player, -1)
                        count[player] = count.get(player, 1) + 1
                        queue.append((player, dest, depth+1))

        queue = [('Y', self.players[THEM], 0)]
        while queue:
            player, pos, depth = queue.pop(0)
            x, y = pos
            #cb[y][x] = (player, depth)
            #print "mark", pos, player, depth
            
            #for dest in self.adjacent(pos):
            for dest in [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]:
                x, y = dest
                #if x > 0 and y > 0 and x < self.width and y < self.height:
                if 0 < x < self.width and 0 < y < self.height:
                    if cb[y][x] == FLOOR:
                        cb[y][x] = depth - 1 #(player, -1)
                        count[player] = count.get(player, 1) + 1
                        queue.append((player, dest, depth - 1))
                    #elif type(cb[y][x]) == types.TupleType:
                    elif type(cb[y][x]) == type(1) and cb[y][x] != 0:
                        opponent = 'Y' if player == 'X' else 'X'
                        d = cb[y][x]
                        
                        if signum(d) == 1:
                            # taking over a square
                            if abs(depth)+1 < d:
                                count['X'] = count.get('X', 1) - 1
                                count['Y'] = count.get('Y', 1) + 1
                                cb[y][x] = depth - 1 #('Y', -1)
                                queue.append((player, dest, depth - 1))
                                #print "appended", (player, dest, depth+1)
                            # sharing a square
                            if abs(d) == abs(depth)+1:
                                count['X'] = count.get('X', 1) - 1
                                #count['Y'] = count.get('Y', 1) - 1
                                #count['equal'] = count.get("equal", 1) + 1
                                cb[y][x] = 0 #('XY', -1)
                                queue.append(('XY', dest, depth - 1))
                                #print "appended", ('XY', dest, depth+1)
        #for line in cb:
            #print line
        
        #return (count.get('X',0) - count.get('Y',0))

        print count
        return cb
    

    def voronoiNew(self):
        global voronoi_calls
        voronoi_calls += 1
        print "voronoi"
        #self.print_board()

        vb = self.simpleVoronoi()
        sb = [self.board[y][:] for y in xrange(self.height)]
        cb = [[0]*self.width for y in xrange(self.height)]
        parents = [[0]*self.width for y in xrange(self.height)]

        start = self.players[ME]

        def neighbors(node):
            #print node
            x, y = node
            possible = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            #print possible
            #print [(x,y) for x,y in possible if y == 2]
            passable = [pos for pos in possible if self[pos] == FLOOR or self[pos] == ME]
            return passable

        def newneighbors(bb, node):
            #print node
            ox, oy = node
            possible = [(ox+tabx[dir], oy+taby[dir]) for dir in DIRECTIONS]
            #print possible
            #print [(x,y) for x,y in possible if y == 2]
            #print ox,oy
            passable = [(x,y) for (x,y) in possible if x > 0 and y > 0 and x < self.width and y < self.height and bb[y][x] != WALL and (bb[y][x] > 0 or bb[y][x] == ME)]
            return passable


        print "voronoi"
        for y in xrange(self.height):
            print vb[y]


        visited = {}
        stack = [start]
        count = [0]

        num = {}
        low = {}
        parent = {}
        counter = [1]



        def dfs(node, depth):
            #print count[0], "pre", node, depth
            #count[0] += 1
            #final1.append(node)
            visited[node] = True
            low[node] = num[node] = counter[0]
            counter[0] += 1
            #print "rule1", node, low[node]
            #print "\t\t",neighbors(node)
            for child in newneighbors(vb, node):
                #print node, "->", v
                #if v == start:
                    #print "HEY", v
                if child not in visited:
                    parent[child] = node
                    #visited[v] = True
                    dfs(child, depth+1)
                    if low[child] >= num[node]:
                        x, y = node
                        sb[y][x] = 'A'
                        print node, "is an articulation point"
                        print child, " is at fault", low[child], num[node]
                    low[node] = min(low[node], low[child])
                    #print "rule3", node, low[node]
                else:
                    if parent.get(node) != child:
                        low[node] = min(low[node], num[child])
                        #print "backedge", node, low[node]
            #print count[0], "post", node, depth
            #count[0] += 1
            #final1.append(node)

        print "dfs"
        dfs(start, 0)
        print "dfs done"

        class Chamber:
            entrance = None
            size = 0
            leaf = False
            parent = None
            label = 0
            depth = 0
            def __init__(self, en, si, le, la, de):
                self.entrance = en
                self.size = si
                self.leaf = le
                self.label = la
                self.depth = de

        chambers = {} #[[0]*self.width for y in xrange(self.height)]
        chamberMap = {}

        labelCount = 0
        lolChamber = Chamber(None, 0, False, labelCount, 0)
        chamberMap[(0,0)] = lolChamber
        chambers[labelCount] = lolChamber
        labelCount += 1

        startChamber = Chamber((0,0), 1, False, labelCount, 1)
        chambers[labelCount] = startChamber
        chamberMap[start] = startChamber
        labelCount += 1
        
        queue = [start]
        artPoints = []
        while queue:
            pos = queue.pop(0)
            print "pop", pos
            ox,oy = pos
            for v in neighbors(pos):
                x,y = v
                if vb[y][x] < 0:
                    continue
                elif not v in chamberMap and sb[y][x] != 'A':
                    chamberMap[pos].size += 1
                    chamberMap[v] = chamberMap[pos]
                    queue.append(v)
                elif not v in chamberMap and sb[y][x] == 'A':
                    #artPoints.append()
                    print "new chamber", v, "parent", pos, "pp", chamberMap[pos].entrance
                    newChamber = Chamber(pos, 1, False, labelCount, chamberMap[pos].depth+1)
                    chambers[labelCount] = newChamber
                    labelCount += 1
                    chamberMap[v] = newChamber
                    queue.append(v)
                elif v in chamberMap and (chamberMap[v] == chamberMap[pos] or v == chamberMap[pos].entrance):
                    continue
                elif v in chamberMap :
                    print "merge", pos, v, chamberMap[pos], chamberMap[v]
                    commonparent = None
                    parmap = {}

                    p = pos
                    pp = chamberMap[p]
                    while pp.entrance:
                        print "parent", p, pp.entrance, pp
                        parmap[pp] = 1
                        p = pp.entrance
                        pp = chamberMap[p]
                    
                    print "ll"
                    p = v
                    pp = chamberMap[p]
                    while pp.entrance:
                        print "lookup", p, pp.entrance, pp
                        if pp in parmap:
                            print "ok", p, pp.entrance
                            commonparent = p
                            break
                        p = pp.entrance
                        pp = chamberMap[p]
                    #commonparent

                    chamberMap[commonparent].size += chamberMap[v].size
                    chamberMap[commonparent].size += chamberMap[pos].size
                    chamberMap[v] = chamberMap[commonparent]
                    chamberMap[pos] = chamberMap[commonparent]
                    #if chamberMap[v].label > chamberMap[pos].label:
                        #chamberMap[pos].size += chamberMap[v].size
                        ##chamberMap[chamberMap[v].entrance] = chamberMap[pos].parent
                        #chamberMap[v] = chamberMap[pos]
                    #else:
                        #chamberMap[v].size += chamberMap[pos].size
                        ##chamberMap[chamberMap[v].entrance]
                        #chamberMap[pos] = chamberMap[v]
        print 
        print " CHAMBERS "                   
        print                    
        for y in xrange(self.height):
            for x in xrange(self.width):
                if (x,y) in chamberMap: print chamberMap[(x,y)].label,
                else: print "N",
            print
        print                    
        print                    
        print                    


                    



        #print
        #print
        ##print final1
        #print
        #print

        ##final2 = []

        ##visited = {}
        ##stack = [[]]
        ##jumpstack = []

        ##tmplist = []
        ##node = start
        
        ##count = 0
        ##counter = 0

        ##while True:

            ##while node:
                ##if node in visited:
                    ##if len(stack[-1]) > 0:
                        ##node = stack[-1].pop(0)
                    ##else:
                        ##node = None
                    ##continue
                ##### PRE
                ###print count, "pre", node, len(jumpstack)
                ###count += 1
                ##final2.append(node)
                ##jumpstack.append(node)
                ##visited[node] = True
                ##x,y = node
                ##num[y][x] = counter
                ##low[y][x] = counter
                ##counter += 1
                ##list = []
                ##for v in neighbors(node):
                    ###if v not in visited:
                    ###x2,y2 = v
                    ###parent[y2][x2] = node
                    ###if num[y2][x2] > num[y][x]:
                    ##list.append(v)
                    ###else:
                        ###if parent[y][x] != v:

                
                ##if len(list) > 0:
                    ##node = list[0]
                    ##stack.append(list[1:])
                ##else:
                    ##node = None

            ##if not stack:
                ##break
            
            ##if len(stack[-1]) > 0:
                ##node = stack[-1].pop(0)
                ###while node in visited and len(stack[-1]) > 0:
                    ###node = stack[-1].pop(0)

                ###if len(stack[-1]) == 0:
                    ###stack.pop()
            ##else:
                ##stack.pop()

                ##if jumpstack:
                    ##popitem = jumpstack.pop()
                    ##### POST
                    ###x, y = popitem
                    ###px, py = parent[y][x]
                    ###if low[y][x] >= num[py][px]:
                       ###print popitem, "is an articulation point"
                    ###low[py][px] = min(low[py][px], low[y][x])
                    ##print count, "post", popitem, len(jumpstack)
                    ##count += 1
                    ##final2.append(popitem)

        ###print "extra"
        ###while jumpstack:
            ###popitem = jumpstack.pop()
            ###print count, "post", popitem, len(jumpstack)
            ###count += 1
            ###final2.append(popitem)

        ##print "done"
        ##print
        ##print
        ###print final2
        ##print
        ##print
        ##print final1 == final2
        ##print len(final1), len(final2)
        ##print
        ##print
        ##for i in xrange(len(final1)):
            ##if final1[i] != final2[i]:
                ##print i, final1[i], final2[i]
            
        ##print
        ##print


    
            ##pos, depth = stack.pop()
            ##print pos
            ##x, y = pos
            ##if sb[y][x] == FLOOR or sb[y][x] == '1':
                ##sb[y][x] = count
                ##count += 1
                ###print "pop", pos
                ##for dest in [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]:
                    ##x2, y2 = dest
                    ###if sb[y][x] == 'X':
                    ###if type(sb[y][x]) == type(1) and sb[y][x] < depth:
                        ###cb[y][x] += 1

                    ##if sb[y2][x2] == FLOOR:
                    ###if sb[y][x] < depth:
                        ###sb[y][x] = 'X'
                        ###print "add", dest
                        ##parents[y2][x2] = sb[y][x]
                        ##stack.append((dest, depth+1))
                        ###count += 1

        ## low
        

            
        print "   SB   "
        print "  ",
        for x in xrange(0, self.width):
            print "%3d" % (x),
        print
        for y in xrange(self.height):
            print "%2d" % y, 
            for x in xrange(self.width):
                print "%3s" % sb[y][x],
            print
        
        print
        print

        print "   LOW   "
        print "  ",
        for x in xrange(0, self.width):
            print "%3d" % (x),
        print
        for y in xrange(self.height):
            print "%2d" % y, 
            for x in xrange(self.width):
                print "%3d" % low.get((x,y),0),
            print

        print
        print

        print "   NUM   "
        print "  ",
        for x in xrange(0, self.width):
            print "%3d" % (x),
        print
        for y in xrange(self.height):
            print "%2d" % y, 
            for x in xrange(self.width):
                print "%3d" % num.get((x,y),0),
            print

        print
        print

        print "   parent   "
        print parent
        print "  ",
        for x in xrange(0, self.width):
            print "%3d" % (x),
        print
        for y in xrange(self.height):
            print "%2d" % y, 
            for x in xrange(self.width):
                print parent.get((x,y), (0,0)),
            print

        #print
        #print

        #print "  ",
        #for x in xrange(1, self.width+1):
            #print "%3d" % (x),
        #print
        #for y in xrange(self.height):
            #print "%2d" % y, 
            #for x in xrange(self.width):
                #print "%3d" % parents[y][x],
            #print

        #print cb
        #iter = 0
        #found = False
        #start = self.players[ME]
        #queue = [('X', self.players[ME], 0)] #, ('Y', self.players[THEM], 0)]
        #count = {}
        #while queue:
            #iter += 1
            #player, pos, depth = queue.pop(0)
            #x, y = pos
            #cb[y][x] = (player, depth)
            ##print "mark", pos, player, depth
            ##print (player, pos, depth)
##            opponent = 'Y' if player == 'X' else 'Y'
            ##return [self.rel(dir, origin) for dir in DIRECTIONS]
            #list = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            #for dest in list:
            ##for dest in self.adjacent(pos):
                #x, y = dest
                #if x > 0 and y > 0 and x < self.width and y < self.height:
                    ##print dest, x, y, cb[y][x]
                    #if cb[y][x] == THEM:
                        #found = True
                    #if cb[y][x] == FLOOR:
                        #cb[y][x] = (player, -1)
                        #count[player] = count.get(player, 1) + 1
                        #queue.append((player, dest, depth+1))
                        ##print "appended", (player, dest, depth+1)


        ##print "x done"
        ##print "first iters:", iter
        #iter = 0
        #queue = [('Y', self.players[THEM], 0)]
        #while queue:
            #iter += 1
            #player, pos, depth = queue.pop(0)
            #x, y = pos
            #cb[y][x] = (player, depth)
            ##print "mark", pos, player, depth
            
            #list = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            ##for dest in self.adjacent(pos):
            #for dest in list:
                #x, y = dest
                ##if x > 0 and y > 0 and x < self.width and y < self.height:
                #if 0 <= x < self.width and 0 <= y < self.height:
                    #if cb[y][x] == FLOOR:
                        #cb[y][x] = (player, -1)
                        #count[player] = count.get(player, 1) + 1
                        #queue.append((player, dest, depth+1))
                        ##print "appended", (player, dest, depth+1)
                    #elif type(cb[y][x]) == types.TupleType:
                        ##print cb[y][x], depth
                        #opponent = 'Y' if player == 'X' else 'X'
                        #p, d = cb[y][x]
                        
                        #if p == opponent:
                            ## taking over a square
                            #if depth+1 < d:
                                #count[p] = count.get(p, 1) - 1
                                #count[player] = count.get(player, 1) + 1
                                #cb[y][x] = ('Y', -1)
                                #queue.append((player, dest, depth+1))
                                ##print "appended", (player, dest, depth+1)
                            ## sharing a square
                            #if d == depth+1:
                                #count[p] = count.get(p, 1) - 1
                                #count[player] = count.get(player, 1) + 1
                                ##count['equal'] = count.get("equal", 1) + 1
                                #cb[y][x] = ('XY', -1)
                                #queue.append(('XY', dest, depth+1))
                                ##print "appended", ('XY', dest, depth+1)
        ##for line in cb:
            ##print line
        ##print count
        ##print "second iters:", iter
        ##print found
        
        #return ((count.get('X',0) - count.get('Y',0)), found)

    #def getMonoUtility(self):
        #return self.warn(self.players[ME])

    def getutility(self, player):
        opponent = THEM if player == ME else ME
        if self.utility[player] == 0:
            mymoves = self.getPassableMoves(self.players[player])
            theirmoves = self.getPassableMoves(self.players[opponent])
            if len(mymoves) == 0 and len(theirmoves) == 0:
                return -0.0001#-98
            if len(mymoves) > 0 and len(theirmoves) == 0:
                return +4000
            if len(mymoves) == 0 and len(theirmoves) > 0:
                return -4000

            #connected = self.playersAreConnected()
            squares, isconn = self.voronoi()
            #squares = self.warn(self.players[ME])

            #print " voronoi: ", squares, connected, isconn
            #assert connected == isconn
            #squares = self.countSquares(player)
            #print squares
            #self.print_board()
            #score = 99*squares/(self.width*self.height)
            #print score
            return squares
            
             

        return self.utility[player]

    #def getMonoutili

    
    def do_move(self, dir):
        #print >>sys.stderr, self.to_move
        player = self.to_move # 'X'
        assert player == ME or player == THEM
        opponent = THEM if player == ME else ME
        player_pos = self.players[player] #pos
        opponents_pos = self.players[opponent] #pos

        old_pos = player_pos 
        new_pos = self.rel(dir, player_pos)
        if self[new_pos] == WALL:
            # loss for player
            self.utility[player] = -9000
            self.utility[opponent] = +9000
        elif self[new_pos] == opponent:
            # draw
            self.utility[player] = -0.00001#-99
            self.utility[opponent] = -0.00001#-99
            #print >>sys.stderr, "DRAW.."
            self.game_done = True
        self[old_pos] = WALL
        self[new_pos] = player
        self.players[player] = new_pos
        self.to_move = opponent

    def undo_move(self, dir):
        pass

    def terminal_test(self):
        #return True
        #print "player", self.to_move
        #print "pos", self.players[self.to_move]
        if self.to_move == ME:
            if self[self.players[ME]] != ME and self.players[ME] != self.players[THEM]:
                self.utility[ME] = -5000
                return True
            #if not self.playersAreConnected():
                #return True
            if self.game_done:
                #print >>sys.stderr, "Terminator 2."
                return True

            meok = False
            themok = False
            for dir in DIRECTIONS:
                #print "dir", dir
                x, y = self.players[ME]
                dest = x+tabx[dir], y+taby[dir]
                #dest = self.rel(dir, self.players[self.to_move])
                #print "dest", dest
                #print self.passable(dest)
                if self.passable(dest):
                    meok = True
                    #return False
                x, y = self.players[THEM]
                dest = x+tabx[dir], y+taby[dir]
                if self.passable(dest):
                    themok = True

            if meok and themok:
                return False
            else:
                return True

        if self.to_move == THEM:
            if self[self.players[THEM]] != THEM:
                self.utility[THEM] = -5000
                return True
            if self.game_done:
                #print >>sys.stderr, "Terminator 1."
                return True
         
            #for dir in DIRECTIONS:
                #if self.passable(self.rel(dir, self.players[self.to_move])):
                    #return False
            #return True
        return False

    def printb(self):
        #log.debug("\t"*depth,)
        print "-"*10
        for y in self.board:
            #print "\t"*depth,
            print ''.join(y)
        #print >>sys.stderr, "\t"*depth,

    def print_board(self, log, depth=0):
        #log.debug("\t"*depth,)
        log.debug("-"*10)
        for y in self.board:
         #   print >>sys.stderr, "\t"*depth,
            log.debug(''.join(y))
        #print >>sys.stderr, "\t"*depth,

    def playersAreConnected(self):
        #start = self.players[player]

        cb = [None]*self.height
        for y in xrange(self.height):
            cb[y] = self.board[y][:]

        iter = 0
        queue = [(ME, self.players[ME]), (THEM, self.players[THEM])]
        while queue:
            iter += 1
            p, pos = queue.pop(0)
            x, y = pos
            list = [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]
            for dest in list:
                x, y = dest
                if cb[y][x] == FLOOR:
                    cb[y][x] = 'X'+p
                    queue.append((p, dest))
                elif cb[y][x] == 'X1' or cb[y][x] == 'X2':
                    opponent = THEM if p == ME else ME
                    if cb[y][x] == 'X'+opponent:
                        #print "connected iters:", iter
                        return True

        #print cb
        #print "connected iters:", iter
        return False

    #def wdag(self, start):
        
        #cb = [None]*self.height
        #for y in xrange(self.height):
            #cb[y] = self.board[y][:]

        ##length_to = [0] * (self.width * self.height)
        #length_to = {}
        #p = {}
        #queue = [start]
        #count = 0

        #while queue:
            #pos = queue.pop(0)
            #print "pop", pos
            #x, y = pos
            #for dest in [(x+tabx[dir], y+taby[dir]) for dir in DIRECTIONS]:
                #x,y = dest
                #if cb[y][x] == FLOOR:
                    #print "append", dest
                    #queue.append(dest)
                    #cb[y][x] = 'X'
                    #if length_to.get(dest, 0) <= length_to.get(pos, 0) + 1:
                        #length_to[dest] = length_to.get(pos, 0) + 1
                        #p[dest] = pos
                        #cb[y][x] = count
                        #count += 1
        
        ##print length_to
        #print sorted(length_to.items(), key=operator.itemgetter(1))
        ##print p
        #for y in cb:
            #print >>sys.stderr, y
        #print >>sys.stderr, '----'





    def warn(self, start): # warnsdorff

        #cb = [None]*self.height
        #for y in xrange(self.height):
            #cb[y] = self.board[y][:]
        cb = [self.board[y][:] for y in xrange(self.height)]
        
        #start = self.players[ME]
        #queue = [(start, 1)]
        
        #squares = self.countSquares(start)

        #def valid(b, pos):
            #return filter(lambda s: b[y][x] == FLOOR, list)

            #possible = dict((dir, self.rel(dir, player)) for dir in DIRECTIONS)
            #passable = [dir for dir in possible if self[possible[dir]] == FLOOR]
            #return passable

        count = 0
        first = None
        pos = start
        while True:
            #print "pos", pos
            lowest = None
            #neighbors = []
            minNeigh = 99
            for dir in DIRECTIONS:
                x, y = pos
                x, y = dest = x+tabx[dir], y+taby[dir]
                #x,y = dest = self.rel(dir, pos)
                if cb[y][x] == FLOOR:
                    #print "neigh", dest
                    temp = 0
                    for dir2 in DIRECTIONS:
                        #x2,y2 = self.rel(dir2, dest)
                        x2, y2 =x+tabx[dir2], y+taby[dir2]
                        if cb[y2][x2] == FLOOR:
                            temp+=1
                    #if temp == 0: continue
                    if temp < minNeigh:
                        minNeigh = temp
                        lowest = dest
                        #neighbors.append((dir, dest))

            #list = [self.rel(dir, pos) for dir in DIRECTIONS]
            ##list = filter(lambda s: cb[s[1]][s[0]] == FLOOR, list)
            #for dest in list:
                #x,y = dest
                #if cb[y][x] == FLOOR:
                    ##cb[y][x] = 'X'
                    #neighbors.append((dir, dest))
            #print "----"
            #print neighbors
            #print list
            #print "----"


            #destinations = sorted(neighbors, key=lambda c: len( filter(lambda s: cb[s[1]][s[0]] == FLOOR, [self.rel(dir, c[1]) for dir in DIRECTIONS])))
            #if not destinations:
                #break
            #lowest = destinations[0][1]

            if not lowest:
                break


            x, y = pos = lowest
            cb[y][x] = count
            count += 1

        #if count >= 50:
            #self.print_board()
        #for y in cb:
            #print >>sys.stderr, y
        #print >>sys.stderr, '----'

        #if first:
            #return first, count
        return 1, count

    def countSquares(self, start):

        cb = [None]*self.height
        for y in xrange(self.height):
            cb[y] = self.board[y][:]

        count = 0
        queue = [start]
        while queue:
            pos = queue.pop(0)
            x, y = pos
            cb[y][x] = 'X'
            for dest in self.adjacent(pos):
                x, y = dest
                if cb[y][x] == FLOOR:
                    count += 1
                    cb[y][x] = 'Y'
                    queue.append(dest)
        return count
