REPYTAR=seattle_linux.tgz
REPYDIR=seattle_repy
REPY=seattle_repy/repy.py
REPYPP=seattle_repy/repypp.py
RESTR=restrictions.default

# Cannot use the same port
S_PORT=12345
C_PORT=12346

# IP?
IP=`hostname -i`

# files
IN=in.file
OUT=junk_test.out

all: demokit reliable_client reliable_server

reliable_client:
	python ${REPYPP} reliable_client.repy test/reliable_client

reliable_server:
	python ${REPYPP} reliable_server.repy test/reliable_server

test: reliable_client reliable_server 
	cd test && python ../${REPY} ${RESTR} reliable_client ${IN} ${IP} ${S_PORT} ${IP} ${C_PORT} &
	cd test && python ../${REPY} ${RESTR} reliable_server ${OUT} ${S_PORT}

# download repy
demokit:
	# Dowloading Repy...
	if [ ! -e ${REPYDIR} ]; then wget --no-check-certificate https://seattlegeni.cs.washington.edu/geni/download/flibble/${REPYTAR}; tar xzf ${REPYTAR}; rm -f ${REPYTAR}; fi
	# done.
	#	

dist: superclean
	mkdir reliable
	cp reliable.repy reliable_client.repy reliable_server.repy Makefile README reliable
	mkdir reliable/test
	cp test/in.file test/restrictions.default reliable/test
	tar czf reliable.tgz reliable
	rm -rf reliable

clean:
	rm -f test/reliable_client test/reliable_server test/${OUT}

superclean: clean
	rm -rf ${REPYDIR} ${REPYTAR}
