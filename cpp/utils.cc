#include <sys/time.h>
#include <cstdlib>
#include <cstdio>

double getTime() {
    struct timeval TV;
    const int RC = gettimeofday(&TV, NULL);
    if(RC == -1)
    {
        printf("ERROR: Bad call to gettimeofday\n");
        return(-1);
    }
    return( ((double)TV.tv_sec) + 1e-6 * ((double)TV.tv_usec) );
}
