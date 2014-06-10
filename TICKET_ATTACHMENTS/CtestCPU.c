#include <stdio.h>
#include <stdarg.h>
#include <mach/mach.h>
#include <mach/mach_error.h>
#include <mach/mach_host.h>
#include <mach/mach_init.h>
#include <mach/mach_time.h>
#include <mach/vm_statistics.h>
#include <sys/sysctl.h>
#include <sys/errno.h>

#define PID 2008

extern int proc_pidinfo(int pid, int flavor, uint64_t arg,  void *buffer, int buffersize);
struct proc_taskinfo {
        uint64_t                pti_virtual_size;   /* virtual memory size (bytes) */
        uint64_t                pti_resident_size;  /* resident memory size (bytes) */
        uint64_t                pti_total_user;         /* total time */
        uint64_t                pti_total_system;
        uint64_t                pti_threads_user;       /* existing threads only */
        uint64_t                pti_threads_system;
        int32_t                 pti_policy;             /* default policy for new threads */
        int32_t                 pti_faults;             /* number of page faults */
        int32_t                 pti_pageins;    /* number of actual pageins */
        int32_t                 pti_cow_faults; /* number of copy-on-write faults */
        int32_t                 pti_messages_sent;      /* number of messages sent */
        int32_t                 pti_messages_received; /* number of messages received */
        int32_t                 pti_syscalls_mach;  /* number of mach system calls */
        int32_t                 pti_syscalls_unix;  /* number of unix system calls */
        int32_t                 pti_csw;            /* number of context switches */
        int32_t                 pti_threadnum;          /* number of threads in the task */
        int32_t                 pti_numrunning;         /* number of running threads */
        int32_t                 pti_priority;           /* task priority*/
};
#define PROC_PIDTASKINFO 4

int main (int argc, char const *argv[]) {
	struct proc_taskinfo tinfo;
	printf("%d\n",PID);
	int nb = proc_pidinfo(PID, PROC_PIDTASKINFO, 0,  &tinfo, sizeof(struct proc_taskinfo));
	printf("%d\n",nb);
	
	printf("%llu %llu\n",tinfo.pti_total_user, tinfo.pti_total_system);
	printf("%f %f\n",(double)tinfo.pti_total_user/1000000000, (double)tinfo.pti_total_system/1000000000);
	
	return 0;
}