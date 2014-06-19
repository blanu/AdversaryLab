""" The models module provides App Engine db.Model classes for storing freefall models in the App Engine database. """

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class View(db.Model):
  """ View represents a Freefall view. It contains a name which can be used to look it up and a pre-serialized JSON-encoded representation of the view. """
  name=db.StringProperty(required=True)
  json=db.TextProperty(required=True)

class CollectionModel(polymodel.PolyModel):
  """ CollectionModel is the base class for all collections. It has no properties and is mainly used as a base type, while the specific types are used for queries. """
  pass

class BagModel(CollectionModel):
  """ BagModel models a bag type collection. It has no properties and is mainly used as a type queries. """
  pass

class ListModel(CollectionModel):
  """ ListModel models a list type collection. It has no properties and is mainly used as a type queries. """
  pass

class MapModel(CollectionModel):
  """ MapModel models a map type collection. It has no properties and is mainly used as a type for queries. """
  pass

class Value(polymodel.PolyModel):
  """ Value is the base class for all values. It has a property 'collection' which references its parent collection. """
  collection=db.ReferenceProperty(CollectionModel, required=True)

class Item(polymodel.PolyModel):
  """ Item is the base class for all items. Items encapsulate values so that they can be placed into collections. The base Item class is also used for items in bag collections. """
  collection=db.ReferenceProperty(CollectionModel, required=True)
  value=db.ReferenceProperty(Value, required=True)

class ListItem(Item):
  """ ListItem represents a list type item. It has an Integer property called 'index'."""
  index=db.IntegerProperty(required=True)

class MapItem(Item):
  """ ListItem represents a list type item. It has an Integer property called 'index'."""
  index=db.StringProperty(required=True)

class CollectionValue(Value):
  """ CollectionValue represents a collection type value. It has a 'value' property which references the collection. """
  value=db.ReferenceProperty(CollectionModel, required=True)

class StringValue(Value):
  """ StringValue represents a string type value. It has a 'value' property which stores the string. """
  value=db.StringProperty(required=True)

class FloatValue(Value):
  """ FloatValue represents a float type value. It has a 'value' property which stores the float. """
  value=db.FloatProperty(required=True)

class Root(db.Model):
  """ Root represents the root collection for the entire collection tree. There can only be one root at a time. It has a 'value' property represneting the map which is the root of the collection tree. """
  value=db.ReferenceProperty(MapModel, required=True)
