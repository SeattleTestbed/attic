from ctypes import *

STRING = c_char_p


class kinfo_proc(Structure):
    pass
class pargs(Structure):
    pass
class proc(Structure):
    pass
class user(Structure):
    pass
class vnode(Structure):
    pass
class filedesc(Structure):
    pass
class vmspace(Structure):
    pass
__int32_t = c_int
__pid_t = __int32_t
pid_t = __pid_t
__uint32_t = c_uint
__dev_t = __uint32_t
dev_t = __dev_t
class __sigset(Structure):
    pass
__sigset._fields_ = [
    ('__bits', __uint32_t * 4),
]
__sigset_t = __sigset
sigset_t = __sigset_t
__uid_t = __uint32_t
uid_t = __uid_t
__gid_t = __uint32_t
gid_t = __gid_t
__vm_size_t = __uint32_t
vm_size_t = __vm_size_t
__segsz_t = __int32_t
segsz_t = __segsz_t
u_short = c_ushort
__fixpt_t = __uint32_t
fixpt_t = __fixpt_t
u_int = c_uint
__uint64_t = c_ulonglong
u_int64_t = __uint64_t
class timeval(Structure):
    pass
__time_t = __int32_t
time_t = __time_t
__suseconds_t = c_long
suseconds_t = __suseconds_t
timeval._fields_ = [
    ('tv_sec', time_t),
    ('tv_usec', suseconds_t),
]
u_char = c_ubyte
__lwpid_t = __int32_t
lwpid_t = __lwpid_t
class priority(Structure):
    pass
priority._fields_ = [
    ('pri_class', u_char),
    ('pri_level', u_char),
    ('pri_native', u_char),
    ('pri_user', u_char),
]
class rusage(Structure):
    pass
rusage._fields_ = [
    ('ru_utime', timeval),
    ('ru_stime', timeval),
    ('ru_maxrss', c_long),
    ('ru_ixrss', c_long),
    ('ru_idrss', c_long),
    ('ru_isrss', c_long),
    ('ru_minflt', c_long),
    ('ru_majflt', c_long),
    ('ru_nswap', c_long),
    ('ru_inblock', c_long),
    ('ru_oublock', c_long),
    ('ru_msgsnd', c_long),
    ('ru_msgrcv', c_long),
    ('ru_nsignals', c_long),
    ('ru_nvcsw', c_long),
    ('ru_nivcsw', c_long),
]
class pcb(Structure):
    pass
kinfo_proc._pack_ = 4
kinfo_proc._fields_ = [
    ('ki_structsize', c_int),
    ('ki_layout', c_int),
    ('ki_args', POINTER(pargs)),
    ('ki_paddr', POINTER(proc)),
    ('ki_addr', POINTER(user)),
    ('ki_tracep', POINTER(vnode)),
    ('ki_textvp', POINTER(vnode)),
    ('ki_fd', POINTER(filedesc)),
    ('ki_vmspace', POINTER(vmspace)),
    ('ki_wchan', c_void_p),
    ('ki_pid', pid_t),
    ('ki_ppid', pid_t),
    ('ki_pgid', pid_t),
    ('ki_tpgid', pid_t),
    ('ki_sid', pid_t),
    ('ki_tsid', pid_t),
    ('ki_jobc', c_short),
    ('ki_spare_short1', c_short),
    ('ki_tdev', dev_t),
    ('ki_siglist', sigset_t),
    ('ki_sigmask', sigset_t),
    ('ki_sigignore', sigset_t),
    ('ki_sigcatch', sigset_t),
    ('ki_uid', uid_t),
    ('ki_ruid', uid_t),
    ('ki_svuid', uid_t),
    ('ki_rgid', gid_t),
    ('ki_svgid', gid_t),
    ('ki_ngroups', c_short),
    ('ki_spare_short2', c_short),
    ('ki_groups', gid_t * 16),
    ('ki_size', vm_size_t),
    ('ki_rssize', segsz_t),
    ('ki_swrss', segsz_t),
    ('ki_tsize', segsz_t),
    ('ki_dsize', segsz_t),
    ('ki_ssize', segsz_t),
    ('ki_xstat', u_short),
    ('ki_acflag', u_short),
    ('ki_pctcpu', fixpt_t),
    ('ki_estcpu', u_int),
    ('ki_slptime', u_int),
    ('ki_swtime', u_int),
    ('ki_spareint1', c_int),
    ('ki_runtime', u_int64_t),
    ('ki_start', timeval),
    ('ki_childtime', timeval),
    ('ki_flag', c_long),
    ('ki_kiflag', c_long),
    ('ki_traceflag', c_int),
    ('ki_stat', c_char),
    ('ki_nice', c_byte),
    ('ki_lock', c_char),
    ('ki_rqindex', c_char),
    ('ki_oncpu', u_char),
    ('ki_lastcpu', u_char),
    ('ki_ocomm', c_char * 17),
    ('ki_wmesg', c_char * 9),
    ('ki_login', c_char * 18),
    ('ki_lockname', c_char * 9),
    ('ki_comm', c_char * 20),
    ('ki_emul', c_char * 17),
    ('ki_sparestrings', c_char * 68),
    ('ki_spareints', c_int * 10),
    ('ki_jid', c_int),
    ('ki_numthreads', c_int),
    ('ki_tid', lwpid_t),
    ('ki_pri', priority),
    ('ki_rusage', rusage),
    ('ki_rusage_ch', rusage),
    ('ki_pcb', POINTER(pcb)),
    ('ki_kstack', c_void_p),
    ('ki_udata', c_void_p),
    ('ki_spareptrs', c_void_p * 7),
    ('ki_sparelongs', c_long * 12),
    ('ki_sflag', c_long),
    ('ki_tdflags', c_long),
]
class savefpu(Union):
    pass
