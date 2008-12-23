"""
<Program Name>
  models.py

<Started>
  October, 2008

<Author>
  ivan@cs.washington.edu
  Ivan Beschastnikh

<Purpose>
  Defines django model classes which are interfaces between django
  applications and the database

  This file contains definitions of model classes which are used by
  django to (1) create the django (geni) database schema, (2) to
  define an interface between django applications and the database and
  are used to maintain an evolvable schema that is easy to read,
  modify, and operate on.

  See http://docs.djangoproject.com/en/dev/topics/db/models/

<ToDo>
  This file needs to be cleaned up by moving all functions that
  operate on models out of this file and into a 'modelslib' file or
  the like. This file _should_ contain only model class definitions.
"""

import random
import datetime
import time
import traceback

from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.db import connection
from django.db import transaction
from geni.changeusers import changeusers

# 4 hours worth of seconds
VESSEL_EXPIRE_TIME_SECS = 14400

def pop_key():
    """
    <Purpose>
        

    <Arguments>

    <Exceptions>
        

    <Side Effects>
        

    <Returns>
        
    """
    
    cursor = connection.cursor()
    cursor.execute("BEGIN")
    cursor.execute("SELECT id,pub,priv FROM keygen.keys_512 limit 1")
    row = cursor.fetchone()
    if row == ():
        cursor.execute("ABORT")
        return []
    cursor.execute("DELETE from keygen.keys_512 WHERE id=%d"%(row[0]))
    cursor.execute("COMMIT")
    return [row[1],row[2]]

def get_unacquired_vessels(geni_user, filter_str):
    """
    <Purpose>
    

    <Arguments>

    <Exceptions>
        

    <Side Effects>
        

    <Returns>
        
    """

    # consider vessels that are not 'extra vessels'
    v_non_extra = Vessel.objects.filter(extra_vessel=False)
    # consider vessels that match the geni_user's assigned port
    v_right_port = v_non_extra.filter(vesselports__port__exact=geni_user.port)
    # consider unassigned vessels
    v_unacquired = v_right_port.exclude(vesselmap__isnull=False)
    # consider vessels on currently active donations
    v_active = v_unacquired.filter(donation__active__exact=True)

    print "v_non_extra", len(v_non_extra)
    print "v_right_port", len(v_right_port)
    print "v_unacquired", len(v_unacquired)
    print "v_active", len(v_active)
    
    vret = []
    for v in v_active:
        # perform filtering on ip (for LAN nodes)
        if filter_str != "" and filter_str not in v.donation.ip:
            continue
        vret.append(v)
    
    # shuffle the resulting set for a bit of randomness
    random.shuffle(vret)
    return vret

def release_resources(geni_user, resource_id, all):
    """
    <Purpose>
        

    <Arguments>

    <Exceptions>
        

    <Side Effects>
        

    <Returns>
        
    """

    myresources = VesselMap.objects.filter(user=geni_user)

    ret = ""
    for r in myresources:
        if (all is True) or (r.id == resource_id):
            nmip = r.vessel.donation.ip
            nmport = int(r.vessel.donation.port)
            vesselname = r.vessel.name
            nodepubkey = r.vessel.donation.owner_pubkey
            nodeprivkey = r.vessel.donation.owner_privkey
            success,msg = changeusers([""], nmip, nmport, vesselname, nodepubkey, nodeprivkey)
            if not success:
                print msg
            r.delete()
            if not all:
                ret = str(nmip) + ":" + str(nmport) + ":" + str(vesselname)
    return ret
            
