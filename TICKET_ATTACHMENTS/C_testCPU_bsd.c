#include <kvm.h>
#include <stdio.h>
#include <stdarg.h>
#include <sys/resource.h>
#include <sys/types.h> 
#include <sys/ptrace.h>
#include <unistd.h> 
#include <signal.h>
#include <sys/sysctl.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/user.h>

#define RUSAGE_SELF 0
#define RUSAGE_CHILDREN -1

int main (int argc, char const *argv[]) {
	long seconds = 0;
	long microseconds = 0;
	
	/* Get the resource usage data */
	struct rusage ru;
	int status = getrusage(RUSAGE_SELF, &ru);
	printf("%d\n", status);
	
	int num = 2;
	do {
		/* Add user time */
		seconds += ru.ru_utime.tv_sec;
		microseconds += ru.ru_utime.tv_usec;

		/* Add system time */
		seconds += ru.ru_stime.tv_sec;
		microseconds += ru.ru_stime.tv_usec;
		
		num--;
		
		/* Point to the new rusage struct */
		status = getrusage(RUSAGE_CHILDREN, &ru);
	} while (num > 0);
	
	printf("%ld %ld\n", seconds, microseconds);
	
	return 0;
}