class save87(Structure):
    pass
class env87(Structure):
    pass
env87._fields_ = [
    ('en_cw', c_long),
    ('en_sw', c_long),
    ('en_tw', c_long),
    ('en_fip', c_long),
    ('en_fcs', u_short),
    ('en_opcode', u_short),
    ('en_foo', c_long),
    ('en_fos', c_long),
]
class fpacc87(Structure):
    pass
fpacc87._fields_ = [
    ('fp_bytes', u_char * 10),
]
save87._fields_ = [
    ('sv_env', env87),
    ('sv_ac', fpacc87 * 8),
    ('sv_pad0', u_char * 4),
    ('sv_pad', u_char * 64),
]
class savexmm(Structure):
    pass
class envxmm(Structure):
    pass
__uint16_t = c_ushort
u_int16_t = __uint16_t
u_int32_t = __uint32_t
envxmm._fields_ = [
    ('en_cw', u_int16_t),
    ('en_sw', u_int16_t),
    ('en_tw', u_int16_t),
    ('en_opcode', u_int16_t),
    ('en_fip', u_int32_t),
    ('en_fcs', u_int16_t),
    ('en_pad0', u_int16_t),
    ('en_foo', u_int32_t),
    ('en_fos', u_int16_t),
    ('en_pad1', u_int16_t),
    ('en_mxcsr', u_int32_t),
    ('en_mxcsr_mask', u_int32_t),
]
class N7savexmm3DOLLAR_1E(Structure):
    pass
N7savexmm3DOLLAR_1E._fields_ = [
    ('fp_acc', fpacc87),
    ('fp_pad', u_char * 6),
]
class xmmacc(Structure):
    pass
xmmacc._fields_ = [
    ('xmm_bytes', u_char * 16),
]
savexmm._fields_ = [
    ('sv_env', envxmm),
    ('sv_fp', N7savexmm3DOLLAR_1E * 8),
    ('sv_xmm', xmmacc * 8),
    ('sv_pad', u_char * 224),
]
savefpu._fields_ = [
    ('sv_87', save87),
    ('sv_xmm', savexmm),
]
caddr_t = STRING
class segment_descriptor(Structure):
    pass
segment_descriptor._fields_ = [
    ('sd_lolimit', c_uint, 16),
    ('sd_lobase', c_uint, 24),
    ('sd_type', c_uint, 5),
    ('sd_dpl', c_uint, 2),
    ('sd_p', c_uint, 1),
    ('sd_hilimit', c_uint, 4),
    ('sd_xx', c_uint, 2),
    ('sd_def32', c_uint, 1),
    ('sd_gran', c_uint, 1),
    ('sd_hibase', c_uint, 8),
]
class pcb_ext(Structure):
    pass
u_long = c_ulong
pcb._fields_ = [
    ('pcb_cr3', c_int),
    ('pcb_edi', c_int),
    ('pcb_esi', c_int),
    ('pcb_ebp', c_int),
    ('pcb_esp', c_int),
    ('pcb_ebx', c_int),
    ('pcb_eip', c_int),
    ('pcb_dr0', c_int),
    ('pcb_dr1', c_int),
    ('pcb_dr2', c_int),
    ('pcb_dr3', c_int),
    ('pcb_dr6', c_int),
    ('pcb_dr7', c_int),
    ('pcb_save', savefpu),
    ('pcb_flags', u_int),
    ('pcb_onfault', caddr_t),
    ('pcb_gs', c_int),
    ('pcb_fsd', segment_descriptor),
    ('pcb_gsd', segment_descriptor),
    ('pcb_ext', POINTER(pcb_ext)),
    ('pcb_psl', c_int),
    ('pcb_vm86', u_long * 2),
]
class file(Structure):
    pass
class sx(Structure):
    pass
class lock_object(Structure):
    pass
class N11lock_object4DOLLAR_11E(Union):
    pass
class N11lock_object4DOLLAR_114DOLLAR_12E(Structure):
    pass
N11lock_object4DOLLAR_114DOLLAR_12E._fields_ = [
    ('stqe_next', POINTER(lock_object)),
]
class witness(Structure):
    pass
N11lock_object4DOLLAR_11E._fields_ = [
    ('lod_list', N11lock_object4DOLLAR_114DOLLAR_12E),
    ('lod_witness', POINTER(witness)),
]
lock_object._fields_ = [
    ('lo_name', STRING),
    ('lo_type', STRING),
    ('lo_flags', u_int),
    ('lo_witness_data', N11lock_object4DOLLAR_11E),
]
__uintptr_t = __uint32_t
uintptr_t = __uintptr_t
sx._fields_ = [
    ('lock_object', lock_object),
    ('sx_lock', uintptr_t),
    ('sx_recurse', c_uint),
]
class kqlist(Structure):
    pass
class kqueue(Structure):
    pass
kqlist._fields_ = [
    ('slh_first', POINTER(kqueue)),
]
filedesc._fields_ = [
    ('fd_ofiles', POINTER(POINTER(file))),
    ('fd_ofileflags', STRING),
    ('fd_cdir', POINTER(vnode)),
    ('fd_rdir', POINTER(vnode)),
    ('fd_jdir', POINTER(vnode)),
    ('fd_nfiles', c_int),
    ('fd_map', POINTER(u_long)),
    ('fd_lastfile', c_int),
    ('fd_freefile', c_int),
    ('fd_cmask', u_short),
    ('fd_refcnt', u_short),
    ('fd_holdcnt', u_short),
    ('fd_sx', sx),
    ('fd_kqlist', kqlist),
    ('fd_holdleaderscount', c_int),
    ('fd_holdleaderswakeup', c_int),
]
vnode._fields_ = [
]
pargs._fields_ = [
    ('ar_ref', u_int),
    ('ar_length', u_int),
    ('ar_args', u_char * 1),
]
class N4proc4DOLLAR_30E(Structure):
    pass
