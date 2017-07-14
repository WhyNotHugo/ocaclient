from datetime import datetime
from decimal import Decimal

from dateutil import parser
from lxml import etree
from zeep import Client
from zeep.cache import SqliteCache
from zeep.client import OperationProxy
from zeep.transports import Transport


WSDL = 'http://webservice.oca.com.ar/epak_tracking/Oep_TrackEPak.asmx?WSDL'

NODE_TYPES = {
    'adicional': Decimal,
    'fecha': lambda s: datetime.strptime(s, '%d-%m-%Y').date(),
    'fechaingreso': parser.parse,
    'cantidadregistros': int,
    'cantidadingresados': int,
    'cantidadrechazados': int,
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

        response.raise_for_status()

        xml = etree.fromstring(response.content)
        nodes = xml.xpath('//NewDataSet/Table') or xml.findall('.//Resumen')

        data = [{
            child.tag.lower(): parse_node(child)
            for child in node.getchildren() if child.tag != 'XML'
        } for node in nodes]

        if len(data) == 1:
            return data[0]

        return data


class OcaClient:

    def __init__(self, username=None, password=None):
        """
        Creates a new OcaClient instance.

        Username and password are only required for pick request creation.

        :param str username: The username used at OCA's website.
        :param str password: The password used at OCA's website.
        """
        transport = Transport(cache=SqliteCache())
        self.client = Client(WSDL, transport=transport)

        self.username = username
        self.password = password

    def create_pickup_request(self, request, days, timerange, confirm=False):
        """
        Create a new pickup request order

        Returns a dictionary with the following fields::

            codigooperacion
            fechaingreso
            mailusuario
            cantidadregistros
            cantidadingresados
            cantidadrechazados

        :param ocaclient.models.PickupRequest: The request to send to OCA.
        :param int days: How many days into the future this order must be
            picked up.
        :params int timerange: the timerange where this order should be picked
            up.  See `ocaclient.models.TIME_RANGES`.
        """
        return self.IngresoOR(
            usr=self.username,
            psw=self.password,
            xml_Datos=request.serialize(),
            ConfirmarRetiro=confirm,
            DiasHastaRetiro=days,
            idFranjaHoraria=timerange,
        )

    def __getattr__(self, key):
        value = getattr(self.client.service, key)
        if isinstance(value, OperationProxy):
            return OcaOperationProxy(value, self.client)
        return value
