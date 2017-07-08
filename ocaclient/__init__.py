__all__ = [
    'OcaClient',
]

from datetime import datetime
from decimal import Decimal

from lxml import etree
from zeep import Client
from zeep.cache import SqliteCache
from zeep.client import OperationProxy
from zeep.transports import Transport

WSDL = 'http://webservice.oca.com.ar/epak_tracking/Oep_TrackEPak.asmx?WSDL'


NODE_TYPES = {
    'adicional': Decimal,
    'fecha': lambda s: datetime.strptime(s, '%d-%m-%Y').date(),
    'idcentroimposicion': int,
    'idtiposercicio': int,
    'nroproducto': int,
    'numero': int,
    'numeroenvio': int,
    'piso': int,
    'plazoentrega': int,
    'precio': Decimal,
    'tarifador': int,
    'total': Decimal,
}


def parse_node(node):
    tag = node.tag.lower()

    if tag in NODE_TYPES:
        value = NODE_TYPES[tag](node.text)
    else:
        value = node.text

    return value


class OcaOperationProxy:

    def __init__(self, operation, client):
        self.operation = operation
        self.client = client

    def __call__(self, *args, **kwargs):
        with self.client.options(raw_response=True):
            response = self.operation.__call__(*args, **kwargs)

        xml = etree.fromstring(response.content)
        nodes = xml.xpath('//NewDataSet/Table')

        data = [{
            child.tag.lower(): parse_node(child)
            for child in node.getchildren() if child.tag != 'XML'
        } for node in nodes]

        if len(data) == 1:
            return data[0]

        return data


class OcaClient:

    def __init__(self):
        transport = Transport(cache=SqliteCache())
        self.client = Client(WSDL, transport=transport)

    def __getattr__(self, key):
        value = getattr(self.client.service, key)
        if isinstance(value, OperationProxy):
            return OcaOperationProxy(value, self.client)
        return value