N4proc4DOLLAR_30E._fields_ = [
    ('le_next', POINTER(proc)),
    ('le_prev', POINTER(POINTER(proc))),
]
class N4proc4DOLLAR_31E(Structure):
    pass
class thread(Structure):
    pass
N4proc4DOLLAR_31E._fields_ = [
    ('tqh_first', POINTER(thread)),
    ('tqh_last', POINTER(POINTER(thread))),
]
class N4proc4DOLLAR_32E(Structure):
    pass
class kse_upcall(Structure):
    pass
N4proc4DOLLAR_32E._fields_ = [
    ('tqh_first', POINTER(kse_upcall)),
    ('tqh_last', POINTER(POINTER(kse_upcall))),
]
class mtx(Structure):
    pass
mtx._fields_ = [
    ('lock_object', lock_object),
    ('mtx_lock', uintptr_t),
    ('mtx_recurse', u_int),
]
class ucred(Structure):
    pass
class filedesc_to_leader(Structure):
    pass
class pstats(Structure):
    pass
class plimit(Structure):
    pass
class callout(Structure):
    pass
class N7callout4DOLLAR_13E(Union):
    pass
class N7callout4DOLLAR_134DOLLAR_14E(Structure):
    pass
N7callout4DOLLAR_134DOLLAR_14E._fields_ = [
    ('sle_next', POINTER(callout)),
]
class N7callout4DOLLAR_134DOLLAR_15E(Structure):
    pass
N7callout4DOLLAR_134DOLLAR_15E._fields_ = [
    ('tqe_next', POINTER(callout)),
    ('tqe_prev', POINTER(POINTER(callout))),
]
N7callout4DOLLAR_13E._fields_ = [
    ('sle', N7callout4DOLLAR_134DOLLAR_14E),
    ('tqe', N7callout4DOLLAR_134DOLLAR_15E),
]
callout._fields_ = [
    ('c_links', N7callout4DOLLAR_13E),
    ('c_time', c_int),
    ('c_arg', c_void_p),
    ('c_func', CFUNCTYPE(None, c_void_p)),
    ('c_mtx', POINTER(mtx)),
    ('c_flags', c_int),
]
class sigacts(Structure):
    pass

# values for unnamed enumeration
PRS_NEW = 0
PRS_NORMAL = 1
PRS_ZOMBIE = 2
class N4proc4DOLLAR_34E(Structure):
    pass
N4proc4DOLLAR_34E._fields_ = [
    ('le_next', POINTER(proc)),
    ('le_prev', POINTER(POINTER(proc))),
]
class N4proc4DOLLAR_35E(Structure):
    pass
N4proc4DOLLAR_35E._fields_ = [
    ('le_next', POINTER(proc)),
    ('le_prev', POINTER(POINTER(proc))),
]
class N4proc4DOLLAR_36E(Structure):
    pass
N4proc4DOLLAR_36E._fields_ = [
    ('le_next', POINTER(proc)),
    ('le_prev', POINTER(POINTER(proc))),
]
class N4proc4DOLLAR_37E(Structure):
    pass
N4proc4DOLLAR_37E._fields_ = [
    ('lh_first', POINTER(proc)),
]
class ksiginfo(Structure):
    pass
class sigqueue(Structure):
    pass
class N8sigqueue4DOLLAR_20E(Structure):
    pass
N8sigqueue4DOLLAR_20E._fields_ = [
    ('tqh_first', POINTER(ksiginfo)),
    ('tqh_last', POINTER(POINTER(ksiginfo))),
]
sigqueue._fields_ = [
    ('sq_signals', sigset_t),
    ('sq_kill', sigset_t),
    ('sq_list', N8sigqueue4DOLLAR_20E),
    ('sq_proc', POINTER(proc)),
    ('sq_flags', c_int),
]
sigqueue_t = sigqueue
class itimerval(Structure):
    pass
itimerval._fields_ = [
    ('it_interval', timeval),
    ('it_value', timeval),
]
class rusage_ext(Structure):
    pass
rusage_ext._pack_ = 4
rusage_ext._fields_ = [
    ('rux_runtime', u_int64_t),
    ('rux_uticks', u_int64_t),
    ('rux_sticks', u_int64_t),
    ('rux_iticks', u_int64_t),
    ('rux_uu', u_int64_t),
    ('rux_su', u_int64_t),
    ('rux_tu', u_int64_t),
]
class sigiolst(Structure):
    pass
class sigio(Structure):
    pass
sigiolst._fields_ = [
    ('slh_first', POINTER(sigio)),
]
class nlminfo(Structure):
    pass
class kaioinfo(Structure):
    pass
class itimers(Structure):
    pass
class kse_thr_mailbox(Structure):
    pass
class pgrp(Structure):
    pass
class sysentvec(Structure):
    pass
__int64_t = c_longlong
__rlim_t = __int64_t
rlim_t = __rlim_t
class knlist(Structure):
    pass
class klist(Structure):
    pass
class knote(Structure):
    pass
