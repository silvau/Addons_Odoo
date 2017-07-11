# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import pdb
class stock_picking(osv.Model):

    _inherit = "stock.picking"

    _columns= {

        'picking_no' : fields.char('Picking Number', readonly=True),

    }


    _sql_constraints = [

    ('picking_no_unique', 'unique(picking_no)', 'Picking Number should be unique.'),
    
    ]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context={} 
        vals['picking_no']= self.pool.get('ir.sequence').next_by_code(cr,uid,'stock.picking1')
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
 
