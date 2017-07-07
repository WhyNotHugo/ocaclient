OcaClient
=========

This library is a very simple client to OCA's Epak webservice. OCA's WS is very
SOAP-like, so this is really a very light wrapper around ``zeep``, manually
parsing responses that aren't entirely SOAP.

Usage example:

.. code-block:: python

    response = OcaClient().Tarifar_Envio_Corporativo(
        PesoTotal=0.5,  # kg
        VolumenTotal=0.125,  # m³
        CodigoPostalOrigen=1414,
        CodigoPostalDestino=1111,
        CantidadPaquetes=1,
        Cuit='20-12345678-0',
        Operativa=2712345,
        ValorDeclarado=120,
    )

The ``OcaClient`` class exposes the same methods as those in the official
documentation, with the same parameters. Responses are python dictionaries, eg:

.. code-block:: python

    {
        'tarifador': '15',
        'precio': '237.7900',
        'idtiposervicio': '1',
        'ambito': 'Local',
        'plazoentrega': '3',
        'adicional': '0.0000',
        'total': '237.7900',
    }

Licence
-------

This software is licensed under the ISC licence. See LICENCE for details.

Copyright (c) 2017 Hugo Osvaldo Barrera <hugo@barrera.io>