klist._fields_ = [
    ('slh_first', POINTER(knote)),
]
knlist._fields_ = [
    ('kl_list', klist),
    ('kl_lock', CFUNCTYPE(None, c_void_p)),
    ('kl_unlock', CFUNCTYPE(None, c_void_p)),
    ('kl_locked', CFUNCTYPE(c_int, c_void_p)),
    ('kl_lockarg', c_void_p),
]
class mdproc(Structure):
    pass
class proc_ldt(Structure):
    pass
mdproc._fields_ = [
    ('md_ldt', POINTER(proc_ldt)),
]
class label(Structure):
    pass
class p_sched(Structure):
    pass
class N4proc4DOLLAR_38E(Structure):
    pass
class ktr_request(Structure):
    pass
N4proc4DOLLAR_38E._fields_ = [
    ('stqh_first', POINTER(ktr_request)),
    ('stqh_last', POINTER(POINTER(ktr_request))),
]
class N4proc4DOLLAR_39E(Structure):
    pass
class mqueue_notifier(Structure):
    pass
N4proc4DOLLAR_39E._fields_ = [
    ('lh_first', POINTER(mqueue_notifier)),
]
proc._pack_ = 4
proc._fields_ = [
    ('p_list', N4proc4DOLLAR_30E),
    ('p_threads', N4proc4DOLLAR_31E),
    ('p_upcalls', N4proc4DOLLAR_32E),
    ('p_slock', mtx),
    ('p_ucred', POINTER(ucred)),
    ('p_fd', POINTER(filedesc)),
    ('p_fdtol', POINTER(filedesc_to_leader)),
    ('p_stats', POINTER(pstats)),
    ('p_limit', POINTER(plimit)),
    ('p_limco', callout),
    ('p_sigacts', POINTER(sigacts)),
    ('p_flag', c_int),
    ('p_state', c_int),
    ('p_pid', pid_t),
    ('p_hash', N4proc4DOLLAR_34E),
    ('p_pglist', N4proc4DOLLAR_35E),
    ('p_pptr', POINTER(proc)),
    ('p_sibling', N4proc4DOLLAR_36E),
    ('p_children', N4proc4DOLLAR_37E),
    ('p_mtx', mtx),
    ('p_ksi', POINTER(ksiginfo)),
    ('p_sigqueue', sigqueue_t),
    ('p_oppid', pid_t),
    ('p_vmspace', POINTER(vmspace)),
    ('p_swtick', u_int),
    ('p_realtimer', itimerval),
    ('p_ru', rusage),
    ('p_rux', rusage_ext),
    ('p_crux', rusage_ext),
    ('p_profthreads', c_int),
    ('p_exitthreads', c_int),
    ('p_traceflag', c_int),
    ('p_tracevp', POINTER(vnode)),
    ('p_tracecred', POINTER(ucred)),
    ('p_textvp', POINTER(vnode)),
    ('p_lock', c_char),
    ('p_sigiolst', sigiolst),
    ('p_sigparent', c_int),
    ('p_sig', c_int),
    ('p_code', u_long),
    ('p_stops', u_int),
    ('p_stype', u_int),
    ('p_step', c_char),
    ('p_pfsflags', u_char),
    ('p_nlminfo', POINTER(nlminfo)),
    ('p_aioinfo', POINTER(kaioinfo)),
    ('p_singlethread', POINTER(thread)),
    ('p_suspcount', c_int),
    ('p_xthread', POINTER(thread)),
    ('p_boundary_count', c_int),
    ('p_pendingcnt', c_int),
    ('p_itimers', POINTER(itimers)),
    ('p_numupcalls', c_int),
    ('p_upsleeps', c_int),
    ('p_completed', POINTER(kse_thr_mailbox)),
    ('p_nextupcall', c_int),
    ('p_upquantum', c_int),
    ('p_magic', u_int),
    ('p_osrel', c_int),
    ('p_comm', c_char * 20),
    ('p_pgrp', POINTER(pgrp)),
    ('p_sysent', POINTER(sysentvec)),
    ('p_args', POINTER(pargs)),
    ('p_cpulimit', rlim_t),
    ('p_nice', c_byte),
    ('p_xstat', u_short),
    ('p_klist', knlist),
    ('p_numthreads', c_int),
    ('p_md', mdproc),
    ('p_itcallout', callout),
    ('p_acflag', u_short),
    ('p_peers', POINTER(proc)),
    ('p_leader', POINTER(proc)),
    ('p_emuldata', c_void_p),
    ('p_label', POINTER(label)),
    ('p_sched', POINTER(p_sched)),
    ('p_ktr', N4proc4DOLLAR_38E),
    ('p_mqnotifier', N4proc4DOLLAR_39E),
]
class uprof(Structure):
    pass
uprof._fields_ = [
    ('pr_base', caddr_t),
    ('pr_size', u_long),
    ('pr_off', u_long),
    ('pr_scale', u_long),
]
pstats._fields_ = [
    ('p_cru', rusage),
    ('p_timer', itimerval * 3),
    ('p_prof', uprof),
    ('p_start', timeval),
]
user._fields_ = [
    ('u_stats', pstats),
    ('u_kproc', kinfo_proc),
]
class vm_map(Structure):
    pass
class vm_map_entry(Structure):
    pass
__vm_offset_t = __uint32_t
vm_offset_t = __vm_offset_t
class vm_map_object(Union):
    pass
class vm_object(Structure):
    pass
