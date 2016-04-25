# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, orm

class AccountReportPartnersLedgerWizard(orm.TransientModel):

    """Will launch partner ledger report and pass required args"""

    _inherit = "partners.ledger.webkit"

    _columns = {
        'account_ids': fields.many2many(
            'account.account',
            string='Filter on accounts',
            help="Only selected accounts will be printed. "
            "Leave empty to print all accounts."),
    }
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountReportPartnersLedgerWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        if context is None:
            context = {}
        vals = self.read(cr, uid, ids,
                         ['account_ids'],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_partner_ledger_by_account',
                    'datas': data}
        else:
            return super(partner_ledger_webkit_wizard, self)._print_report(
                cr, uid, ids, data, context=context)

