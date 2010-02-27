#include <iostream>
#include <cstdio>
#include <csignal>
#include <cstdlib>
#include <sys/time.h>
#include <errno.h>
#include <cstring>
#include <queue>
#include <cassert>

#include "utils.h"

using namespace std;

//#define DEBUG

#ifdef DEBUG
#define debug(format, args...) fprintf(stderr, format, ## args)
#else
#define debug
#endif

const int TIMEOUT = 900000;

class TimeoutException {
};

void tab(int n) {
    for (int i = 0; i < n; ++i) debug("  ."); ///debug("  . ");
}

//volatile int alrmcount = 0;
volatile int timeout = 0;
int calls = 0;
int voronoicalls = 0;
int warncalls = 0;


void myhandler(int sig) {
    //debug("ALARM DING DING DING\n");
    //cout << "alarm is here " << sig << endl;
    //signal (SIGINT, SIG_IGN);
    //alrmcount = 1;
    //struct itimerval value;
    //getitimer( ITIMER_REAL, &value );
    //value.it_value.tv_sec = 0;
    //value.it_value.tv_usec = 200000;
    //setitimer( ITIMER_REAL, &value, NULL );


    timeout = 1;
    //throw TimeoutException();
}

typedef void (*PFV)(void);
PFV set_terminate(PFV);

//void terminator() {
    
        //fprintf(stderr, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stderr, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stderr, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stderr, "ERR RRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stdout, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stdout, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stdout, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        //fprintf(stdout, "ER RRRRRRRRRRRRRRRRRRRRRRRRROR\n");
    //exit(1);

//}

enum DIRECTIONS { NORTH = 1, EAST, SOUTH, WEST };
char possiblemoves[] = {NORTH, EAST, SOUTH, WEST};
enum PLAYER { ME = 0, THEM };
char playerSymbol[2] = {'1', '2'};
int infinity = 10000000;
char minmoves[2500][4] = {NORTH, EAST, SOUTH, WEST}; // 2500 = 
char maxmoves[2500][4] = {NORTH, EAST, SOUTH, WEST};
//char memoizedmoves[50*50][4];

//bool game_done = false;

struct QueueElem {
    int x, y, depth;
};

struct Board {
    int px, py;
    int ox, oy;
    int width;
    int height;
    char to_move;
    int utility;
    //int movelog[2500*2];
    int numMoves;
    bool game_done;

    char **map;

    Board(int width, int height) {

        this->width = width;
        this->height = height;
        utility = 0;
        numMoves = 0;
        //memset(movelog, 0, sizeof(movelog));
        game_done = false;
        to_move = ME;

        map = allocateMap();
        //map = (char**)malloc(sizeof(char*)*height + sizeof(char)*width*height);
        //if (!map) {
            //fprintf(stderr,"Cannot allocate array\n");
            //exit(-1);
        //}
        //for (int i = 0; i < height; i++) {
            //map[i] = (char*)(map+height) + i*width;
        //}
    }

    char** allocateMap() {

        char **tmp;
        tmp = (char**)calloc(1, (sizeof(char*)*this->height) + (sizeof(char) * this->width * this->height));
        if (!tmp) {
            fprintf(stderr,"Cannot allocate array\n");
            exit(-1);
        }
        for (int i = 0; i < height; i++) {
            tmp[i] = (char*)(tmp+height) + i*width;
        }
        return tmp;
    }

    short** allocateShortMap() {

        short **tmp;
        tmp = (short**)calloc(1, (sizeof(short*)*this->height) + (sizeof(short) * this->width * this->height));
        if (!tmp) {
            fprintf(stderr,"Cannot allocate array\n");
            exit(-1);
        }
        for (int i = 0; i < height; i++) {
            tmp[i] = (short*)(tmp+height) + i*width;
        }
        return tmp;
    }

    bool checkDir(int dir, int x, int y) {
        //debug("%d %d %d\n", dir, x, y);
        
        if (x <= 0 || y <= 0 || x > width || y > height) {
            return false;
        }
        switch(dir){
            case NORTH:
                return map[y-1][x] != '#'; // || map[y-1][x] == '1' || map[y-1][x] == '2';
                break;
            case SOUTH:
                return map[y+1][x] != '#'; // || map[y+1][x] == '1' || map[y+1][x] == '2';
                break;
            case EAST:
                return map[y][x+1] != '#'; // || map[y][x+1] == '1' || map[y][x+1] == '2';
                break;
            case WEST:
                return map[y][x-1] != '#'; // || map[y][x-1] == '1' || map[y][x-1] == '2';
                break;
        }
    }

    void getNewPos(int dir, int &x, int &y) {
        switch(dir){
            case NORTH:
                y-=1;
                break;
            case EAST:
                x+=1;
                break;
            case SOUTH:
                y+=1;
                break;
            case WEST:
                x-=1;
                break;
        }
    }

    void getOldPos(int dir, int &x, int &y) {
        switch(dir){
            case NORTH:
                y+=1;
                break;
            case SOUTH:
                y-=1;
                break;
            case EAST:
                x-=1;
                break;
            case WEST:
                x+=1;
                break;
        }
    }

