#include <stdio.h>
#include <stdarg.h>
#include <sys/types.h>
#include <stdlib.h>
#include <sys/sysctl.h>
#include <sys/user.h>
#include <sys/resource.h>

int main (int argc, char const *argv[]) {
	int mib[4];
	struct kinfo_proc *kp;
	size_t bufSize = 0;
	
	int pid = 72615;

	mib[0] = CTL_KERN;
	mib[1] = KERN_PROC;
	mib[2] = KERN_PROC_PID;
	mib[3] = pid;
	
	if ( sysctl( mib, 4, NULL, &bufSize, NULL, 0 ) < 0 ) {
		printf("Sysclt failed!\n");
	}
	
	kp = (struct kinfo_proc *)malloc(bufSize);
	
	if (sysctl(mib, 4, kp, &bufSize, NULL, 0) < 0) {
		printf("Sysclt failed!\n");
	}

	struct rusage ru = kp->ki_rusage;
	printf("%d %d\n", ru.ru_utime.tv_sec, ru.ru_utime.tv_usec);
	
	printf("%d %d\n", ru.ru_stime.tv_sec, ru.ru_stime.tv_usec);
	
	return 0;
}