@transaction.commit_manually    
def acquire_resources(geni_user, num, env_type):
    """
    <Purpose>
      Acquire num resources/vessels for usergeni_user of type env_type
      (LAN\WAN\Random).

    <Arguments>
      geni_user :
        A User class instance (see below) representing user for whom
        to acquire the vessels
      num :
        Number of vessels to acquire
      env_type :
        The type of vessel environment to acquire. Current support
        values are 1 : LAN, 2 : WAN, 3 : Random

    <Exceptions>
      None

    <Side Effects>
      Modifies the geni database to reflect new vessel
      assignments. Specifically, this function creates new VesselMap
      records and assigns vessels to users. This function also
      modifies vessel state by changing their user keys to geni_user's
      key.

    <Returns>
      bool, list where bool is True on success (some vessels
      acquired), False on failure (no vessels acquired). If bool is
      True then list is (acquired, explanation, summary) where
      acquired is the number of vesesls acquired, explanation is the
      detailed explanation of went on, and summary is a summary
      explanation of what went on. If bool is False then list is
      (explanation, summary) where explanation is a detailed
      explanation and summary is a summary explanation of why we
      failed.
    """
    print "expire_time ", time.time()
    expire_time = datetime.datetime.fromtimestamp(time.time() + VESSEL_EXPIRE_TIME_SECS)
    print "/expire_time ", time.time()
    explanation = ""
    try:
        summary = ""

        print "total_free ", time.time()
        total_free_vessel_count = len(Vessel.objects.all()) - len(VesselMap.objects.all())
        print "/total_free ", time.time()
        
        vessels = []
        if int(env_type) == 1:
            # env_type is LAN
            # summary += " env_type 1,"
            filter_ips = "128.208.1."
            print "get_unacq ", time.time()
            vessels = get_unacquired_vessels(geni_user, filter_ips)
            print "/get_unacq ", time.time()
            
        elif int(env_type) == 2:
            # env_type is WAN
            vessels_free = get_unacquired_vessels(geni_user, "")
            # summary += " env_type 2"
            for v in vessels_free:
                if "128.208.1." not in v.donation.ip:
                    vessels.append(v)
                    
        elif int(env_type) == 3:
            # env_type is RAND
            # summary += " env_type 3"
            vessels = get_unacquired_vessels(geni_user, "")

                    
        if num > len(vessels):
            num = len(vessels)
            explanation += "No more nodes available (max %d)."%(num)
            transaction.rollback()
            summary += " No nodes available to acquire."
            return False, (explanation, summary)
        else:
            explanation += "There are  " + str(total_free_vessel_count) + " vessels free. Your port is available on " + str(len(vessels)) + " of them."
            
        acquired = 0
        #num_failed = 0
        for v in vessels:
            if (acquired >= num):
                break

            # issue the command to remote nodemanager
            userpubkeystringlist = [geni_user.pubkey]
            nmip = v.donation.ip
            nmport = int(v.donation.port)
            vesselname = v.name
            nodepubkey = v.donation.owner_pubkey
            nodeprivkey = v.donation.owner_privkey
            # explanation += " %s:%s:%s - \n\n"%(nmip,nmport,vesselname)
            # explanation += "nodepubkey : %s<br>nodeprivkey: %s<br>"%(nodepubkey,nodeprivkey)
            # explanation += "calling changeusers with: \npubkeystrlist %s\nnmip %s\nnmport %s\nvesselname %s\nnodepubkey %s\nnodeprivkey %s\n"%(userpubkeystringlist, nmip, nmport, vesselname, nodepubkey, nodeprivkey)
            # explanation += " Acquiring %s:%s"%(nmip,nmport)
            print "changeusers ", time.time()
            success,msg = changeusers(userpubkeystringlist, nmip, nmport, vesselname, nodepubkey, nodeprivkey)
            print "/changeusers " , time.time()
            if success:
                acquired += 1
                # create and save the new vmap entry
                print "create and save vmap ", time.time()
                vmap = VesselMap(vessel = v, user = geni_user, expiration = "%s"%(expire_time))
                vmap.save()
                print "/create and save vmap ", time.time()
            else:
                explanation += " " + nmip + ":" + str(nmport) + " " + msg
            #else:
            #    explanation += msg
            #    break
                #explanation += " added, "
            #else:
            # explanation += "%s, "%(msg)
                #num_failed += 1
            
        if (num - acquired) != 0:
            summary += " Failed to acquire %d vessel(s)."%(num-acquired)
            
    except:
        # a hack to get the traceback information into a string by
        # printing to file and then reading back from file
        f = open("/tmp/models_trace","w")
        traceback.print_exc(None,f)
        f.close()
        f = open("/tmp/models_trace","r")
        explanation += f.read()
        f.close()
        transaction.rollback()
        summary += " Failed to acquire vessel(s). Internal Error."
        return False, (explanation, summary)
    else:
        transaction.commit()
        if acquired == 0:
            return False, (explanation,summary)
        summary += " Acquired %d vessel(s). "%(acquired)
        return True, (acquired, explanation, summary)

