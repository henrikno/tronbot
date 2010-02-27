
CFLAGS=-ggdb2 -Wall -Wextra
CFLAGS=-O3 #-fprofile-use #-fprofile-generate
SOURCES=MyTronBot.o utils.o

all: MyTronBot

MyTronBot: ${SOURCES} Makefile
	g++ ${CFLAGS} -o MyTronBot ${SOURCES}

MyTronBot.o: MyTronBot.cc Makefile
	g++ ${CFLAGS} -c -o MyTronBot.o MyTronBot.cc

utils.o: utils.cc Makefile
	g++ ${CFLAGS} -c -o utils.o utils.cc

clean:
	rm ${SOURCES}
