from django.db import models
import urllib.parse

class Line(models.Model):
    name = models.CharField(max_length=200)
    ref = models.CharField('Internal line number of operator', max_length=20, unique=True)
    publicref = models.CharField('Line number', max_length=20)
    operator = models.CharField(max_length=30)
    network = models.CharField('Abbreviation for region', max_length=30)
    colour = models.CharField(max_length=7)
    mode =  models.CharField('transport mode', max_length=30)
    xml =  models.TextField('XML', default='')
    #pub_date = models.DateTimeField('date published')

    def __str__(self):
        return '{} {} {} {}'.format(self.mode, self.publicref, self.operator, self.ref)

    def getLink(self):
        values = { 'data': self.xml.replace('\n','').replace('\r',''),
           'new_layer': 'true',
           'layer_name': self.operator + ' ' + self.ref + ' ' + self.name}
        data = urllib.parse.urlencode(values)
        return 'http://localhost:8111/load_data?{}'.format(data)

class Itinerary(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    fromstop = models.CharField('first stop', max_length=50)
    tostop = models.CharField('terminus', max_length=50)
    version = models.IntegerField('public transport version of OSM route relation', default=2)

    def __str__(self):
        return '{} {} {}'.format(self.name, self.fromstop, self.tostop)
