import sys
import os

from board import Board

def invalid_input(message):
    print >>sys.stderr, "Invalid input: %s" % message
    sys.exit(1)

def readline(buf):
    while not '\n' in buf:
        tmp = os.read(0, 1024)
        if not tmp:
            break
        buf += tmp

    if not buf.strip():
        return None, buf
    if not '\n' in buf:
        invalid_input('unexpected EOF after "%s"' % buf)

    index = buf.find('\n')
    line = buf[0:index]
    rest = buf[index + 1:]
    return line, rest

def read(buf):
    meta, buf = readline(buf)

    if not meta:
        return None, buf

    dim = meta.split(' ')

    if len(dim) != 2:
        invalid_input("expected dimensions on first line")

    try:
        width, height = int(dim[0]), int(dim[1])
    except ValueError:
        invalid_input("malformed dimensions on first line")

    lines = []

    while len(lines) != height:
        line, buf = readline(buf)
        if not line:
            invalid_input("unexpected EOF reading board")
        lines.append(line)

    board = [line[:width] for line in lines]

    me = None
    them = None
    board2 = [] #[None]*height
    y = 0
    for line in lines:
        x = 0
        list = []
        for obj in line:
            list.append(obj)
            if obj == '1':
                me = (x, y)
            elif obj == '2':
                them = (x, y)
            x += 1
        board2.append(list)
        y += 1

    #print board2

    #for x in board2:
        #for y in x:
            #print y,
        #print
#    print board2
#    print board

    if len(board) != height or any(len(board[y]) != width for y in xrange(height)):
        invalid_input("malformed board")

    return Board(width, height, board2, me, them), buf

def generate():
    """Generate board objects, once per turn.

    This method returns a generator which you may iterate over.
    Make sure to call tron.move() exactly once for every board
    generated, or your bot will not work.
    """

    buf = ''

    while True:
        board, buf = read(buf)
        if not board:
            break
        yield board

    if buf.strip():
        invalid_input("garbage after last board: %s" % buf)

