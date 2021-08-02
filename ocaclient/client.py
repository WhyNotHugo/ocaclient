from base64 import b64decode
from datetime import datetime
from decimal import Decimal

from dateutil import parser
from lxml import etree
from zeep import Client
from zeep.cache import SqliteCache
from zeep.proxy import OperationProxy
from zeep.transports import Transport

from ocaclient import models

WSDL = "http://webservice.oca.com.ar/epak_tracking/Oep_TrackEPak.asmx?WSDL"
WSDL2 = "http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx?Wsdl"


def parse_datetime(s):
    try:
        return datetime.strptime(s, "%d-%m-%Y").date()
    except ValueError:
        # Matches ISO-8601:
        return parser.parse(s)


NODE_TYPES = {
    "adicional": Decimal,
    "fecha": parse_datetime,
    "fechaingreso": parser.parse,
    "cantidadregistros": int,
    "cantidadingresados": int,
    "cantidadrechazados": int,
    "idcentroimposicion": int,
    "idtiposercicio": int,
    "numeroenvio": int,
    "plazoentrega": int,
    "precio": Decimal,
    "tarifador": int,
    "total": Decimal,
}


RESPONSE_TYPES = {
    "IngresoOR": models.PickupRequestResponse,
}


def parse_node(node):
    if node.text and node.text.strip():
        tag = node.tag.lower()
        value = node.text.strip()
        if tag in NODE_TYPES:
            value = NODE_TYPES[tag](value)
    else:
        value = None

    return value


class OcaWebServiceError(Exception):
    """Raise when the web service returns some sort of error."""


class OcaOperationProxy:
    def __init__(self, operation, client, return_type):
        self.operation = operation
        self.client = client
        self.return_type = return_type

    def _execute_request(self, *args, **kwargs):
        with self.client.settings(raw_response=True):
            response = self.operation.__call__(*args, **kwargs)

        response.raise_for_status()

        return response

    def _parse_response(self, xml):
        nodes = xml.xpath("//NewDataSet/Table") or xml.findall(".//Resumen")
        data = [
            {
                child.tag.lower(): parse_node(child)
                for child in node.getchildren()
                if child.tag != "XML"
            }
            for node in nodes
        ]

        if self.return_type:
            data = [self.return_type(**entry) for entry in data]

        return data

    def __call__(self, *args, **kwargs):
        response = self._execute_request(*args, **kwargs)
        xml = etree.fromstring(response.content)

        errors = xml.xpath("//Errores/Error/Descripcion")
        if errors:
            raise OcaWebServiceError(errors[0].text)

        parsed_response = self._parse_response(xml)

        return parsed_response


class OcaClient:
    def __init__(self, username: str = None, password: str = None):
        """
        Creates a new OcaClient instance.

        Username and password are only required for pick request creation.

        :param username: The username used at OCA's website.
        :param password: The password used at OCA's website.
        """
        self.transport = Transport(cache=SqliteCache())
        self.client = Client(WSDL, transport=self.transport)

        self.username = username
        self.password = password

    def create_pickup_request(
        self,
        request: models.PickupRequest,
        days: int,
        timerange: int,
        confirm=False,
    ) -> models.PickupRequestResponse:
        """
        Create a new pickup request order

        :param request: The request to send to OCA.
        :param days: How many days into the future this order must be
            picked up.
        :params timerange: the timerange where this order should be picked
            up.  See ``ocaclient.models.TIME_RANGES``.
        :return: The request creation data.
        :raises requests.exceptions.HTTPError: If the WS returns an error.
        """
        return self.IngresoOR(
            usr=self.username,
            psw=self.password,
            xml_Datos=request.serialize(),
            ConfirmarRetiro=confirm,
            DiasHastaRetiro=days,
            idFranjaHoraria=timerange,
        )[0]

    def __getattr__(self, key):
        value = getattr(self.client.service, key)
        if isinstance(value, OperationProxy):
            return_type = RESPONSE_TYPES.get(key, None)
            return OcaOperationProxy(value, self.client, return_type)
        return value

    def get_pdf_labels(self, request_id: int) -> bytes:
        """
        Fetches the PDF labels for a given pickup request.

        :param request_id: The id of the request returned by create_pickup_request.
        """
        client = Client(WSDL2, transport=self.transport)
        response = client.service.GetPdfDeEtiquetasPorOrdenOrNumeroEnvio(
            idOrdenRetiro=request_id,
            logisticaInversa=False,
        )
        return b64decode(response)