vm_map_object._fields_ = [
    ('vm_object', POINTER(vm_object)),
    ('sub_map', POINTER(vm_map)),
]
__vm_ooffset_t = __int64_t
vm_ooffset_t = __vm_ooffset_t
vm_eflags_t = u_int
vm_prot_t = u_char
vm_inherit_t = c_char
__vm_pindex_t = __uint64_t
vm_pindex_t = __vm_pindex_t
vm_map_entry._pack_ = 4
vm_map_entry._fields_ = [
    ('prev', POINTER(vm_map_entry)),
    ('next', POINTER(vm_map_entry)),
    ('left', POINTER(vm_map_entry)),
    ('right', POINTER(vm_map_entry)),
    ('start', vm_offset_t),
    ('end', vm_offset_t),
    ('avail_ssize', vm_offset_t),
    ('adj_free', vm_size_t),
    ('max_free', vm_size_t),
    ('object', vm_map_object),
    ('offset', vm_ooffset_t),
    ('eflags', vm_eflags_t),
    ('protection', vm_prot_t),
    ('max_protection', vm_prot_t),
    ('inheritance', vm_inherit_t),
    ('wired_count', c_int),
    ('lastr', vm_pindex_t),
]
vm_flags_t = u_char
vm_map_entry_t = POINTER(vm_map_entry)
class pmap(Structure):
    pass
pmap_t = POINTER(pmap)
vm_map._fields_ = [
    ('header', vm_map_entry),
    ('lock', sx),
    ('system_mtx', mtx),
    ('nentries', c_int),
    ('size', vm_size_t),
    ('timestamp', u_int),
    ('needs_wakeup', u_char),
    ('system_map', u_char),
    ('flags', vm_flags_t),
    ('root', vm_map_entry_t),
    ('pmap', pmap_t),
]
uint32_t = __uint32_t
pd_entry_t = uint32_t
class N4pmap4DOLLAR_41E(Structure):
    pass
class pv_chunk(Structure):
    pass
N4pmap4DOLLAR_41E._fields_ = [
    ('tqh_first', POINTER(pv_chunk)),
    ('tqh_last', POINTER(POINTER(pv_chunk))),
]
class pmap_statistics(Structure):
    pass
pmap_statistics._fields_ = [
    ('resident_count', c_long),
    ('wired_count', c_long),
]
class N4pmap4DOLLAR_42E(Structure):
    pass
N4pmap4DOLLAR_42E._fields_ = [
    ('le_next', POINTER(pmap)),
    ('le_prev', POINTER(POINTER(pmap))),
]
pmap._fields_ = [
    ('pm_mtx', mtx),
    ('pm_pdir', POINTER(pd_entry_t)),
    ('pm_pvchunk', N4pmap4DOLLAR_41E),
    ('pm_active', u_int),
    ('pm_stats', pmap_statistics),
    ('pm_list', N4pmap4DOLLAR_42E),
]
class shmmap_state(Structure):
    pass
vmspace._fields_ = [
    ('vm_map', vm_map),
    ('vm_pmap', pmap),
    ('vm_shm', POINTER(shmmap_state)),
    ('vm_swrss', segsz_t),
    ('vm_tsize', segsz_t),
    ('vm_dsize', segsz_t),
    ('vm_ssize', segsz_t),
    ('vm_taddr', caddr_t),
    ('vm_daddr', caddr_t),
    ('vm_maxsaddr', caddr_t),
    ('vm_refcnt', c_int),
]
pcb_ext._fields_ = [
]
class N8pv_chunk4DOLLAR_44E(Structure):
    pass
N8pv_chunk4DOLLAR_44E._fields_ = [
    ('tqe_next', POINTER(pv_chunk)),
    ('tqe_prev', POINTER(POINTER(pv_chunk))),
]
class pv_entry(Structure):
    pass
class N8pv_entry4DOLLAR_43E(Structure):
    pass
N8pv_entry4DOLLAR_43E._fields_ = [
    ('tqe_next', POINTER(pv_entry)),
    ('tqe_prev', POINTER(POINTER(pv_entry))),
]
pv_entry._fields_ = [
    ('pv_va', vm_offset_t),
    ('pv_list', N8pv_entry4DOLLAR_43E),
]
pv_chunk._fields_ = [
    ('pc_pmap', pmap_t),
    ('pc_list', N8pv_chunk4DOLLAR_44E),
    ('pc_map', uint32_t * 11),
    ('pc_spare', uint32_t * 2),
    ('pc_pventry', pv_entry * 336),
]
proc_ldt._fields_ = [
    ('ldt_base', caddr_t),
    ('ldt_len', c_int),
    ('ldt_refcnt', c_int),
    ('ldt_active', u_long),
    ('ldt_sd', segment_descriptor),
]
witness._fields_ = [
]
knote._fields_ = [
]
kqueue._fields_ = [
]
file._fields_ = [
]
filedesc_to_leader._fields_ = [
    ('fdl_refcount', c_int),
    ('fdl_holdcount', c_int),
    ('fdl_wakeup', c_int),
    ('fdl_leader', POINTER(proc)),
    ('fdl_prev', POINTER(filedesc_to_leader)),
    ('fdl_next', POINTER(filedesc_to_leader)),
]
class N4pgrp4DOLLAR_21E(Structure):
    pass
N4pgrp4DOLLAR_21E._fields_ = [
    ('le_next', POINTER(pgrp)),
    ('le_prev', POINTER(POINTER(pgrp))),
]
class N4pgrp4DOLLAR_22E(Structure):
    pass
N4pgrp4DOLLAR_22E._fields_ = [
    ('lh_first', POINTER(proc)),
]
class session(Structure):
    pass
pgrp._fields_ = [
    ('pg_hash', N4pgrp4DOLLAR_21E),
    ('pg_members', N4pgrp4DOLLAR_22E),
    ('pg_session', POINTER(session)),
    ('pg_sigiolst', sigiolst),
    ('pg_id', pid_t),
    ('pg_jobc', c_int),
    ('pg_mtx', mtx),
]
nlminfo._fields_ = [
]
kaioinfo._fields_ = [
]
p_sched._fields_ = [
]
mqueue_notifier._fields_ = [
]
class N6thread4DOLLAR_23E(Structure):
    pass
