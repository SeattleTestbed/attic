from django.views.generic.simple import direct_to_template

genilookuppubkey = "105218563213892243899209189701795214728063009020190852991629121981430129648590559454805294602863437180197383200157929797560056350651679990894183323458702862383371519103715161824514423932881746333116028227752248782962849181124520405658625393671898781069029621867416896240848133246870330371456213657364326213813 312714756092727515598780292379395872371276579078748109351554518254514481793368058883800678614580459772002765797032260325722225376614522500847276562927611577356613250215335341049455959290730180509179381157215997103098273389151149413304651001604934784742532791625955088398372313329455355494987750365806646536736636469629655380899143568352774219563065173996594667744415518391700387531919897253828997026843423501056159275468434318826550727964420829405894564122992335715124500381230290658083672331257499145017512885259835129381157750762124840076790791959202427846549512062536039325580240373309487741134319467890746673599741871268148060727018149256387697190931523693175768595351239154192239059676450669982991614136056253025495132755577907582430428560957011063839801600705947720544745078362907393070987536242330969100531923153182335864179094051994566951914233193211513835463083579669213012962131981383521706159377642531633316767375065073795772235104272775823159971873875983352843528481287521146512180790378064962825824780897817649973221317403460404503674474228769268269759375408409701974795615072086988269846532097319019681202860566295633729260133667739837481809185531026939053693396561388528361977535344851490021470007393713971344577027977"

def download(request,username):
    return direct_to_template(request,'download/installers.html', {'username' : username})

def mac(request,username):
    return direct_to_template(request,'download/installers.html', {'username' : username})

def linux(request,username):
    return direct_to_template(request,'download/installers.html', {'username' : username})

def win(request,username):
    # vesselinfo = '''
#     Percent 8
#     Owner /tmp/%s
#     User /tmp/%s
#     '''%(user_donation_pub_key,genilookuppubkey);

    # file_put_contents("$dl_prefix/vesselsinfo.txt", vesselinfo);
    # exec("python $vesselinfopy $dl_prefix/vesselsinfo.txt $dl_prefix/vesselsinfo/");
    # exec("python $carter_script w $dl_prefix/vesselsinfo $dl_prefix/");
    return direct_to_template(request,'download/installers.html', {'username' : username})
