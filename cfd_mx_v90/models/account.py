# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.fields import Char, Selection
from openerp.models import Model, api, _

categorias = [
    ('iva', 'IVA'),
    ('ieps', 'IEPS'),
    ('iva_ret', 'Ret. IVA'),
    ('isr_ret', 'Ret. ISR')
]


class AccountTax(Model):
    _inherit = 'account.tax'

    categoria = Selection(categorias, string="Categoria CFD")


class ResCurrency(Model):
    _inherit = 'res.currency'

    nombre_largo = Char("Nombre largo", size=256,
            help="Ejemplo: dólares americanos, francos suizos")