N6thread4DOLLAR_23E._fields_ = [
    ('tqe_next', POINTER(thread)),
    ('tqe_prev', POINTER(POINTER(thread))),
]
class N6thread4DOLLAR_24E(Structure):
    pass
N6thread4DOLLAR_24E._fields_ = [
    ('tqe_next', POINTER(thread)),
    ('tqe_prev', POINTER(POINTER(thread))),
]
class N6thread4DOLLAR_25E(Structure):
    pass
N6thread4DOLLAR_25E._fields_ = [
    ('tqe_next', POINTER(thread)),
    ('tqe_prev', POINTER(POINTER(thread))),
]
class N6thread4DOLLAR_26E(Structure):
    pass
class selinfo(Structure):
    pass
N6thread4DOLLAR_26E._fields_ = [
    ('tqh_first', POINTER(selinfo)),
    ('tqh_last', POINTER(POINTER(selinfo))),
]
class sleepqueue(Structure):
    pass
class turnstile(Structure):
    pass
class umtx_q(Structure):
    pass
class N6thread4DOLLAR_27E(Structure):
    pass
N6thread4DOLLAR_27E._fields_ = [
    ('lh_first', POINTER(turnstile)),
]
class lock_list_entry(Structure):
    pass
uint64_t = __uint64_t
class sigaltstack(Structure):
    pass
__size_t = __uint32_t
sigaltstack._fields_ = [
    ('ss_sp', STRING),
    ('ss_size', __size_t),
    ('ss_flags', c_int),
]
stack_t = sigaltstack

# values for unnamed enumeration
TDS_INACTIVE = 0
TDS_INHIBITED = 1
TDS_CAN_RUN = 2
TDS_RUNQ = 3
TDS_RUNNING = 4
__register_t = __int32_t
register_t = __register_t
class trapframe(Structure):
    pass
class mdthread(Structure):
    pass
mdthread._fields_ = [
    ('md_spinlock_count', c_int),
    ('md_saved_flags', register_t),
]
class td_sched(Structure):
    pass
class kaudit_record(Structure):
    pass
thread._pack_ = 4
thread._fields_ = [
    ('td_lock', POINTER(mtx)),
    ('td_proc', POINTER(proc)),
    ('td_plist', N6thread4DOLLAR_23E),
    ('td_slpq', N6thread4DOLLAR_24E),
    ('td_lockq', N6thread4DOLLAR_25E),
    ('td_selq', N6thread4DOLLAR_26E),
    ('td_sleepqueue', POINTER(sleepqueue)),
    ('td_turnstile', POINTER(turnstile)),
    ('td_umtxq', POINTER(umtx_q)),
    ('td_tid', lwpid_t),
    ('td_sigqueue', sigqueue_t),
    ('td_flags', c_int),
    ('td_inhibitors', c_int),
    ('td_pflags', c_int),
    ('td_dupfd', c_int),
    ('td_sqqueue', c_int),
    ('td_wchan', c_void_p),
    ('td_wmesg', STRING),
    ('td_lastcpu', u_char),
    ('td_oncpu', u_char),
    ('td_owepreempt', u_char),
    ('td_locks', c_short),
    ('td_tsqueue', u_char),
    ('td_blocked', POINTER(turnstile)),
    ('td_lockname', STRING),
    ('td_contested', N6thread4DOLLAR_27E),
    ('td_sleeplocks', POINTER(lock_list_entry)),
    ('td_intr_nesting_level', c_int),
    ('td_pinned', c_int),
    ('td_mailbox', POINTER(kse_thr_mailbox)),
    ('td_ucred', POINTER(ucred)),
    ('td_standin', POINTER(thread)),
    ('td_upcall', POINTER(kse_upcall)),
    ('td_estcpu', u_int),
    ('td_slptick', u_int),
    ('td_ru', rusage),
    ('td_runtime', uint64_t),
    ('td_pticks', u_int),
    ('td_sticks', u_int),
    ('td_iticks', u_int),
    ('td_uticks', u_int),
    ('td_uuticks', u_int),
    ('td_usticks', u_int),
    ('td_intrval', c_int),
    ('td_oldsigmask', sigset_t),
    ('td_sigmask', sigset_t),
    ('td_generation', u_int),
    ('td_sigstk', stack_t),
    ('td_kflags', c_int),
    ('td_xsig', c_int),
    ('td_profil_addr', u_long),
    ('td_profil_ticks', u_int),
    ('td_name', c_char * 20),
    ('td_base_pri', u_char),
    ('td_priority', u_char),
    ('td_pri_class', u_char),
    ('td_user_pri', u_char),
    ('td_base_user_pri', u_char),
    ('td_pcb', POINTER(pcb)),
    ('td_state', c_int),
    ('td_retval', register_t * 2),
    ('td_slpcallout', callout),
    ('td_frame', POINTER(trapframe)),
    ('td_kstack_obj', POINTER(vm_object)),
    ('td_kstack', vm_offset_t),
    ('td_kstack_pages', c_int),
    ('td_altkstack_obj', POINTER(vm_object)),
    ('td_altkstack', vm_offset_t),
    ('td_altkstack_pages', c_int),
    ('td_critnest', u_int),
    ('td_md', mdthread),
    ('td_sched', POINTER(td_sched)),
    ('td_ar', POINTER(kaudit_record)),
    ('td_syscalls', c_int),
]
kse_thr_mailbox._fields_ = [
]
vm_object._fields_ = [
]
class N10kse_upcall4DOLLAR_29E(Structure):
    pass
