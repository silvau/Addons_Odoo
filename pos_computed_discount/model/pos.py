# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields


class PosCategory(orm.Model):
    _inherit = 'pos.category'

    _columns = {
        'is_auction': fields.boolean('Auction'),
    }

    def on_change_parent_id(self, cr, uid, ids, parent_id, context=None):
        res = {'value': {}}
        if parent_id:
            parent = self.browse(cr, uid, parent_id, context)
            res['value']['is_auction'] = parent.is_auction

        return res

    def write(self, cr, uid, ids, vals, context=None):
        for categ_id in ids:
            if 'is_auction' in vals:
                child_ids = self.search(
                    cr, uid, [('parent_id', '=', categ_id)])
                self.write(
                    cr, uid, child_ids, {'is_auction': vals['is_auction']},
                    context)

        return super(PosCategory, self).write(cr, uid, ids, vals, context)


class PosConfig(orm.Model):
    _inherit = 'pos.config'

    _columns = {
        'special_discount_password': fields.char("Special discount password", password=True),
        'discount_amount': fields.float(
            'Discounted Amount', digits_compute=dp.get_precision('Account')),
        'discount_journal_id': fields.many2one(
            'account.journal', 'Discounted Journal', required=True),
        'discount_percent': fields.float(
            'Discount (%)', digits=(16, 2)),
        'discount_inapam_percent': fields.float(
            'Discount (%)', digits=(16, 2)),
        'discount_quantity': fields.float('Discounted Quantity'),
        'discount_quantity_percent': fields.float(
            'Discount (%)', digits=(16, 2)),
    }


class PosOrderLine(orm.Model):
    _inherit = 'pos.order.line'

    _columns = {
        'seller_id': fields.many2one('hr.employee', 'Seller'),
    }