class User(models.Model):
    """
    <Purpose>
      Defines the geni user model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # link GENI user to django user record which authenticates users
    # on the website
    www_user = models.ForeignKey(DjangoUser,unique = True)
    # user's port
    port = models.IntegerField("User (vessel) port")
    # affiliation
    affiliation = models.CharField("Affiliation", max_length=1024)
    # user's personal public key
    pubkey = models.CharField("User public key", max_length=2048)
    # user's personal private key: only stored if generate during
    # registration, and (we recommend that the user delete these, once
    # they download them)
    privkey = models.CharField("User private key [!]", max_length=4096)
    # donor pub key
    donor_pubkey = models.CharField("Donor public key", max_length=2048)
    # donor priv key (user never sees this key
    donor_privkey = models.CharField("Donor private Key", max_length=4096)
    # number of vessels this user has acquired
    num_acquired_vessels = models.IntegerField("Number of acquired vessels")
    
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the User model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the User class
        """
        return self.www_user.username

    def save_new_user(self):
        """
        <Purpose>
          Handles the generation of keys and ports for a new user
          record, and then saves the new user record to the geni db.
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          Saves a new User record to the geni db
        <Returns>
          True on success, or False on failure
        """
        # user ports permitted on vessels on a donated host
        ALLOWED_USER_PORTS = range(63100,63180)

        # generate user pub/priv key pair for accessing vessels
        if self.pubkey == "":
            pubpriv=pop_key()
            if pubpriv == []:
                return False
            self.pubkey,self.privkey = pubpriv
        # generate user pub/priv key pair for donation trackback
        pubpriv2=pop_key()
        if pubpriv2 == []:
            return False
        self.donor_pubkey,self.donor_privkey = pubpriv2
        # generate random port for user
        self.port = random.sample(ALLOWED_USER_PORTS, 1)[0]
        # set default num acquired vessels to 0
        self.num_acquired_vessels = 0
        self.save()
        return True

    def gen_new_key(self):
        """
        <Purpose>
          Generates and sets a new pub\priv key pair for the user
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          Modifies and saves the User record to have a new pub\priv key pair
        <Returns>
          True on success, False on failure
        """
        pubpriv=pop_key()
        if pubpriv == []:
            return False
        self.pubkey,self.privkey = pubpriv
        self.save()
        return True
    
class Donation(models.Model):
    """
    <Purpose>
      Defines the donation model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # user donating
    user = models.ForeignKey(User)
    # machine identifier
    pubkey = models.CharField("Host public key", max_length=1024)
    # machine ip (last IP known)
    ip = models.IPAddressField("Host IP address")
    # node manager port (last port known)
    port = models.IntegerField("Host node manager's port")
    # date this donation was added to the db, auto added to new instances saved
    date_added = models.DateTimeField("Date host added", auto_now_add=True)
    # date we last heard from this machine, this field will be updated
    # ** every time the object is saved **
    last_heard = models.DateTimeField("Last time machine responded", auto_now=True)
    # status: "Initializing", etc
    status = models.CharField("Node status", max_length=1024)
    # node's seattle version
    version = models.CharField("Node Version", max_length=64)
    # owner's public key
    # TODO: change to owner_pubkeystr
    owner_pubkey = models.CharField("Owner user public key", max_length=2048)
    # owner's private key
    # TODO: change to owner_privkeystr
    owner_privkey = models.CharField("Owner user private key", max_length=4096)
    # epoch indicates the last time that the onepercenttoonepercent
    # script contacted this node
    epoch = models.IntegerField("Epoch")
    # active indicates whether this donation counts or not -- when a
    # donation's epoch is older then some threshold from current
    # epoch, a donation is marked as inactive
    active = models.BooleanField()
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the Donation model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the Donation class
        """
        return "%s:%s:%d"%(self.user.www_user.username, self.ip, self.port)
        
class Vessel(models.Model):
    """
    <Purpose>
      Defines the vessel model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # corresponding donation
    donation = models.ForeignKey(Donation)
    # vessel's name, e.g. v1..v10
    name = models.CharField("Vessel name", max_length=8)
    # vessle's last status
    status = models.CharField("Vessel status", max_length=1024)
    # extravessel boolean -- if True, this vessel is used for advertisements of geni's key
    extra_vessel = models.BooleanField()
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the Vessel model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the Vessel class
        """
        return "%s:%s"%(self.donation.ip,self.name)

