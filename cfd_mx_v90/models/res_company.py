# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from openerp.fields import  Char, Many2one, Selection, Boolean, Many2many
from openerp.models import Model


class company(Model):
    _inherit = 'res.company'

    # Fields
    cfd_mx_test = Boolean(string='Timbrar en modo de prueba', default=True)
    cfd_mx_test_nomina = Boolean(string=u'Timbrar en modo de prueba (nómina)')
    cfd_mx_version = Selection(
                        [('2.2', 'CFD 2.2'), 
                        ('3.2', 'CFDI 3.2')],
                        string='Versión', required=True, default='3.2')
    cfd_mx_pac = Selection(
                        [('zenpar', 'Zenpar (EDICOM)'), 
                        ('tralix', 'Tralix'),
                        ('finkok', 'Finkok')], 
                        string="PAC", default='zenpar')
    cfd_mx_journal_ids = Many2many("account.journal", string="Diarios")

    cfd_mx_tralix_key = Char(string="Tralix Customer Key", size=64)
    cfd_mx_tralix_host = Char(string="Tralix Host", size=256)
    cfd_mx_tralix_host_test = Char(string="Tralix Host Modo Pruebas", size=256)
    
    cfd_mx_finkok_user = Char(string="Finkok User", size=64)
    cfd_mx_finkok_key = Char(string="Finkok Password", size=64)
    cfd_mx_finkok_host = Char(string="Finkok URL Stamp", size=256)
    cfd_mx_finkok_host_cancel = Char(string="Finkok URL Cancel", size=256)
    cfd_mx_finkok_host_test = Char(string="Finkok URL Stamp Modo Pruebas", size=256)
    cfd_mx_finkok_host_cancel_test = Char(string="Finkok URL Cancel Modo Pruebas", size=256)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: