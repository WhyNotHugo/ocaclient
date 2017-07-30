from collections import namedtuple
from datetime import date

from lxml import etree


TimeRange = namedtuple('TimeRange', ['id', 'description'])

TIME_RANGES = (
    TimeRange(1, '8 - 17hs'),
    TimeRange(2, '8 - 12hs'),
    TimeRange(3, '14 - 17hs'),
)


PickupRequestResponse = namedtuple('PickupRequestResponse', [
    'cantidadingresados',
    'cantidadrechazados',
    'cantidadregistros',
    'codigooperacion',
    'fechaingreso',
    'mailusuario',
])


class XmlNodeMixin:
    def sanitize_data(self, data):
        """
        Sanitize data received so that's is safe to pass to lxml

        Sanitize data received so that our API is as flexible as possible.
        Datetimes are converted to the custom format OCA expects, numbers and
        other non-strings are cast to strings. None is converted to an empty
        string.
        """
        sanitized_data = {}
        for k, v in data.items():
            if v is None:
                v = ''
            if isinstance(v, date):
                v = v.strftime('%Y%m%d')
            elif not isinstance(v, str):
                v = str(v)
            sanitized_data[k] = v

        return sanitized_data

    def __str__(self):
        return etree.tostring(self.node, pretty_print=True).decode()

    def __repr__(self):
        return '<{}: "{}">'.format(
            self.__class__.__name__,
            str(self),
        )


class PickupRequest(XmlNodeMixin):
    """
    This class models a pickup request sent to OCA

    A pickup request is a request for OCA to physically come and pick up
    packages to be send out.
    """
    def __init__(self, account_number):
        """
        Create a new pickup request.

        Origin data should be included via add_origin, and shipment data via
        add_shipment.
        Note that a single request can include multiple shipments.

        :param str account_number: The account number given by the courrier.
            Should look something like '123456/000.
        """
        self.node = etree.Element('ROWS')
        etree.SubElement(
            self.node,
            'cabecera',
            ver='1.0',
            nrocuenta=account_number,
        )
        self.shipments = etree.SubElement(self.node, 'envios')

    def add_origin(self, origin):
        assert isinstance(origin, Origin)
        self.node.append(origin.node)

    def add_shipment(self, shipment):
        assert isinstance(shipment, Shipment)
        self.shipments.append(shipment.node)

    def serialize(self, pretty_print=True):
        """
        Returns this in the XML format that should to be sent to the WS.
        """
        return etree.tostring(
            self.node,
            xml_declaration=True,
            standalone=True,
            encoding='iso-8859-1',
            pretty_print=pretty_print,
        ).decode('iso-8859-1')


class Origin(XmlNodeMixin):
    def __init__(self, **data):
        self.node = etree.Element('retiro', **self.sanitize_data(data))


class Shipment(XmlNodeMixin):
    def __init__(self, operative, dispatch, **data):
        self.node = etree.Element(
            'envio',
            idoperativa=operative,
            nroremito=dispatch,
        )
        self.destination = etree.SubElement(
            self.node,
            'destinatario',
            **self.sanitize_data(data),
        )
        self.packages = etree.SubElement(self.node, 'paquetes')

    def add_package(self, package):
        assert isinstance(package, Package)
        self.packages.append(package.node)


class Package(XmlNodeMixin):
    def __init__(self, **data):
        self.node = etree.Element('paquete', **self.sanitize_data(data))
