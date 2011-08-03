import urllib
import simplejson
import transaction

from five import grok


from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from zope.lifecycleevent import IObjectCreatedEvent, IObjectModifiedEvent
from plone.directives import form
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider


from example.geo import MessageFactory as _


class IGeocodingBehavior(form.Schema):
    """
       Marker/Form interface for Geocoding Behavior
    """
   
    # -*- Your Zope schema definitions here ... -*-

    address = schema.TextLine(
            title=_('Address'),
            description=_('Full address, separated by commas.'),
            )

    lat = schema.Float(
            title=_('Latitude'),
            description=_('Latitude in decimal format. Clear to automatically generate.'),
            required=False,
            )

    lng = schema.Float(
            title=_('Longitude'),
            description=_('Longitude in decimal format. Clear to automatically generate.'),
            required=False,
            )



alsoProvides(IGeocodingBehavior,IFormFieldProvider)

def context_property(name):
    def getter(self):
        return getattr(self.context, name, None)
    def setter(self, value):
        setattr(self.context, name, value)
    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)

class GeocodingBehavior(object):
    """
       Adapter for Geocoding Behavior
    """
    implements(IGeocodingBehavior)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    address = context_property('address')
    lat = context_property('lat')
    lng = context_property('lng')

def geocode(obj, event):
    if not IGeocodingBehavior(obj).lat or not IGeocodingBehavior(obj).lng:
        url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&region=au&sensor=false' % urllib.quote(IGeocodingBehavior(obj).address)
        geocode = urllib.urlopen(url).read()
        data = simplejson.loads(geocode)
        if data['status'] == 'OK':
            if data['results']:
                location = data['results'][0]['geometry']['location']
                IGeocodingBehavior(obj).lat = float(location['lat'])
                IGeocodingBehavior(obj).lng = float(location['lng'])
                transaction.commit

@grok.subscribe(IDexterityContent, IObjectCreatedEvent)
def add_latlng(obj, event):
    geocode(obj, event)

@grok.subscribe(IDexterityContent, IObjectModifiedEvent)
def add_latlng(obj, event):
    geocode(obj, event)
