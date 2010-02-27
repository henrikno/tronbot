#!/usr/bin/env python
import tronutil
from board import Board, ME, THEM
import board as bbb
import copy
import os
import sys
import time
#import signal

#try:
    #import psyco
    #psyco.full()
#except ImportError:
    #pass

infinity = 1e200

hashmap = {}

#DEBUG = True

#import logging
#x = logging.getLogger("logfun")
#x.setLevel(logging.DEBUG)
##logging.basicConfig(level=logging.DEBUG)
#h = logging.StreamHandler()
#f = logging.Formatter("%(message)s")
#h.setFormatter(f)
#x.addHandler(h)

#log = logging.getLogger("logfun")


TIME_LIMIT = 0.85
doneByDepth = False

history = True
historyboards = 0
history_limit = 1e123#50000
mainboard = None

#print sys.stdout
#sout = sys.stdout
#print sys.stdout, sout
#sys.stdout = sys.stderr
#print sys.stdout, sout

class TimeoutException(Exception):
    pass

#def alarm(*args):
    #raise TimeoutException()

def move(direction):
    #sys.stdout = sout
    print direction
    #sout.flush()
    sys.stdout.flush()
    

def tab(n):
    return "  ."*n

def iterativedeepening(board):
    global mainboard
    global starttime, doneByDepth, history
    
    if history:
        if not mainboard:
            mainboard = board
            #board.print_board()
        else:
            
            found = False
            oldmainboard = mainboard
            theirmove = board.antidir(mainboard.players[THEM], board.players[THEM])
            found = False
            for child in mainboard.childboards:
                if child.move == theirmove:
                    found = True
                    #print "found it"
                    mainboard = child
            #if not found:
                #print "OH FUCK FUCK FUCK"
                #print "old"
                #mainboard.print_board()
                #print "new"
                #board.print_board()
                #print mainboard
                #print theirmove
                #print mainboard.players[THEM]
                #print board.players[THEM]
                #print "children:", mainboard.childboards
                #for child in mainboard.childboards:
                    #print child.move
                    
                
            if found: # if we didn't find it... start over
                board = mainboard
            #assert found

            #del oldmainboard
        
        #board.print_board()
        #mainboard.print_board()
    #print board
    #print "old children", board.childboards

    best = 1
    try:
        for maxdepth in xrange(2, 1000, 2):
            #lastbest = best
            doneByDepth = False
            best = minimax(board, maxdepth)
            #print >>sys.stderr, best, time.time() - starttime, maxdepth, bbb.voronoi_calls, historyboards
            #print >>sys.stderr, "maxdepth:|%d|%d|" % (maxdepth, bbb.voronoi_calls)
            #bbb.voronoi_calls = 0
            if time.time() - starttime > TIME_LIMIT:
                return best
            if not doneByDepth: # If we actually have terminated
                return best
    except TimeoutException, e:
        #print >>sys.stderr "TimeoutException"
        #if debug: print best, time.time() - starttime, maxdepth, bbb.voronoi_calls, historyboards
        #print >>sys.stderr, "maxdepth:|%d|%d|" % (maxdepth, bbb.voronoi_calls)
        #bbb.voronoi_calls = 0
        return best
        #raise e
    #except Exception, e:
        #print "Exception"
        #print e
        #raise
    #finally:
        #print "TIMEOUT", best, time.time() - starttime, maxdepth, bbb.voronoi_calls, historyboards
        #bbb.voronoi_calls = 0
    return best

maxgoodmoves = {}
mingoodmoves = {}

