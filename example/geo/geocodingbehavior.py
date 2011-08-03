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
        return getattr(self.context, name)
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

def geocode(obj, event):
    if not obj.lat or not obj.lng:
        address = ', '.join([getattr(obj, i) for i in
                  ['street', 'suburb', 'town', 'postal_code'] if getattr(obj, i)])
        url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&region=au&sensor=false' % urllib.quote(address)
        geocode = urllib.urlopen(url).read()
        data = simplejson.loads(geocode)
        if data['status'] == 'OK':
            if data['results']:
                location = data['results'][0]['geometry']['location']
                obj.lat = float(location['lat'])
                obj.lng = float(location['lng'])
                transaction.commit

@grok.subscribe(IGeocodingBehavior, IObjectCreatedEvent)
def supplier_created(obj, event):
    geocode(obj, event)

@grok.subscribe(IGeocodingBehavior, IObjectModifiedEvent)
def supplier_modified(obj, event):
    geocode(obj, event)
