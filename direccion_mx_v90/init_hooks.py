def cargar_direcciones(cr, registry):
    """Import CSV data as it is faster than xml and because we can't use
    noupdate anymore with csv"""
    from openerp.tools import convert_file

    filename = 'data/res.country.state.ciudad.csv'
    convert_file(cr, 'direccion_mx', filename, None, mode='init', noupdate=True, kind='init', report=None)
    filename = 'data/res.country.state.municipio.csv'
    convert_file(cr, 'direccion_mx', filename, None, mode='init', noupdate=True, kind='init', report=None)
    filename = 'data/res.country.state.municipio.colonia.csv'
    convert_file(cr, 'direccion_mx', filename, None, mode='init', noupdate=True, kind='init', report=None)