def max_value(board, depth, alpha, beta, offset, player, maxdepth):
    global doneByDepth, maxgoodmoves, historyboards
    #board.print_board()
    if board.terminal_test():
        #print "TERMINATED"
        #board.print_board()
        #print depth
        #print "terminal node max", board.depth, depth
        board.has_terminated = True
        if board.utl and board.depth-offset == depth:
            #print "max save", board.utl
            return board.utl
        utl = board.getutility(player)
        #if utl > 0:
            #utl -= 0.5*depth
        #else:
            #utl += 0.5*depth
        #print "max", utl
        #board.print_board()
        board.utl = utl
        return utl
    if depth >= maxdepth:
        doneByDepth = True
        if board.utl and board.depth-offset == depth:
            return board.utl
        utl = board.getutility(player)
        #print "depth. max.", utl

        #board.print_board()
        board.utl = utl
        return utl
    if time.time() - starttime > TIME_LIMIT:
        raise TimeoutException
    v = -infinity

    if len(board.childboards) > 0:
        #if len(board.childboards) != len(board.validmoves(1)):
            #board.print_board()
            #print [c.move for c in board.childboards]
            #print board.validmoves(1)
            #print board.move

        #assert len(board.childboards) == len(board.validmoves(1))
        #tab(depth); print "max using childboard"

        dtab = []
        for s in board.childboards:
            #if s.has_terminated:
                #tab(depth); print "has terminated"
                #ret = s.utl
            #else:
            #if s.utl and s.depth >= maxdepth:
                #print "yoo", s.utl
                #ret = s.utl
            #else:
            #if debug: tab(depth); print "s MAX move ", s.move, "(", depth, ")"
            ret = min_value(s, depth+1, alpha, beta, offset, player, maxdepth)
            dtab.append((s.move, ret))
            v = max(v, ret)
            if v >= beta:
                #tab(depth); print "pruned"
                return v
            if ret > alpha:
                board.childboards = [s]+[c for c in board.childboards if c != s]
                alpha = ret
                maxgoodmoves[depth] = s.move#dir
        #log.debug("%s s max RESULT: (%d), v: %d, %s" % (tab(depth), depth, v, dtab))
    else:

        tmpChildBoards = []
        for dir in board.validmoves(maxgoodmoves.get(depth,1)):
            s = copy.copy(board)
            s.do_move(dir)
            s.depth = depth+1
            s.move = dir
            tmpChildBoards.append(s)
                #board.ancestor.numchilds += 1
                #s.ancestor = board.ancestor
                #historyboards += 1 # test
        if history and historyboards < history_limit:
            board.childboards = tmpChildBoards
            historyboards += len(tmpChildBoards)
        
        dtab = []
        for s in tmpChildBoards:
            #if debug: tab(depth); print "MAX move:", s.move, "(", depth, ")"
            ret = min_value(s, depth+1, alpha, beta, offset, player, maxdepth)
            dtab.append((s.move, ret))
            v = max(v, ret)
            if v >= beta:
                #tab(depth); print "pruned"
                return v
                #pass
            if ret > alpha:
                alpha = ret
                maxgoodmoves[depth] =s.move
            #if depth == 2:
                #log.debug(v)
                #board.print_board(log)
        #log.debug("%s max RESULT: (%d), v: %d, %s" % (tab(depth), depth, v, dtab))
    return v



