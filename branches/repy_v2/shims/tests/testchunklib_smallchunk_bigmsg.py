dy_import_module_symbols("testchunk_helper.r2py")

SERVER_IP = getmyip()
SERVER_PORT = 60606
DATA_RECV = 1024
CHUNK_SIZE_SEND = 2**9 # 512KB chunk size
CHUNK_SIZE_RECV = 2**9
DATA_TO_SEND = "Hello" * 1024 * 1024 # 5MB of data

launch_test()