class VesselPorts(models.Model):
    """
    <Purpose>
      Defines the vesselport model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # corresponding vessel
    vessel = models.ForeignKey(Vessel)
    # vessel's port on this host
    port = models.IntegerField("Vessel port")
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the VesselPorts model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the VesselPorts class
        """
        return "%s:%s:%s"%(self.vessel.donation.ip, self.vessel.name, self.port)

class VesselMap(models.Model):
    """
    <Purpose>
      Defines the vesselmap model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # the vessel being assigned to a user
    vessel = models.ForeignKey(Vessel)
    # the user assigned to the vessel
    user = models.ForeignKey(User)
    # expiration date/time
    expiration = models.DateTimeField("Mapping expiration date")
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the VesselMap model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the VesselMap class
        """
        return "%s:%s:%s"%(self.vessel.donation.ip, self.vessel.name, self.user.www_user.username)

    def time_remaining(self):
        """
        <Purpose>
          Returns the number of seconds remaining to the assignment of
          a user to a vessel
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          Number of seconds before the vessel expires
        """
        curr_time = datetime.datetime.now()
        delta = self.expiration - curr_time
        if delta.days == -1:
            ret = "now"
        else:
            hours = delta.seconds / (60 * 60)
            minutes = (delta.seconds - (hours * 60 * 60)) / 60
            ret = str(hours) + "h " + str(minutes) + "m"
        return ret
    
class Share(models.Model):
    """
    <Purpose>
      Defines the share model
    <Side Effects>
      Provides an interface to the database
    <Example Use>
      See http://docs.djangoproject.com/en/dev/topics/db/models/
    """

    # user giving
    from_user = models.ForeignKey(User, related_name='from_user')
    # user receiving
    to_user = models.ForeignKey(User, related_name = 'to_user')
    # percent giving user is sharing with receiving user
    percent = models.DecimalField("Percent shared", max_digits=3, decimal_places=0)
    def __unicode__(self):
        """
        <Purpose>
          Produce a string representation of the Share model class
        <Arguments>
          None
        <Exceptions>
          None
        <Side Effects>
          None
        <Returns>
          String representation of the Share class
        """
        return "%s->%s"%(self.from_user.www_user.username,self.to_user.www_user.username)

def test_acquire(username, num_nodes):
    """
    <Purpose>

    <Arguments>
        request:
            
        share_form:
            

    <Exceptions>
        

    <Side Effects>
        

    <Returns>
        
    """

    user = DjangoUser.objects.get(username=username)
    print "django user: ", user
    geni_user = User.objects.get(www_user = user)
    print "geni user: ", geni_user
    ret = acquire_resources(geni_user, num_nodes, "LAN")
    print "acquire returned: ", ret
    if ret[0] == False:
        print ret[1]

def test_acquire_node(username,nodeip,vesselname):
    """
    <Purpose>
        

    <Arguments>
        request:
            
        share_form:
            

    <Exceptions>
        

    <Side Effects>
        

    <Returns>
        
    """

    user = DjangoUser.objects.get(username=username)
    print "django user: ", user
    geni_user = User.objects.get(www_user = user)
    print "geni user: ", geni_user

    d = Donation.objects.get(ip = nodeip)
    print "donation: " , d
    v = Vessel.objects.get(donation = d, name = vesselname)
    print "vessel: ", v
    
    # issue the command to remote nodemanager
    userpubkeystringlist = [geni_user.pubkey]
    nmip = v.donation.ip
    nmport = int(v.donation.port)
    vesselname = v.name
    nodepubkey = v.donation.owner_pubkey
    nodeprivkey = v.donation.owner_privkey
    print "calling changeusers with: \npubkeystrlist %s\nnmip %s\nnmport %s\nvesselname %s\nnodepubkey %s\nnodeprivkey %s\n"%(userpubkeystringlist, nmip, nmport, vesselname, nodepubkey, nodeprivkey)
    success,msg = changeusers(userpubkeystringlist, nmip, nmport, vesselname, nodepubkey, nodeprivkey)
    print "returned: ", success, msg