    //int getNextMove(int x, int y) {
        //if (map[y-1][x] == ' ') { return NORTH; }
        //if (map[y][x+1] == ' ') { return EAST; }
        //if (map[y+1][x] == ' ') { return SOUTH; }
        //if (map[y][x-1] == ' ') { return WEST; }
        //return NORTH;
    //}


    void getMoves(char a[], char goodmoves[]) {
        int posx, posy;
        if (to_move == ME) {
            posx = px; posy = py;
        } else {
            posx = ox; posy = oy;
        }

        //int tmp[] = {NORTH, SOUTH, EAST, WEST};

        int j = 0;
        for (int i = 0; i < 4; i++) {
            if (checkDir(goodmoves[i], posx, posy)) a[j++] = goodmoves[i];
        }
        a[j] = 0;
    }

    void getPlayerMoves(char a[], PLAYER player) {
        int posx, posy;
        if (player == ME) {
            posx = px; posy = py;
        } else {
            posx = ox; posy = oy;
        }

        int tmp[] = {NORTH, EAST, SOUTH, WEST};
        int j = 0;
        for (int i = 0; i < 4; i++) {
            if (checkDir(tmp[i], posx, posy)) a[j++] = tmp[i];
        }
        a[j] = 0;
    }

    char doMove(char dir) {
        int *posx, *posy, oppx, oppy;
        if (to_move == ME) {
            //cerr << "My turn" << endl;
            posx = &px; posy = &py;
            oppx = ox; oppy = oy;
        } else {
            //cerr << "Their turn" << endl;
            posx = &ox; posy = &oy;
            oppx = px; oppy = py;
        }

        int nposx = *posx, nposy = *posy;
        getNewPos(dir, nposx, nposy);

        //this->printBoard();
        if (nposx <= 0 || nposx >= width || nposy <= 0 || nposy >= height) {
            //debug2("went into a wall");
            //replaced = ' ';
            // Wall
        } else if (to_move == ME && map[nposy][nposx] == '2') {
            //replaced = '2';
            utility = +1;
            game_done = true;
            //debug2("ME went into 2");
            // Draw
        } else if (to_move == THEM && map[nposy][nposx] == '1') {
            //replaced = '1';
            utility = +1;
            //debug2("THEM went into 1");
            game_done = true;
            // Draw
        } else if (map[nposy][nposx] == ' ') {
            //replaced = ' ';
        }
        char replaced = map[nposy][nposx];
        //cout << "playersymbol" << playerSymbol[to_move] << to_move << endl;
        map[*posy][*posx] = '#';
        map[nposy][nposx] = playerSymbol[to_move];
        *posx = nposx;
        *posy = nposy;
        //to_move ^= 1; // Switch player
        //
        //movelog[numMoves++] = dir;
        return replaced;
    }

    void undoMove(char dir, char oldVal, int oposx, int oposy) {
        int *posx, *posy, oppx, oppy;
        if (to_move == ME) {
            posx = &px; posy = &py;
            oppx = ox; oppy = oy;
        } else {
            posx = &ox; posy = &oy;
            oppx = px; oppy = py;
        }
        //int oposx = *posx, oposy = *posy;
        //getOldPos(dir, oposx, oposy);
        map[*posy][*posx] = oldVal;
        map[oposy][oposx] = playerSymbol[to_move];
        *posy = oposy;
        *posx = oposx;
        game_done = false;
        //movelog[numMoves--] = 0;
        utility = 0;
    }

    bool terminal_test() {

        if (map[py][px] != playerSymbol[ME] && (ox != px || oy != py)) {
            utility = -15000;
            return true;
        }

        if (game_done && utility != 0) {
            return true;
        }
        
        char xmoves[5];
        getPlayerMoves(xmoves, ME);
        //if (xmoves[0] == 0) {
            //return true;
        //}

        char ymoves[5];
        getPlayerMoves(ymoves, THEM);
        //if (ymoves[0] == 0) {
            //return true;
        //}

        if (xmoves[0] != 0 && ymoves[0] != 0) {
            return false;
        } else  if (xmoves[0] == 0 && ymoves[0] == 0) {
            utility = -1;
            return true;
        } else if (xmoves[0] == 0 && ymoves[0] != 0) {
            utility = -10000;
            return true;
        } else if (xmoves[0] != 0 && ymoves[0] == 0) {
            utility = 10000;
            return true;
        } else {
            cerr << "Something wrong here" << endl;
        }

        return false;
    }

    bool monoTerminal() {

        
        if (map[py][px] != playerSymbol[ME] && (ox != px || oy != py)) {
            //debug("weird stuff\n");
            //this->printBoard();
            //exit(1);
            utility = -5000;
            return true;
        }

        if (game_done && utility != 0) {
            //debug("easy stuff\n");
            return true;
        }
        
        char xmoves[5];
        getPlayerMoves(xmoves, ME);
        if (xmoves[0] == 0) {
            //debug("zero moves\n");
            return true;
        }

        //if (xmoves[0] != 0 && ymoves[0] != 0) {
            //return false;
        //} else  if (xmoves[0] == 0 && ymoves[0] == 0) {
            //utility = -1;
            //return true;
        //} else if (xmoves[0] == 0 && ymoves[0] != 0) {
            //utility = -10000;
            //return true;
        //} else if (xmoves[0] != 0 && ymoves[0] == 0) {
            //utility = 10000;
            //return true;
        //} else {
            //cerr << "Something wrong here" << endl;
        //}

        return false;
    }

