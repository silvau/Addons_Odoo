# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import models
import wizard
import report

from openerp import SUPERUSER_ID


def _auto_install_l10n(cr, registry):

    #check the country of the main company (only) and eventually load some module needed in that country
    country_code = registry['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID, {}).company_id.country_id.code
    if country_code:
        module_list_install = []
        module_list_uninstall = []
        if country_code in ['MX']:
            # module_list.append('l10n_mx', 'base_vat_mx')
            module_list_install.append('base_vat_mx')
            module_list_uninstall.append('base_vat')
        module_ids = registry['ir.module.module'].search(cr, SUPERUSER_ID, [('name', 'in', module_list_install), ('state', '=', 'uninstalled')])
        registry['ir.module.module'].button_install(cr, SUPERUSER_ID, module_ids, {})

        module_ids = registry['ir.module.module'].search(cr, SUPERUSER_ID, [('name', 'in', module_list_uninstall), ('state', '=', 'installed')])
        registry['ir.module.module'].button_uninstall(cr, SUPERUSER_ID, module_ids, {})
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: