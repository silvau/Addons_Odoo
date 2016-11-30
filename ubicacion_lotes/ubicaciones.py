# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class nova_ubicaciones(osv.osv):
    _name = 'ubicacion.lotes'
    _description = 'Ubicacion del lote'
    _columns={
              'name' : fields.char( string='Ubicacion', size=128, required=True),
              'lot_ids' : fields.one2many('stock.production.lot','ubicacion_id', string='Lot ids'),
            }

    def _check_unique_name(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            cr.execute("select name from ubicacion_lotes where name ilike '%s'"%rec.name)
            res = cr.fetchall()
            if len(res) > 1 or (len(rec.name) <> len(rec.name.strip())):
                return False
        return True
    
    _constraints = [(_check_unique_name, 'Nombre repetido o con espacios al inicio o final', ["name"])]