    int getUtility() {
        if (utility == 0) {
            // Define util here
            //
            int voro = 2*this->voronoi();

            return voro;
        }
        return utility;
    }

    void printBoard() {
        debug("-------\n");
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                debug("%c", map[y][x]);
            }
            debug("\n");
        }
        debug("-------\n");
    }

    void printBoard2(char **cmap) {
        debug("-------\n");
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                //if (cmap[y][x] < ' ') {
                    debug("%3d ", cmap[y][x]);
                //} else {
                    //debug("%2c ", cmap[y][x]);
                //}
            }
            debug("\n");
        }
        debug("-------\n");
    }

    void printBoard3(short **cmap) {
        debug("-------\n");
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                //if (cmap[y][x] < ' ') {
                    debug("%3d ", cmap[y][x]);
                //} else {
                    //debug("%2c ", cmap[y][x]);
                //}
            }
            debug("\n");
        }
        debug("-------\n");
    }

    ~Board() {
        free(map);
        map = NULL;
    }

    bool checkDir2(int dir, int x, int y, char **cmap) {
        if (x <= 0 || y <= 0 || x >= width || y >= height) {
            return false;
        }
        switch(dir){
            case NORTH:
                return cmap[y-1][x] != '#'; // || map[y-1][x] == '1' || map[y-1][x] == '2';
                break;
            case SOUTH:
                return cmap[y+1][x] != '#'; // || map[y+1][x] == '1' || map[y+1][x] == '2';
                break;
            case EAST:
                return cmap[y][x+1] != '#'; // || map[y][x+1] == '1' || map[y][x+1] == '2';
                break;
            case WEST:
                return cmap[y][x-1] != '#'; // || map[y][x-1] == '1' || map[y][x-1] == '2';
                break;
        }
    }

    void getMoves2(char a[], int posx, int posy) {
        //int tmp[] = {NORTH, SOUTH, EAST, WEST};
        int j = 0;
        for (int i = 0; i < 4; i++) {
            //debug("check %d %d\n", i, possiblemoves[i]);
            if (checkDir(possiblemoves[i], posx, posy)) a[j++] = possiblemoves[i];
        }
        a[j] = 0;
    }

    void getMoves3(char a[], char goodmoves[], int posx, int posy) {
        //int tmp[] = {NORTH, SOUTH, EAST, WEST};
        int j = 0;
        for (int i = 0; i < 4; i++) {
            if (checkDir(goodmoves[i], posx, posy)) a[j++] = goodmoves[i];
        }
        a[j] = 0;
    }

    int voronoi() {
        voronoicalls++;

        //debug("Voronoi start\n");
        char **mapcopy = allocateMap();
        //memset(mapcopy, 0, (sizeof(char*)*this->height) + (sizeof(char) * this->width * this->height));
        //memcpy(mapcopy, map, (sizeof(char*)*this->height) + (sizeof(char) * this->width * this->height));

        mapcopy[py][px] = 1;
        mapcopy[oy][ox] = -1;
        int count[5] = {};
        int countXred = 0, countYred = 0, countXblack = 0, countYblack = 0;
        queue<QueueElem> queue;
        QueueElem el = {px, py, 1};
        queue.push(el);
        while (queue.size() > 0) {
            QueueElem node = queue.front();
            queue.pop();
            //debug("pop %d\n", node.depth);

            int ax = node.x;
            int ay = node.y;
            //mapcopy[ay][ax] = node.depth;

            int nMoves = 0;
            char moves[5];
            this->getMoves2(moves, ax, ay);
            for (char *move = moves; *move != 0; ++move, ++nMoves) {
                //debug("Move %d\n", *move);
                int x = ax, y = ay;
                getNewPos(*move, x, y);
                //if (map[y][x] != ' ') continue;
                if (mapcopy[y][x] == 0) {
                    mapcopy[y][x] = node.depth+1;
                    count[ME]++;
                    if ((x % 2 == 1 && y % 2 == 1) || (x % 2 == 0 && y % 2 == 0))
                        countXred++;
                    else
                        countXblack++;
                    
                    QueueElem elem = {x, y, node.depth+1};
                    queue.push(elem);
                    //debug("Append %d, %d = %d\n", x, y, node.depth+1);
                }
            }
        }

        //debug("#############\n");

        mapcopy[oy][ox] = -1;
        QueueElem el2 = {ox, oy, -1};
        queue.push(el2);
        while (queue.size() > 0) {
            QueueElem node = queue.front();
            queue.pop();
            //debug("pop %d\n", node.depth);

            int ax = node.x;
            int ay = node.y;
            //mapcopy[ay][ax] = node.depth;
            //debug("%d %d\n", ax, ay);

            int nMoves = 0;
            char moves[5];
            this->getMoves2(moves, ax, ay);
            for (char *move = moves; *move != 0; ++move, ++nMoves) {
                //debug("Move %d\n", *move);
                int x = ax, y = ay;
                getNewPos(*move, x, y);
                
                //if (map[y][x] != ' ') continue;

                if (mapcopy[y][x] == 0) {
                    mapcopy[y][x] = node.depth-1;
                    count[THEM]++;
                    if ((x % 2 == 1 && y % 2 == 1) || (x % 2 == 0 && y % 2 == 0))
                        countYred++;
                    else
                        countYblack++;
                    QueueElem elem = {x, y, node.depth-1};
                    queue.push(elem);
                    //debug("Append %d, %d = %d\n", x, y, node.depth-1);
                } else if (mapcopy[y][x] > -(node.depth-1)) {
                    // Takin' ova'
                    count[ME]--;
                    count[THEM]++;
                    if ((x % 2 == 1 && y % 2 == 1) || (x % 2 == 0 && y % 2 == 0)) {
                        countXred--;
                        countYred++;
                    } else {
                        countXblack--;
                        countYblack++;
                    }
                    mapcopy[y][x] = node.depth-1;
                    QueueElem elem = {x, y, node.depth-1};
                    queue.push(elem);
                    //debug("takeover %d, %d = %d\n", x, y, node.depth-1);
                } else if (mapcopy[y][x] == -(node.depth-1)) {
                    // Sharing is caring
                    count[ME]--;
                    if ((x % 2 == 1 && y % 2 == 1) || (x % 2 == 0 && y % 2 == 0))
                        countXred--;
                    else        
                        countXblack--;
                    mapcopy[y][x] = -127;
                    QueueElem elem = {x, y, node.depth-1};
                    queue.push(elem);
                    //debug("Test %d, %d = %d\n", x, y, node.depth-1);
                }
            }
        }


        //for (int i = 0; i < 4; i++) {
            //debug("count %d, %d\n", i, count[i]);
        //}

        //debug("Voronoi done\n");
        //

        assert(countYred+countYblack == count[THEM]);
        assert(countXred+countXblack == count[ME]);

        int countX = 0, countY = 0;
        if ((px % 2 == 1 && py % 2 == 1) || (px % 2 == 0 && py % 2 == 0)) {
            // red
            countX = 1+(2*min( countXblack-1, countXred));
        } else {
            // black
            countX = 1+(2*min(countXblack, countXred-1));
        }

        if ((ox % 2 == 1 && oy % 2 == 1) || (ox % 2 == 0 && oy % 2 == 0)) {
            countY = 1+(2*min( countYblack-1, countYred));
            //countY = countYblack-1 +countYred;
        } else {
            //countY = (1+min(countYblack, countYred-1) * 2);
            countY = 1+(2*min(countYblack, countYred-1));
            //countY = (countYred-1) + countYblack;
        }
        countX = min(countX, (countXred+countXblack));
        countY = min(countY, (countYred+countYblack));
        countX = max(countX, 0);
        countY = max(countY, 0);

        //if (countXred - countXblack > 1) {
            //debug("X red: %d black: %d, total: %d, count: %d, new: %d\n", countXred, countXblack, countXred+countXblack, count[ME], countX);
            //debug("Y red: %d black: %d, total: %d, count: %d, new: %d\n", countYred, countYblack, countYred+countYblack, count[THEM], countY);       
            //this->printBoard();
            //this->printBoard2(mapcopy);
        //}

        //if (countX > count[ME]) {
            //debug("WOOOT\n");
            //printBoard2(mapcopy);
        //}

        //if (countX - countY != count[ME] - count[THEM])
            //debug("%d %d\n", countX - countY, count[ME] - count[THEM]);

        free(mapcopy);

        return countX - countY; //count[ME] - count[THEM];
    }

    int monoVoronoi() {
        voronoicalls++;

        //debug("Voronoi start\n");
        char **mapcopy = allocateMap();
        //memset(mapcopy, 0, (sizeof(char*)*this->height) + (sizeof(char) * this->width * this->height));
        //memcpy(mapcopy, map, (sizeof(char*)*this->height) + (sizeof(char) * this->width * this->height));

        mapcopy[py][px] = 1;
        mapcopy[oy][ox] = -1;
        int count[5] = {};
        int countXred = 0, countYred = 0, countXblack = 0, countYblack = 0;
        queue<QueueElem> queue;
        QueueElem el = {px, py, 1};
        queue.push(el);
        while (queue.size() > 0) {
            QueueElem node = queue.front();
            queue.pop();

            int ax = node.x;
            int ay = node.y;

            int nMoves = 0;
            char moves[5];
            this->getMoves2(moves, ax, ay);
            for (char *move = moves; *move != 0; ++move, ++nMoves) {
                int x = ax, y = ay;
                getNewPos(*move, x, y);
                if (mapcopy[y][x] == 0) {
                    mapcopy[y][x] = node.depth+1;
                    count[ME]++;
                    if ((x % 2 == 1 && y % 2 == 1) || (x % 2 == 0 && y % 2 == 0))
                        countXred++;
                    else
                        countXblack++;
                    
                    QueueElem elem = {x, y, node.depth+1};
                    queue.push(elem);
                }
            }
        }

        assert(countXred+countXblack == count[ME]);

        int countX = 0, countY = 0;
        if ((px % 2 == 1 && py % 2 == 1) || (px % 2 == 0 && py % 2 == 0)) {
            // red
            countX = 1+(2*min( countXblack-1, countXred));
        } else {
            // black
            countX = 1+(2*min(countXblack, countXred-1));
        }
        countX = min(countX, (countXred+countXblack));
        countX = max(countX, 0);

        free(mapcopy);

        return countX;
    }

    bool arePlayersConnected() {

        char **mapcopy = allocateMap();

        mapcopy[py][px] = 1;
        mapcopy[oy][ox] = -1;
        int count[5] = {};
        queue<QueueElem> queue;
        QueueElem el = {px, py, 1};
        QueueElem el2 = {ox, oy, -1};
        queue.push(el);
        while (queue.size() > 0) {
            QueueElem node = queue.front();
            queue.pop();
            //debug("pop %d\n", node.depth);

            int ax = node.x;
            int ay = node.y;
            //mapcopy[ay][ax] = node.depth;

            int nMoves = 0;
            char moves[5];
            this->getMoves2(moves, ax, ay);
            for (char *move = moves; *move != 0; ++move, ++nMoves) {
                //debug("Move %d\n", *move);
                int x = ax, y = ay;
                getNewPos(*move, x, y);
                //if (map[y][x] != ' ') continue;
                if (mapcopy[y][x] == 0) {
                    mapcopy[y][x] = node.depth + (node.depth > 0 ? 1 : -1);
                    count[ME]++;
                    QueueElem elem = {x, y, node.depth+1};
                    queue.push(elem);
                    //debug("Append %d, %d = %d\n", x, y, node.depth+1);
                } else if (node.depth > 0 && mapcopy[y][x] < 0) {
                    return true;
                } else if (node.depth < 0 && mapcopy[y][x] > 0) {
                    return true;
                }
            }
        }
        return false;
    }

    int warn() {
        warncalls++;
        short **mapcopy = allocateShortMap(); 
        //this->printBoard();

        int count = 1;
//        first = None
//        pos = start
        int posx = px, posy = py;
        while (1) {
            //debug("pop %d %d\n", posx, posy);
            char lowestx = 0, lowesty = 0;
            int x, y;
            //char neighbors[5];
            int minNeigh = 1337;
            int nMoves = 0;
            int tmp;
            char moves[5];
            this->getMoves2(moves, posx, posy);
            for (char *move = moves; *move != 0; ++move, ++nMoves) {
                x = posx;
                y = posy;
                //debug("move %d\n", *move);
                getNewPos(*move, x, y);
                if (map[y][x] == ' ' && mapcopy[y][x] == 0) {
                    //debug("neig %d %d\n", x, y);
                    tmp = 0;
                    int nMoves2 = 0;
                    char moves2[5];
                    this->getMoves2(moves2, x, y);
                    for (char *move2 = moves2; *move2 != 0; ++move2, ++nMoves2) {
                        int x2 = x, y2 = y;
                        getNewPos(*move2, x2, y2);
                        if (map[y2][x2] == ' ' && mapcopy[y2][x2] == 0) {
                            tmp++;
                        }
                    }
                    //debug("degree %d\n", tmp);
                    //if (tmp == 0) continue;
                    if (tmp < minNeigh) {
                        minNeigh = tmp;
                        lowestx = x;
                        lowesty = y;
                    }
                }

                //x, y = dest = x+tabx[dir], y+taby[dir]
                //#x,y = dest = self.rel(dir, pos)
                //if cb[y][x] == FLOOR:
                    //for dir2 in DIRECTIONS:
                        //#x2,y2 = self.rel(dir2, dest)
                        //x2, y2 =x+tabx[dir2], y+taby[dir2]
                        //temp = 0
                        //if cb[y2][x2] == FLOOR:
                            //temp+=1
                        //if temp == 0: continue
                        //if temp < minNeigh:
                            //minNeigh = temp
                            //lowest = dest
                    //neighbors.append((dir, dest))
            }

            
            //x, y = pos = lowest
            //x = px;
            //y = py;
            //getNewPos(lowest, x, y);
            //debug("Lowest %d %d = %d\n", lowestx, lowesty, count);
            mapcopy[posy][posx] = count++;
            posx = lowestx;
            posy = lowesty;
            if (lowestx == 0 && lowesty == 0) {
                break;
            }

        }
        //debug("count: %d\n", count);

        //if (count > 100)
            //printBoard3(mapcopy);

        free(mapcopy);

        return count;
    }

};

