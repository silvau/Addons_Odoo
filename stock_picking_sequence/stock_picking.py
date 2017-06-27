# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class stock_picking(osv.Model):

    _inherit = "stock.picking"

    _columns= {

        'picking_no' : fields.char('Picking Number', readonly=True),

    }

    _defaults= {

        'picking_no' : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').next_by_code(cr,uid,'stock.picking1'),
    }

    _sql_constraints = [

    ('picking_no_unique', 'unique(pickuing_no)', 'Picking Number should be unique.'),
    
    ]


    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'picking_no': self.pool.get('ir.sequence').next_by_code(cr, uid, 'stock.picking1'),
        })
        return super(stock_picking, self).copy(cr, uid, id, default, context=context)


