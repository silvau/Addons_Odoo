# -*- coding: utf-8 -*-
from openerp.osv import fields,osv


class product(osv.Model):
    _inherit = 'product.product'


    _columns = {
              'num_corrugado': fields.integer('Número de corrugado'),
              'piezas_corrugado': fields.integer('Piezas / Corrugado'),
               }
    
    def _check_num_corrugado(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.num_corrugado < 0:
                return False;
        return True;

    def _check_piezas_corrugado(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.piezas_corrugado < 0:
                return False;
        return True;

    _constraints = [
            (_check_num_corrugado, 'Numero de corrugado debe ser positivo', ['num_corrugado']),
            (_check_piezas_corrugado, 'Piezas / corrugado debe ser positivo', ['piezas_corrugado'])
        ]


