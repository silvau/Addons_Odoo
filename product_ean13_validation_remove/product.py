# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'ean13': fields.char('Barcode', size=128,
                             help="International Article Number used for "\
                                "product identification."),
    }


    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, '', ['ean13'])]

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
