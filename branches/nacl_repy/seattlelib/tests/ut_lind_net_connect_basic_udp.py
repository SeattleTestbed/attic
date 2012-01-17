import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError

# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)

# should be okay...
lind_net_calls.connect_syscall(sockfd,'127.0.0.1',50103)

# bind will not be interesting...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)


# I should be able to retarget it...
lind_net_calls.connect_syscall(sockfd,'127.0.0.1',50104)