def min_value(board, depth, alpha, beta, offset, player, maxdepth):
    global doneByDepth, mingoodmoves, betachanges, historyboards
    #board.print_board()
    #if board.terminal_test():
        #board.print_board()
        ##print "terminal node min", board.depth, depth
        #if board.utl and board.depth-offset == depth:
            ##print "min save", board.utl
            ##print "save", board.utl
            #return board.utl
        #utl = board.getutility(player)
        #utl += 0.1*depth
        ##print "max", utl
        #board.utl = utl
        #return utl
    if depth >= maxdepth:
        doneByDepth = True
        if board.utl and board.depth-offset == depth:
            #print "save"
            return board.utl
        utl = board.getutility(player)
        #utl += depth
        #print "depth. min", utl
        board.utl = utl
        return utl

    if time.time() - starttime > TIME_LIMIT:
        raise TimeoutException
    v = infinity

    if len(board.childboards) > 0:
        #if len(board.childboards) != len(board.validmoves(1)):
            #board.print_board()
            #print [c.move for c in board.childboards]
            #print board.validmoves(1)
            #print board.move

        #assert len(board.childboards) == len(board.validmoves(1))
        #tab(depth); print "min using childboard"
        dtab = []
        for s in board.childboards:
            #tab(depth); print "s MIN move ", s.move, "(", s.depth, ")"
            #if s.utl and s.depth-1 >= maxdepth:
                #print "yoo", s.utl
                #ret = s.utl
            #else:
            ret = max_value(s, depth+1, alpha, beta, offset, player, maxdepth)
            dtab.append((s.move, ret))
            v = min(v, ret)
            if v <= alpha:
                #tab(depth); print "pruned"
                return v
            if v < beta:
                board.childboards = [s]+[c for c in board.childboards if c != s]
                beta = v
                mingoodmoves[depth] = s.move #dir
        #log.debug("%s s min RESULT: (%d) v: %d, %s" % (tab(depth), depth, v, dtab))
    else:
        
        tmpChildBoards = []
        for dir in board.validmoves(mingoodmoves.get(depth, 1)):
            s = copy.copy(board)
            s.do_move(dir)
            s.depth = depth+1
            s.move = dir
            #if history and historyboards < history_limit:
                #board.childboards.append(s)
                #board.ancestor.numchilds += 1
                #s.ancestor = board.ancestor
                #historyboards += 1 # test
            tmpChildBoards.append(s)
                #board.ancestor.numchilds += 1
                #s.ancestor = board.ancestor
                #historyboards += 1 # test

        if history and historyboards < history_limit:
            board.childboards = tmpChildBoards
            historyboards += len(tmpChildBoards)
    
        dtab = []
        for s in tmpChildBoards:
            #if debug: tab(depth); print "MIN move:", s.move, "(", depth, ")"
            ret = max_value(s, depth+1, alpha, beta, offset, player, maxdepth)
            dtab.append((s.move, ret))
            v = min(v, ret)
            if v <= alpha:
                #if debug: tab(depth); print "pruned"
                return v
            if v < beta:
                beta = v
                mingoodmoves[depth] = s.move
            #if depth == 1:
                #log.debug(v)
                #board.print_board(log)
            #if v < -4000:
                #log.debug("HEY")
                #log.debug("%d" % v,)
                #s.print_board(log)
                #log.debug("prev")
                #board.print_board(log)
        #log.debug("%s min RESULT: %d (%d) %s" % (tab(depth), v,  depth,  dtab))

    return v

def minimax(board, maxdepth):
    global starttime, historyboards
    player = board.to_move



    moves = board.validmoves(maxgoodmoves.get(0, 1))
    if not moves: return 1

    best = moves[0]

    v = -infinity
    if len(board.childboards) > 0:
        assert len(board.childboards) == len(board.validmoves(1))
        #print "using childboard"
        dtab = []
        for s in board.childboards:
            #if debug: print "MAX childboard move:", s.move, "depth: 0"
            #print "board", s.depth, 1
            nv = min_value(s, 1, -infinity, infinity, s.depth-1, player, maxdepth)
            dtab.append((s.move, nv))
            if nv > v:
                # find, and move s to start of list TODO
                #print board.childboards
                board.childboards = [s]+[c for c in board.childboards if c != s]
                #print board.childboards
                maxgoodmoves[0] = s.move #dir
                v = nv
                best = s.move #dir

        #log.debug("s max dir RESULT:", best, "v:", v, dtab)
            #s.print_board()
    else:

        # Body of minimax_decision starts here:
        dtab = []
        for dir in moves:
            #if debug: tab(0); print "MAX move:", dir
            s = copy.copy(board)
            s.do_move(dir)
            s.depth = 1
            s.move = dir
            if history and historyboards < history_limit:
                board.childboards.append(s)
                historyboards += 1
            #if s.game_done
                #nv = s.getutility(player)
            #else:


            #if debug: print "MAX move:", s.move, "depth: 0"
            nv = min_value(s, 1, -infinity, infinity, 1, player, maxdepth)
            dtab.append((s.move, nv))
            if nv > v:
                maxgoodmoves[0] = dir
                v = nv
                best = dir
        #if debug: print "max dir RESULT:", best, "v:", v, dtab
        #log.debug("max dir RESULT: %d v: %d, %s" % (best, v, dtab))

    return best