class Game {
public:
    int width;
    int height;
    Board *board;

    Game()
    : board(NULL) {
        
    }

    ~Game() {
        delete board;
        board = NULL;
    }

    void readFromFile(FILE *file_handle) {

        int num_items = fscanf(file_handle, "%d %d\n", &width, &height);
        if (feof(file_handle) || num_items < 2) {
            exit(0); // End of stream means end of game-> Just exit.
        }

        if (board == NULL) {
            board = new Board(width, height);
        }

        int x = 0;
        int y = 0;
        int c;
        while (y < height && (c = fgetc(file_handle)) != EOF) {
            switch (c) {
                case '\r':
                    break;
                case '\n':
                    if (x != width) {
                        debug("x != width in Board_ReadFromStream\n");
                        return ;
                    }
                    ++y;
                    x = 0;
                    break;
                case '#':
                    if (x >= width) {
                        debug("x >= width in Board_ReadFromStream\n");
                        return ;
                    }
                    board->map[y][x] = '#';
                    ++x;
                    break;
                case ' ':
                    if (x >= width) {
                        debug("x >= width in Board_ReadFromStream\n");
                        return ;
                    }
                    board->map[y][x] = ' ';
                    ++x;
                    break;
                case '1':
                    if (x >= width) {
                        debug("x >= width in Board_ReadFromStream\n");
                        return ;
                    }
                    board->map[y][x] = '1';
                    board->px = x;
                    board->py = y;
                    ++x;
                    break;
                case '2':
                    if (x >= width) {
                        debug("x >= width in Board_ReadFromStream\n");
                        return ;
                    }
                    board->map[y][x] = '2';
                    board->ox = x;
                    board->oy = y;
                    ++x;
                    break;
                default:
                    debug("unexpected character %d in Board_ReadFromStream", c);
                    return ;
            }
        }
    }
};

