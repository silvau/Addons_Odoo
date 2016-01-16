# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from openerp.osv import orm, fields


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'

    _columns = {
        'seller': fields.boolean('POS Seller'),
    }
