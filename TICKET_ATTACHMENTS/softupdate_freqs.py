#!/usr/bin/python

# parses file which has some lines of format:
# 128.208.1.114 - - [22/Mar/2009:06:40:01 -0700] "GET /couvb/updatesite/test/metainfo HTTP/1.0" 404 433 "-" "Python-urllib/1.17"
#
# presents frequencies of access (count of such accesses) by IP address on the same timestamp (date/time)

def main():
    fname = "/var/log/apache2/access.log"
    f = open(fname, "r")
    lines = f.readlines()
    f.close()

    h = {}
    for line in lines:
        line = line.strip()
        if "GET /couvb/updatesite/test/metainfo" in line:
            s = line.split(" ")
            ip = s[0]
            tstamp = s[3]
            h.setdefault(tstamp, []).append(ip)

    tstamps_count = []
    for k, v in h.items():
        tstamps_count.append([len(v) , k])

    tstamps_count.sort()
    tstamps_count.reverse()

    print "COUNT TIMESTAMP:"
    for item in tstamps_count[:50]:
        print item[1], item[0]
    return


if __name__ == "__main__":
    main()