int min_player(Board *board, int maxdepth, int depth, int alpha, int beta);

int max_player(Board *board, int maxdepth, int depth, int alpha, int beta) {
    calls++;

    if (timeout) {
        throw TimeoutException();
    }

    if (depth >= maxdepth) {
        // return utility
        int util = board->getUtility();
        //if (util == -194) {
            //debug("Done by depth\n");
            //debug("Utility: %d", util);
            //board->printBoard();
        //}
        return util;
        //return 0;
    }

    if (board->terminal_test()) {
        int util = board->getUtility();
        //tab(depth); debug("Done by terminal");
        //debug("Utility: %d", util);
        //board->printBoard();
        return util; 
    }

    int max = -infinity;
    int result = 0;
    int results[4];
    int nMoves = 0;

    char moves[5];
    board->getMoves(moves, maxmoves[depth]);
    for (char *move = moves; *move != 0; ++move, ++nMoves) {
        //tab(depth); printf("max Enumerating move: %d\n", *move);
        int oldposx = board->px;
        int oldposy = board->py;
        //cout << oldposx << " " << oldposy << endl;
        int oldVal = board->doMove(*move);
        board->to_move = 1;
        //board->printBoard();
        result = min_player(board, maxdepth, depth+1, alpha, beta);
        results[nMoves] = result;
        board->to_move = 0;
        board->undoMove(*move, oldVal, oldposx, oldposy);

        if (result >= beta) {
            return result;
        }
        if (result > alpha) {
            alpha = result;

            if (maxmoves[depth][0] != *move) {
                int oldpos = 0;
                for (int i = 0; i < 4; i++) {
                    if (maxmoves[depth][i] == *move) {
                        oldpos = i;
                        break;
                    }
                }
                swap(maxmoves[depth][oldpos], maxmoves[depth][0]);
            }
        }

        if (result > max) {
            max = result;
            //best = *move;
        }
    }
    
    //tab2(depth); debug2("max results: ");
    //for (int i = 0; i < nMoves; ++i) {
        //debug2("(%d, %d) ", moves[i], results[i]);
    //}
    //debug2("\n");

    return max;
}

