"""
<Program Name>
  models.py

<Started>
  July 15, 2009

<Author>
  Justin Samuel

<Purpose>
  This file contains definitions of model classes for the main database
  of SeattleGeni. These models are used by django to 1) create the database
  schema, and 2) to define an interface between django applications and the
  database.

  For information on how models are defined in django apps, see
  http://docs.djangoproject.com/en/dev/topics/db/models/

  Changes to these models should be done with corresponding changes
  to the design document at https://seattle.cs.washington.edu/wiki/SeattleGeniDesign
"""

from django.db import models
from django.contrib.auth.models import User as DjangoUser




class GeniUser(DjangoUser):
  """
  Defines the GeniUser model. A GeniUser record represents a SeattleGeni user.
  
  By extending the DjangoUser model, django will still create a separate table
  in the database for the GeniUser model but will take care of making it look
  the same to us.
  """

  # The port which must be assigned to a vessel for the user to be able to
  # acquire that vessel.
  # Note: This field may go away later on if users are no longer always
  # assigned to the same port on all vessels. 
  usable_vessel_port = models.IntegerField("GeniUser's vessel port")

  # The text the user supplied which identifies the organization they are
  # affiliated with. 
  affiliation = models.CharField("Affiliation", max_length=200)
  
  # The user's public key which they use for communicating with nodes.
  # Note that the key is stored as a string "e n" where e and n are
  # decimal numbers. Because of this, max_length != max bits in the key.
  # We index this field with custom sql. See the file sql/geniuser.sql.
  user_pubkey = models.CharField("GeniUser's public key", max_length=2048)
  
  # The user's private key which they use for communicating with nodes.
  # This is not stored in the Key DB because the website needs access to it and
  # it is not used by us. The private key will only be stored when the the user
  # has had us generate their keys. The user will be encouraged through the
  # website to download this private key and have us delete our copy of it.
  # Note that the key is stored as a string "d p q" where d, p, and q are
  # decimal numbers. Because of this, max_length != max bits in the key.
  user_privkey = models.CharField("GeniUser's private key [!]", max_length=4096, null=True)
  
  # This is not a cryptographic key. This is an API key that we generate which
  # can be used by the user with the public SeattleGeni XML-RPC interface.
  # The purpose is to allow developers to use the XML-RPC interface without
  # requiring them to embed their passphrase in their source code. 
  api_key = models.CharField("API key", max_length=100, db_index=True)
  
  # The public key new donations use to indicate the donation is by this user.
  # The corresponding private key is always stored in the Key DB and is
  # accessible using this public key. The user never sees their donor keys.
  # Note that the key is stored as a string "e n" where e and n are
  # decimal numbers. Because of this, max_length != max bits in the key.
  # We index this field with custom sql. See the file sql/geniuser.sql.
  donor_pubkey = models.CharField("Donor public Key", max_length=2048)
  
  # Have the database keep track of when each record was created and modified.
  date_created = models.DateTimeField("Date added to DB", auto_now_add=True, db_index=True)
  date_modified = models.DateTimeField("Date modified in DB", auto_now=True, db_index=True)
  
  
  def __unicode__(self):
    """
    Produce a string representation of the GeniUser instance.
    """
    return "GeniUser:%s" % (self.username)





class Node(models.Model):
  """
  Defines the Node model. A Node record represents an individual nodemanager.
  When a node goes offline, it is marked inactive. Node records are never
  deleted because if they were and a node with a delete node's node_identifier
  came back online, the owner private key would have been lost. 
  """

  # The node's identifier (which happens to be a public key with no
  # corresponding private key).
  # This should be unique, but we can't set this constraint at the
  # database-level because the length is too long for mysql to index the full
  # field.
  # We index this field with custom sql. See the file sql/node.sql.
  node_identifier = models.CharField("Node identifier", max_length=2048)

  # The IP address the nodemanager was last known to be accessible through.
  last_known_ip = models.IPAddressField("Last known nodemanager IP address")

  # The port the nodemanager was last known to be accessible through. 
  last_known_port = models.IntegerField("Last known nodemanager port")

  # The version of seattle the node was last known to be running. 
  last_known_version = models.CharField("Last known version", max_length=64, blank=True, db_index=True)

  # The last time the node could be contacted.
  # This is set to the current time when the node object is first created.
  date_last_contacted = models.DateTimeField("Last date successfully contacted", auto_now_add=True, db_index=True)

  # The node gets marked as not active when it becomes inaccessible. Nodes are
  # never deleted from the database no matter how long they have been inactive.
  # If they were deleted from the database, we wouldn't have the owner key to
  # be able to contact them if they came back online later.
  is_active = models.BooleanField(db_index=True)

  # The SeattleGeni's owner key for this node. The private key is always stored
  # in the Key DB and is accessible using this public key.
  # Note that the key is stored as a string "e n" where e and n are
  # decimal numbers. Because of this, max_length != max bits in the key.
  owner_pubkey = models.CharField("Owner public key", max_length=2048)

  # The extra vessel will (at least in the near future) have the node's free
  # resources assigned to it, so the name needs to be known in order to do
  # things with those resources. 
  extra_vessel_name = models.CharField("Extra-vessel name", max_length=8)
  
  # Have the database keep track of when each record was created and modified.
  date_created = models.DateTimeField("Date added to DB", auto_now_add=True, db_index=True)
  date_modified = models.DateTimeField("Date modified in DB", auto_now=True, db_index=True)


  def __unicode__(self):
    """
    Produces a string representation of the Node instance.
    """
    return "Node:%s:%s:%d" % (self.node_identifier[:8], self.last_known_ip, self.last_known_port)





