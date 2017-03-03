# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm

class stock_production_lot(osv.osv):
 
    _inherit = 'stock.production.lot'

    _columns= {


        'category_id': fields.related('product_id', 'categ_id', type='many2one', relation='product.category', string='Product Category'),

     }