int min_player(Board *board, int maxdepth, int depth, int alpha, int beta) {
    calls++;

    if (timeout) {
        throw TimeoutException();
    }

    //if (depth >= maxdepth) {
        // return utility
        //cerr << "Done by depth" << endl;
        //return 0;
    //}

    ////if (board->terminal_test()) {
        //cerr << "Done by terminal" << endl;
        //board->printBoard();
        //return board->getUtility(); 
    //}

    int min = +infinity;
    int result = 0;
    int results[4];
    int nMoves = 0;

    bool ahah = false;
    char moves[5];
    board->getMoves(moves, minmoves[depth]);
    if (moves[0] == 0 && board->game_done) {
        // Hack to avoid errors on draws
        if (board->ox <= 1)
            moves[0] = 2;
        else 
            moves[0] = 4;
        moves[1] = 0;
        ahah = true;
    }
    for (char *move = moves; *move != 0; ++move, ++nMoves) {
        int oldposx = board->ox;
        int oldposy = board->oy;
        int oldVal = board->doMove(*move);
        board->to_move = 0;
        //tab(depth); debug("min Enumerating move: %d, depth: %d\n", *move, depth);
        if (ahah) {
            board->map[board->py][board->px] = '1';
        }
        result = max_player(board, maxdepth, depth+1, alpha, beta);
        board->to_move = 1;
        board->undoMove(*move, oldVal, oldposx, oldposy);
        results[nMoves] = result;

        if (result <= alpha) {
            return result;
        }
        if (result < beta) {
            beta = result;
            // update killer moves
            
            if (minmoves[depth][0] != *move) {
                int oldpos = 0;
                for (int i = 0; i < 4; i++) {
                    if (minmoves[depth][i] == *move) {
                        oldpos = i;
                        break;
                    }
                }
                //debug("old minmoves\n");
                //for (int i = 0; i < 4; i++) {
                    //debug("%d, ", minmoves[depth][i]);
                //}
                swap(minmoves[depth][oldpos], minmoves[depth][0]);
                //debug("\nold minmoves\n");
                //for (int i = 0; i < 4; i++) {
                    //debug("%d, ", minmoves[depth][i]);
                //}
                //debug("\n");
            }

        }
        
        if (result < min) {
            min = result;
        }
    }

    //tab(depth); debug("min results: ");
    //for (int i = 0; i < nMoves; ++i) {
        //debug("(%d, %d) ", moves[i], results[i]);
    //}
    //debug("\n");

    return min;
}