def main():
    global starttime, doneByDepth, mingoodmoves, maxgoodmoves, mainboard, historyboards
    for board in tronutil.generate():

        #old_alarm = signal.signal(signal.SIGALRM, alarm)
        #signal.setitimer(signal.ITIMER_REAL, TIME_LIMIT)
        #signal.alarm(timeout)

        starttime = time.time()
        doneByDepth = False
        board.to_move = ME

        # TEST
        #board.printb()
        #board.voronoi()
        #board.simpleVoronoi()
        #board.warn(board.players[ME])
        #board.voronoiNew()
        #continue

        #board.print_board(log)

        #print board.playersAreConnected()

        if board.playersAreConnected():

            m = iterativedeepening(board)
            #log.debug("MOVE: %d" % (m,))
            move(m)
            #print >> sys.stderr, m

            newmingoodmoves = {}
            for key,val in mingoodmoves.items():
                if key > 1:
                    newmingoodmoves[key-2] = val
            mingoodmoves = newmingoodmoves

            newmaxgoodmoves = {}
            for key,val in maxgoodmoves.items():
                if key > 1:
                    newmaxgoodmoves[key-2] = val
            maxgoodmoves = newmaxgoodmoves

        else:
            #try:
            best = 1
            lm = 0
            #board.wdag(board.players[ME])
            #print board.players[ME]
            #for dir in board.validmoves(1):
                #dest = board.rel(dir, board.players[ME])
                #s = copy.copy(board)
                #s.do_move(dir)
                ##print dest
                #v, l = s.warn(dest)
                #if l > lm:
                    #lm = l
                    #best = dir
                #print best
            v, best = superiterative(board)
                    #v, best = supermax(board, 0, -infinity, infinity, 0, board.to_move, 100)

            #except TimeoutException, e:
                #print "Timeout"
                #pass
            #finally:
                #move(best)
            #log.debug("MOVE: %d" % (best,))
            move(best)

        if mainboard:
            oldmainboard = mainboard
            found = False
            for child in mainboard.childboards:
                if child.move == m:
                    #print "new mainboard"
                    found = True
                    mainboard = child
                else:
                    def reccount(b):
                        count = 1
                        for child in b.childboards:
                            count += reccount(child)
                        return count
                        
                    #count = reccount(child)
                    #print "deleted", count
                    #historyboards -= count

            #if not found:
                #print mainboard
                #mainboard.print_board
                #mainboard.move
                #print mainboard.childboards
                #for child in mainboard.childboards:
                    #print child.move
                    #child.print_board()

            #assert found
                    

            #del oldmainboard


def superiterative(board):
    global doneByDepth
    try:
        best = (0, 1)
        doneByDepth = False
        for maxdepth in xrange(1, 1000):
            doneByDepth = False
            best = supermax(board, 0, -infinity, infinity, 0, board.to_move, maxdepth)
            #print >>sys.stderr, best, time.time() - starttime, maxdepth
            #bbb.voronoi_calls = 0
            if time.time() - starttime > TIME_LIMIT:
                return best
            if not doneByDepth: # If we actually have terminated
                #print "done by term"
                return best
    except TimeoutException, e:
        #print "TimeoutException"
        #print >>sys.stderr, best, time.time() - starttime, maxdepth
        #bbb.voronoi_calls = 0
        return best



def supermax(board, depth, alpha, beta, offset, player, maxdepth):
    global doneByDepth, maxgoodmoves
    #board.print_board()
    if board.terminal_test():
        #print "term"
        move,count = board.warn(board.players[ME])
        count += depth
        #utl += 0.1*depth
        return count, move
    if depth >= maxdepth:
        doneByDepth = True
        move,count = board.warn(board.players[ME])
        count += depth
        return count, move
    if time.time() - starttime > TIME_LIMIT:
        raise TimeoutException

    v = -infinity
    mv = 1

    tmpChildBoards = []
    for dir in board.validmoves(maxgoodmoves.get(depth,1)):
        if board[board.rel(dir, board.players[ME])] != ' ': continue
        #tab(depth); print "maxiMAX move:", dir, "(", depth, ")", maxdepth
        s = copy.copy(board)
        s.do_move(dir)
        s.to_move = ME
        s.depth = depth+1
        s.move = dir

        ret,l = supermax(s, depth+1, alpha, beta, offset, player, maxdepth)
        v = max(v, ret)
        if v >= beta:
            #tab(depth); print "pruned"
            return v, dir
        if ret > alpha:
            mv = dir
            alpha = ret
            maxgoodmoves[depth] = dir

        #if v >= 50:
        #if depth == 0:
            #print "dir:", s.move, "v:", v
            #s.print_board()
            #s.warn(s.players[ME])
    return v, mv

main()
