REPYTAR=seattle_linux.tgz
REPYDIR=seattle_repy
REPY=seattle_repy/repy.py
REPYPP=seattle_repy/repypp.py
RESTR=restrictions.default

# Cannot use the same port
S_PORT=12345
C_PORT=12346

# IP?
IP='127.0.0.1'
# files
IN=in.file
OUT=junk_test.out


all: demokit extra_reliable_client extra_reliable_server

extra_reliable_client:
	python ${REPYPP} extra_reliable_client.repy test/extra_reliable_client

extra_reliable_server:
	python ${REPYPP} extra_reliable_server.repy test/extra_reliable_server

test: extra_reliable_client extra_reliable_server 
	cd test && python ../${REPY} ${RESTR} extra_reliable_client ${IN} ${IP} ${S_PORT} ${IP} ${C_PORT} &
	cd test && python ../${REPY} ${RESTR} extra_reliable_server ${OUT} ${IP} ${S_PORT}

dist: superclean
	mkdir extra_reliable
	cp extra_reliable.repy extra_reliable_client.repy extra_reliable_server.repy Makefile README extra_reliable
	mkdir extra_reliable/test
	cp test/in.file test/restrictions.default extra_reliable/test
	tar czf extra_reliable.tgz extra_reliable
	rm -rf extra_reliable


clean:
	rm -f test/extra_reliable_client test/extra_reliable_server test/${OUT}

# download repy
demokit:
	# Dowloading Repy...
	if [ ! -e ${REPYDIR} ]; then wget --no-check-certificate https://seattlegeni.cs.washington.edu/geni/download/flibble/${REPYTAR}; tar xzf ${REPYTAR}; rm -f ${REPYTAR}; fi
	# done.
	#	

superclean: clean
	rm -rf ${REPYDIR} ${REPYTAR}