int globresults[4];
char globmoves[4];

int minimax(Game &game, int maxdepth) {
    int result = 0;
    int best = 1;
    int max = -infinity;

    int results[4];
    int nMoves = 0;

    
    //debug("[");
    //for (int i = 0; i < 4; ++i)
        //debug("%d", maxmoves[0][i]);
    //debug("] ");
    char moves[5];
    game.board->getMoves(moves, maxmoves[0]);
    for (char *move = moves; *move != 0; ++move, ++nMoves) {
        //debug("max Enumerating move: %d\n", *move);
            //game.board->printBoard();
        int oldposx = game.board->px;
        int oldposy = game.board->py;
        //cout << oldposx << oldposy << endl;
        int oldVal = game.board->doMove(*move);
        game.board->to_move = 1;
        //game.board->printBoard();

        result = min_player(game.board, maxdepth, 1, -infinity, infinity);
        results[nMoves] = result;
        //printf("final max result: %d, move: %d\n", result, *move);

        if (result > max) {
            max = result;
            best = *move;

            if (maxmoves[0][0] != *move) {
                int oldpos = 0;
                for (int i = 0; i < 4; i++) {
                    if (maxmoves[0][i] == *move) {
                        oldpos = i;
                        break;
                    }
                }
                swap(maxmoves[0][oldpos], maxmoves[0][0]);
            }
        }
        game.board->to_move = 0;
        game.board->undoMove(*move, oldVal, oldposx, oldposy);
    }
    //game.board->printBoard();
    //debug("max final results: [");
    //for (int i = 0; i < 4; ++i)
        //debug("%d", maxmoves[0][i]);
    //debug("] ");
    //for (int i = 0; i < nMoves; ++i) {
        //debug("(%d, %d) ", moves[i], results[i]);
    //}
    //debug("\n");
    memcpy(globresults, results, sizeof(globresults));
    memcpy(globmoves, moves, sizeof(globmoves));

    //debug("depth: %d, Final result: %d, with move: %d\n", depth, max, best);

    return best;
}

int maximax_player(Board *board, int maxdepth, int depth) {
    calls++;

    if (timeout) {
        throw TimeoutException();
    }

    if (depth >= maxdepth) {
        // return utility
        //cerr << "Done by depth" << endl;
        //int utl = depth + board->warn();
        int utl = depth + board->monoVoronoi();
        //debug("Utility: %d", utl);
        //if (utl == 130)
            //board->printBoard();
        return utl;
        //return 0;
    }

    //debug("depth %d\n", depth);
    if (board->monoTerminal()) {
        //tab(depth); debug("Done by terminal %d\n", depth);
        //debug("game done: %d\n", board->game_done);
        //board->printBoard();
        //debug("warn %d\n", board->warn());
        //return depth + board->warn();
        return depth + board->monoVoronoi();
    }

    int max = -infinity;
    int result = 0;
    int results[4];
    int nMoves = 0;

    char moves[5];
    board->getMoves(moves, maxmoves[depth]);
    for (char *move = moves; *move != 0; ++move, ++nMoves) {
        //tab(depth); printf("max Enumerating move: %d\n", *move);
        int oldposx = board->px;
        int oldposy = board->py;
        //cout << oldposx << " " << oldposy << endl;
        int oldVal = board->doMove(*move);
        //board->to_move = 1;
        //board->printBoard();
        result = maximax_player(board, maxdepth, depth+1);
        results[nMoves] = result;
        //board->to_move = 0;
        board->undoMove(*move, oldVal, oldposx, oldposy);

        //if (result >= beta) {
            //debug("prune\n");
            //return result;
        //}
        //if (result > alpha) {
            //alpha = result;

        //}

        if (result > max) {
            max = result;
            if (maxmoves[depth][0] != *move) {
                int oldpos = 0;
                for (int i = 0; i < 4; i++) {
                    if (maxmoves[depth][i] == *move) {
                        oldpos = i;
                        break;
                    }
                }
                swap(maxmoves[depth][oldpos], maxmoves[depth][0]);
            }
            //best = *move;
        }
    }
    
    //tab(depth); debug("max results: ");
    //for (int i = 0; i < nMoves; ++i) {
        //debug("(%d, %d) ", moves[i], results[i]);
    //}
    //debug("\n");

    return max;
}

int maximax(Game &game, int depth) {

    int result = 0;
    int best = 1;
    int max = -infinity;

    int results[4];
    int nMoves = 0;

    char moves[5];
    game.board->getMoves(moves, maxmoves[0]);
    for (char *move = moves; *move != 0; ++move, ++nMoves) {
        //debug("max Enumerating move: %d\n", *move);
        int oldposx = game.board->px;
        int oldposy = game.board->py;
        //cout << oldposx << oldposy << endl;
        int oldVal = game.board->doMove(*move);
        //game.board->to_move = 1;
        //debug("inside maximax %d %d %d %d\n", depth, *move, oldposx, oldposy);
        //game.board->printBoard();

        result = maximax_player(game.board, depth, 1);
        results[nMoves] = result;
        //debug("final max result: %d, move: %d\n", result, *move);

        if (result > max) {
            max = result;
            best = *move;
        }
        //game.board->to_move = 0;
        game.board->undoMove(*move, oldVal, oldposx, oldposy);
        
    }
    //debug("max final results: ");
    //for (int i = 0; i < nMoves; ++i) {
        //debug("(%d, %d) ", moves[i], results[i]);
    //}
    //debug("\n");
    memcpy(globresults, results, sizeof(globresults));
    memcpy(globmoves, moves, sizeof(globmoves));

    //debug("depth: %d, Final result: %d, with move: %d\n", depth, max, best);

    return best;
}


