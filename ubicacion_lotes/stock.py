# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns={
             
             'ubicacion_id' : fields.many2one('ubicacion.lotes', 'Ubicación Lote',
                                   help="Ubicacion fisica asignada al lote"),
             }
 
     