N10kse_upcall4DOLLAR_29E._fields_ = [
    ('tqe_next', POINTER(kse_upcall)),
    ('tqe_prev', POINTER(POINTER(kse_upcall))),
]
class kse_mailbox(Structure):
    pass
kse_upcall._fields_ = [
    ('ku_link', N10kse_upcall4DOLLAR_29E),
    ('ku_proc', POINTER(proc)),
    ('ku_owner', POINTER(thread)),
    ('ku_flags', c_int),
    ('ku_mailbox', POINTER(kse_mailbox)),
    ('ku_stack', stack_t),
    ('ku_func', c_void_p),
    ('ku_mflags', c_uint),
]
plimit._fields_ = [
]
itimers._fields_ = [
]
sysentvec._fields_ = [
]
label._fields_ = [
]
ktr_request._fields_ = [
]
class N5sigio4DOLLAR_16E(Union):
    pass
N5sigio4DOLLAR_16E._fields_ = [
    ('siu_proc', POINTER(proc)),
    ('siu_pgrp', POINTER(pgrp)),
]
class N5sigio4DOLLAR_17E(Structure):
    pass
N5sigio4DOLLAR_17E._fields_ = [
    ('sle_next', POINTER(sigio)),
]
sigio._fields_ = [
    ('sio_u', N5sigio4DOLLAR_16E),
    ('sio_pgsigio', N5sigio4DOLLAR_17E),
    ('sio_myref', POINTER(POINTER(sigio))),
    ('sio_ucred', POINTER(ucred)),
    ('sio_pgid', pid_t),
]
ucred._fields_ = [
]
__sighandler_t = CFUNCTYPE(None, c_int)
sig_t = POINTER(__sighandler_t)
sigacts._fields_ = [
    ('ps_sigact', sig_t * 128),
    ('ps_catchmask', sigset_t * 128),
    ('ps_sigonstack', sigset_t),
    ('ps_sigintr', sigset_t),
    ('ps_sigreset', sigset_t),
    ('ps_signodefer', sigset_t),
    ('ps_siginfo', sigset_t),
    ('ps_sigignore', sigset_t),
    ('ps_sigcatch', sigset_t),
    ('ps_freebsd4', sigset_t),
    ('ps_osigset', sigset_t),
    ('ps_usertramp', sigset_t),
    ('ps_flag', c_int),
    ('ps_refcnt', c_int),
    ('ps_mtx', mtx),
]
class N8ksiginfo4DOLLAR_19E(Structure):
    pass
N8ksiginfo4DOLLAR_19E._fields_ = [
    ('tqe_next', POINTER(ksiginfo)),
    ('tqe_prev', POINTER(POINTER(ksiginfo))),
]
class __siginfo(Structure):
    pass
class sigval(Union):
    pass
sigval._fields_ = [
    ('sival_int', c_int),
    ('sival_ptr', c_void_p),
    ('sigval_int', c_int),
    ('sigval_ptr', c_void_p),
]
class N9__siginfo3DOLLAR_4E(Union):
    pass
class N9__siginfo3DOLLAR_43DOLLAR_5E(Structure):
    pass
N9__siginfo3DOLLAR_43DOLLAR_5E._fields_ = [
    ('_trapno', c_int),
]
class N9__siginfo3DOLLAR_43DOLLAR_6E(Structure):
    pass
N9__siginfo3DOLLAR_43DOLLAR_6E._fields_ = [
    ('_timerid', c_int),
    ('_overrun', c_int),
]
class N9__siginfo3DOLLAR_43DOLLAR_7E(Structure):
    pass
N9__siginfo3DOLLAR_43DOLLAR_7E._fields_ = [
    ('_mqd', c_int),
]
class N9__siginfo3DOLLAR_43DOLLAR_8E(Structure):
    pass
N9__siginfo3DOLLAR_43DOLLAR_8E._fields_ = [
    ('_band', c_long),
]
class N9__siginfo3DOLLAR_43DOLLAR_9E(Structure):
    pass
N9__siginfo3DOLLAR_43DOLLAR_9E._fields_ = [
    ('__spare1__', c_long),
    ('__spare2__', c_int * 7),
]
N9__siginfo3DOLLAR_4E._fields_ = [
    ('_fault', N9__siginfo3DOLLAR_43DOLLAR_5E),
    ('_timer', N9__siginfo3DOLLAR_43DOLLAR_6E),
    ('_mesgq', N9__siginfo3DOLLAR_43DOLLAR_7E),
    ('_poll', N9__siginfo3DOLLAR_43DOLLAR_8E),
    ('__spare__', N9__siginfo3DOLLAR_43DOLLAR_9E),
]
__siginfo._fields_ = [
    ('si_signo', c_int),
    ('si_errno', c_int),
    ('si_code', c_int),
    ('si_pid', __pid_t),
    ('si_uid', __uid_t),
    ('si_status', c_int),
    ('si_addr', c_void_p),
    ('si_value', sigval),
    ('_reason', N9__siginfo3DOLLAR_4E),
]
siginfo_t = __siginfo
ksiginfo._fields_ = [
    ('ksi_link', N8ksiginfo4DOLLAR_19E),
    ('ksi_info', siginfo_t),
    ('ksi_flags', c_int),
    ('ksi_sigq', POINTER(sigqueue)),
]
shmmap_state._fields_ = [
]
class tty(Structure):
    pass