int main() {
    srand(time(0));

    for (int i = 0; i < 2500; i++) {
        for (int j = 0; j < 4; j++) {
            maxmoves[i][j] = j+1;
            minmoves[i][j] = j+1;
            //memoizedmoves[i][j] = j+1;
        }
    }

    //set_terminate(__gnu_cxx::__verbose_terminate_handler);

    Game game;

    struct sigaction sact;
    sigemptyset( &sact.sa_mask );
    sact.sa_flags = SA_NODEFER;
    //sact.sa_flags = 0;
    sact.sa_handler = myhandler;
    sigaction( SIGALRM, &sact, NULL );
    //sigaction( SIGINT, &sact, NULL );

    struct itimerval ovalue, pvalue;
    struct itimerval alarmtimer = {};
    alarmtimer.it_value.tv_sec = 0;
    alarmtimer.it_value.tv_usec = TIMEOUT; //500000;//950000;
    alarmtimer.it_interval.tv_sec = 0;
    alarmtimer.it_interval.tv_usec = 0;

    int bestmove = 1;
    int depth;
    try {
        while (true) {
            
            double startTime = 0;
            try {
                timeout = 0;
                bestmove = (rand()%4)+1;
                //alrmcount = 0;

                //debug("READING BOARD %f\n", getTime()-startTime);
                game.readFromFile(stdin);
                startTime = getTime();
                game.board->to_move = ME; // Important
                game.board->utility = 0;
                game.board->numMoves = 0;
                game.board->game_done = false;
                //debug("DONE READING BOARD %f\n", getTime()-startTime);
                //debug("before\n");
                //game.board->printBoard();

                //game.board->voronoi();
                //game.board->warn();
                //continue;

                int result = setitimer(ITIMER_REAL, &alarmtimer, NULL);

                if (game.board->arePlayersConnected()) {
                    //debug("Players are connected\n");

                    for (depth = 2; depth < 2500; depth += 2) {
                        bestmove = minimax(game, depth);
                        //debug("minimax done depth %d time %f bestmove %d\n", depth, getTime()-startTime, bestmove);
                    }
                    debug("DONE depth %d, calls %d, best: %d\n", depth, calls, bestmove);

                } else {
                    //debug("maximax\n");
                    //game.board->printBoard();
                    for (depth = 1; depth < 2500; depth++) {
                        bestmove = maximax(game, depth);
                    }
                    debug("maximax done depth %d time %f warncalls %d calls %d\n", depth, getTime()-startTime, warncalls, calls);
                    
                }
                //char moves[5];
                //game.board->getMoves(moves);
                //for (char *p = moves; *p != 0; ++p) {
                    //debug("%d\n", *p);
                //}

            } catch (TimeoutException &e) {
                //debug("Exception\n");
                //debug("%f\n", getTime() - startTime);
                debug("not done depth %d, calls %d, voronoi %d, warn %d, best: %d\n", depth, calls, voronoicalls, warncalls, bestmove);
            }

            struct itimerval value;
            getitimer( ITIMER_REAL, &value );
            value.it_value.tv_sec = 0;
            value.it_value.tv_usec = 0;
            setitimer( ITIMER_REAL, &value, NULL );
            
            debug("OUTPUT VALUE %d time: %f\n", bestmove, getTime() - startTime);

            fprintf(stdout, "%d\n", bestmove);
            fflush(stdout);

            //debug("after\n");
            //game.board->printBoard();

            debug("max final results: ");
            for (int i = 0; i < 4; ++i) {
                debug("(%d, %d) ", globmoves[i], globresults[i]);
            }
            debug("\n");

            for (int i = 2; i < 1000; ++i) {
                for (int j = 0; j < 4; ++j) {
                    maxmoves[i-2][j] = maxmoves[i][j];  
                    minmoves[i-2][j] = minmoves[i][j];  
                }
            }
            //memcpy(maxmoves, maxmoves+2, sizeof(maxmoves)-2*sizeof(maxmoves[0]));
            //memcpy(minmoves, minmoves+2, sizeof(minmoves)-2*sizeof(minmoves[0]));
            //for (int i = 2500-8; i < 2500; i++) {
                //for (int j = 0; j < 4; j++) {
                    //maxmoves[i][j] = j+1;
                    //minmoves[i][j] = j+1;
                    ////debug("%d %d =  %d \n", i, j, maxmoves[i][j]);
                //}
            //}

            calls = 0;
            voronoicalls = 0;
            warncalls = 0;
        }
    } catch (...) {
        fprintf(stderr, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stderr, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stderr, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stderr, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stdout, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stdout, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stdout, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
        fprintf(stdout, "ERRRRRRRRRRRRRRRRRRRRRRRRRROR\n");
    }
    
    return 0;
}
