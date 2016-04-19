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

from collections import defaultdict
from datetime import datetime

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.addons.account_financial_report_webkit.report import partners_ledger
import pdb
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser
import pdb

class PartnersLedgerWebkit_oisa(report_sxw.rml_parse,
                           CommonPartnersReportHeaderWebkit):


    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will
           be used by mako template"""
        new_ids = data['form']['chart_account_id']
        # account partner memoizer
        # Reading form
        main_filter = self._get_form_param('filter', data, default='filter_no')
        target_move = self._get_form_param('target_move', data, default='all')
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        fiscalyear = self.get_fiscalyear_br(data)
        partner_ids = self._get_form_param('partner_ids', data)
        result_selection = self._get_form_param('result_selection', data)
        chart_account = self._get_chart_account_id_br(data)

        if main_filter == 'filter_no' and fiscalyear:
            start_period = self.get_first_fiscalyear_period(fiscalyear)
            stop_period = self.get_last_fiscalyear_period(fiscalyear)

        # Retrieving accounts
        filter_type = ('payable', 'receivable')
        if result_selection == 'customer':
            filter_type = ('receivable',)
        if result_selection == 'supplier':
            filter_type = ('payable',)
        pdb.set_trace()
        accounts = self.get_all_accounts(new_ids, exclude_type=['view'],
                                         only_type=filter_type)

        if not accounts:
            raise osv.except_osv(_('Error'), _('No accounts to print.'))

        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period

        # when the opening period is included in the selected range of periods
        # and the opening period contains move lines, we must not compute the
        # initial balance from previous periods but only display the move lines
        # of the opening period we identify them as:
        #  - 'initial_balance' means compute the sums of move lines from
        #    previous periods
        #  - 'opening_balance' means display the move lines of the opening
        #    period
        init_balance = main_filter in ('filter_no', 'filter_period')
        initial_balance_mode = init_balance and self._get_initial_balance_mode(
            start) or False

        initial_balance_lines = {}
        if initial_balance_mode == 'initial_balance':
            initial_balance_lines = self._compute_partners_initial_balances(
                accounts, start_period, partner_filter=partner_ids,
                exclude_reconcile=False)

        ledger_lines = self._compute_partner_ledger_lines(
            accounts, main_filter, target_move, start, stop,
            partner_filter=partner_ids)
        objects = []
        for account in self.pool.get('account.account').browse(
                self.cursor, self.uid, accounts, context=self.localcontext):
            account.ledger_lines = ledger_lines.get(account.id, {})
            account.init_balance = initial_balance_lines.get(account.id, {})
            # we have to compute partner order based on inital balance
            # and ledger line as we may have partner with init bal
            # that are not in ledger line and vice versa
            ledg_lines_pids = ledger_lines.get(account.id, {}).keys()
            if initial_balance_mode:
                non_null_init_balances = dict(
                    [(ib, amounts) for ib, amounts
                     in account.init_balance.iteritems()
                     if amounts['init_balance']
                     or amounts['init_balance_currency']])
                init_bal_lines_pids = non_null_init_balances.keys()
            else:
                account.init_balance = {}
                init_bal_lines_pids = []

            account.partners_order = self._order_partners(
                ledg_lines_pids, init_bal_lines_pids)
            objects.append(account)

        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,
            'partner_ids': partner_ids,
            'chart_account': chart_account,
            'initial_balance_mode': initial_balance_mode,
        })

        return super(PartnersLedgerWebkit_oisa, self).set_context(
            objects, data, new_ids, report_type=report_type)