session._fields_ = [
    ('s_count', c_int),
    ('s_leader', POINTER(proc)),
    ('s_ttyvp', POINTER(vnode)),
    ('s_ttyp', POINTER(tty)),
    ('s_sid', pid_t),
    ('s_login', c_char * 20),
    ('s_mtx', mtx),
]
kaudit_record._fields_ = [
]
sleepqueue._fields_ = [
]
trapframe._fields_ = [
]
turnstile._fields_ = [
]
selinfo._fields_ = [
]
umtx_q._fields_ = [
]
lock_list_entry._fields_ = [
]
kse_mailbox._fields_ = [
]
td_sched._fields_ = [
]
tty._fields_ = [
]
__all__ = ['__uint16_t', 'ksiginfo', 'uid_t', 'segment_descriptor',
           'lwpid_t', 'N4proc4DOLLAR_39E', 'selinfo', 'tty',
           'savefpu', 'TDS_RUNQ', 'session', 'uprof',
           'N9__siginfo3DOLLAR_43DOLLAR_7E', 'kaioinfo',
           'N8ksiginfo4DOLLAR_19E', 'kqueue', 'N4proc4DOLLAR_36E',
           'mdproc', 'N9__siginfo3DOLLAR_4E', '__size_t', '__segsz_t',
           'TDS_INACTIVE', 'pcb', 'N9__siginfo3DOLLAR_43DOLLAR_8E',
           'save87', 'kse_thr_mailbox', 'N4pmap4DOLLAR_41E',
           'N7savexmm3DOLLAR_1E', 'N4proc4DOLLAR_38E', '__sigset',
           'N9__siginfo3DOLLAR_43DOLLAR_6E', 'u_char', 'fixpt_t',
           'N7callout4DOLLAR_134DOLLAR_15E', 'N4proc4DOLLAR_30E',
           'u_int64_t', 'u_int16_t', '__fixpt_t', '__time_t',
           'vm_prot_t', 'vm_pindex_t', 'N4proc4DOLLAR_31E',
           'sigset_t', 'filedesc_to_leader', 'kaudit_record', 'vnode',
           '__int32_t', 'filedesc', '__vm_size_t', 'sigiolst',
           'N6thread4DOLLAR_27E', '__uint64_t', 'mdthread',
           '__register_t', 'N4pgrp4DOLLAR_21E', 'itimerval',
           'lock_list_entry', 'u_int32_t', 'PRS_ZOMBIE', 'PRS_NEW',
           'witness', '__sigset_t', 'N4proc4DOLLAR_34E', 'siginfo_t',
           'vm_offset_t', 'vm_map_entry_t', 'N5sigio4DOLLAR_17E',
           'label', 'N4pmap4DOLLAR_42E', 'sigaltstack', 'pargs',
           'proc', 'vm_object', 'vm_map_entry', '__gid_t',
           'sigqueue_t', 'N11lock_object4DOLLAR_114DOLLAR_12E',
           'env87', '__uint32_t', 'sigio', 'sysentvec',
           'N4pgrp4DOLLAR_22E', 'pv_entry', '__lwpid_t', 'sig_t',
           'fpacc87', 'vm_size_t', 'thread', 'N4proc4DOLLAR_37E',
           'segsz_t', 'pcb_ext', '__vm_offset_t', '__sighandler_t',
           'pstats', 'caddr_t', 'itimers', 'PRS_NORMAL',
           'N6thread4DOLLAR_25E', 'N6thread4DOLLAR_26E',
           'pmap_statistics', 'sigval', 'knote', 'rlim_t', 'klist',
           'vm_map_object', 'kqlist', 'kinfo_proc', 'pd_entry_t',
           'register_t', 'N4proc4DOLLAR_32E', 'shmmap_state',
           'callout', 'kse_upcall', 'priority', 'vm_flags_t', 'pmap',
           'N8pv_entry4DOLLAR_43E', 'rusage_ext', 'uintptr_t',
           'stack_t', 'xmmacc', 'TDS_INHIBITED', 'u_int', 'nlminfo',
           'N11lock_object4DOLLAR_11E', 'ktr_request',
           'N10kse_upcall4DOLLAR_29E', 'gid_t', 'sigacts', 'mtx',
           'envxmm', '__suseconds_t', 'pid_t', 'pmap_t', 'p_sched',
           'u_long', 'N4proc4DOLLAR_35E', '__siginfo', 'pgrp',
           'N9__siginfo3DOLLAR_43DOLLAR_9E', 'uint64_t', 'sigqueue',
           'vm_map', 'proc_ldt', 'N5sigio4DOLLAR_16E', 'savexmm',
           'lock_object', 'file', 'N7callout4DOLLAR_134DOLLAR_14E',
           'vmspace', '__rlim_t', 'N9__siginfo3DOLLAR_43DOLLAR_5E',
           'N6thread4DOLLAR_23E', 'time_t', 'u_short',
           'N7callout4DOLLAR_13E', 'sleepqueue', 'vm_ooffset_t',
           'timeval', 'trapframe', '__int64_t', 'umtx_q',
           'vm_inherit_t', '__vm_ooffset_t', '__pid_t',
           'N8pv_chunk4DOLLAR_44E', 'N6thread4DOLLAR_24E',
           'vm_eflags_t', 'kse_mailbox', 'ucred', 'user', 'turnstile',
           'TDS_RUNNING', 'rusage', '__uintptr_t', 'td_sched', 'sx',
           '__vm_pindex_t', 'pv_chunk', 'TDS_CAN_RUN',
           'N8sigqueue4DOLLAR_20E', 'plimit', 'knlist', 'uint32_t',
           'dev_t', '__uid_t', 'mqueue_notifier', 'suseconds_t',
           '__dev_t']