class Donation(models.Model):
  """
  Defines the Donation model. A Donation record represents the resources a user
  has donated from a single node. 
  """
  
  class Meta:
    # Only one record can have a given node and donor combination.
    unique_together = ("node", "donor")


  # The node that this donation is from.
  node = models.ForeignKey(Node, db_index=True)
  
  # The user that is credited for this donation.
  donor = models.ForeignKey(GeniUser, db_index=True)
 
  # This field will be used, if necessary, to indicate steps in the process of
  # setting up a donation's resources for use (which, for now, would be
  # creating vessels on the corresponding node using this donation's resources).
  # TODO: remove this if it doesn't get used.
  status = models.CharField("Donation status", max_length=100, blank=True, db_index=True)

  # Simple storage of the contents of a resource file describing the donated
  # resources. This information is not currently used anywhere. How this data
  # is stored may change in the future and this field just serves to start
  # keeping track of the information for now. 
  resource_description_text = models.TextField("Resource description")
  
  # Have the database keep track of when each record was created and modified.
  date_created = models.DateTimeField("Date added to DB", auto_now_add=True, db_index=True)
  date_modified = models.DateTimeField("Date modified in DB", auto_now=True, db_index=True)
    
    
  def __unicode__(self):
    """
    Produces a string representation of the Donation instance.
    """
    return "Donation:[%s]:[%s]" % (self.node, self.donor)





class Vessel(models.Model):
  """
  Defines the Vessel model. A vessel record represents a vessel that
  SeattleGeni has setup on a node. Note that this is not tied to an
  individual donation of resources from that node. 
  """

  class Meta:
    # Only one record can have a given node and vessel name combination.
    unique_together = ("node", "name")


  # The node that this vessel is on.
  node = models.ForeignKey(Node, db_index=True)

  # The name used to refer to the vessel when communicating with the nodemanager.
  name = models.CharField("Vessel name", max_length=50)
  
  # If this vessel has been acquired by a user, this is the user who acquired
  # it. This will be a null/None value if the vessel is not currently acquired
  # by any user.
  acquired_by_user = models.ForeignKey(GeniUser, null=True, db_index=True)
  
  # The date that the acquired_by_user acquired this vessel.
  date_acquired = models.DateTimeField("Date acquired", null=True, db_index=True)
  
  # The date after which the vessel should be taken away from the user who has
  # acquired it.
  date_expires = models.DateTimeField("Date that acquisition expires", null=True, db_index=True)
    
  # The vessel is marked as dirty if it needs to be reset, etc. before it can
  # be acquired.
  is_dirty = models.BooleanField(db_index=True)
    
  # Have the database keep track of when each record was created and modified.
  date_created = models.DateTimeField("Date added to DB", auto_now_add=True, db_index=True)
  date_modified = models.DateTimeField("Date modified in DB", auto_now=True, db_index=True)
    
    
  def __unicode__(self):
    """
    Produces a string representation of the Vessel instance.
    """
    return "Vessel:[%s]:%s" % (self.node, self.name)





class VesselPort(models.Model):
  """
  Defines the VesselPort model. A VesselPort record represents a port that is
  assigned to a vessel. A single vessel can have multiple ports assigned to it
  (multiple VesselPort records). 
  """

  class Meta:
    # Only one record can have a given vessel and port combination.
    unique_together = ("vessel", "port")


  # The vessel that this port record is in reference to.
  vessel = models.ForeignKey(Vessel, db_index=True)
  
  # The port being represented.
  port = models.IntegerField("Port", db_index=True)


  def __unicode__(self):
    """
    Produces a string representation of the VesselPort instance.
    """
    return "VesselPort:[%s]:%s" % (self.vessel, self.port)





class VesselUserAccessMap(models.Model):
  """
  Defines the VesselUserAccessMap model. A VesselUserAccessMap record
  represents user access to vessels. This is a many-to-many relationship.
  The user who acquired the vessel will always have a mapping to that vessel.
  In the future when additional users can be added to a Vessel through
  SeattleGeni, the additional users would have records here. 
  """
  
  class Meta:
    # Only one record can have a given vessel and user combination.
    unique_together = ("vessel", "user")


  vessel = models.ForeignKey(Vessel, db_index=True)
  
  user = models.ForeignKey(GeniUser, db_index=True)
  
  # Have the database keep track of when each record was created.
  date_created = models.DateTimeField("Date added to DB", auto_now_add=True, db_index=True)
  
  
  def __unicode__(self):
    """
    Produces a string representation of the VesselUserAccessMap instance.
    """
    return "VesselUserAccessMap:[%s]:[%s]" % (self.vessel, self.user)
  
