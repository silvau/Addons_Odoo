# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.fields import Char, Selection
from openerp.models import Model, api, _


class AccountJournal(Model):
    _inherit = 'account.journal'

    lugar = Char('Lugar de expedición', size=128)
    serie = Char('Serie', size=32)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: