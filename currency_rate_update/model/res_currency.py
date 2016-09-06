# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date
from openerp.osv import fields, osv
from openerp.tools.translate import _

from ..services import update_service_MX_BdM
_logger = logging.getLogger(__name__)

class res_currency(osv.osv):
    _inherit = 'res.currency'

    def refresh_currency(self, cr, uid, ids, context=None):
        """Refresh the currencies rates !!for all companies now"""
        _logger.info('  ** Starting to refresh currencies with service %s', ids)
        if context is None:
            context = {}
        rate_obj = self.pool.get('res.currency.rate')
        rate = 0.0
        currency_obj = self.pool.get('res.currency')
        for res in currency_obj.browse(cr, uid, ids, context=context):
            try:                
                rate_brw = rate_obj.search(cr, uid, [('name', 'like', context.get('date_cron')), ('currency_id', '=', res.id)])
                rate = update_service_MX_BdM.rate_retrieve()
                vals = {
                    'name': context.get('date_cron'),
                    'currency_id': res.id,
                    'rate': rate
                }
                if not rate_brw:
                    rate_obj.create(cr, uid, vals, context=context)
                    _logger.info('  ** Create currency rate %s -- date %s',self.name, context.get('date_cron'))
                else:
                    rate_obj.write(cr, uid, vals, context=context)
                    _logger.info('  ** Update currency rate %s -- date %s',self.name, context.get('date_cron'))
            except:
                pass
        return rate

    def run_currency_update(self, cr, uid, context=None):
        _logger.info(' === Starting the currency rate update cron')
        currency_obj = self.pool.get('res.currency')
        today = date.today()
        services = {
            'cron': True,
            'date_cron': '%s'%(today)
        }
        currency_ids = currency_obj.search(cr, uid, [('name', 'in', ('MN', 'MXN'))], context=services)
        for res in currency_obj.browse(cr, uid, currency_ids):
            currency_obj.refresh_currency(cr, uid, [res.id], context=services)
            _logger.info(' === End of the currency rate update cron')
        return True

    def _run_currency_update(self, cr, uid, context=None):
        if context is None:
            context = {}
        self.run_currency_update(cr, uid)
        return True
        