# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.fields import Char, Selection, One2many, Integer, Many2one
from openerp.models import Model, api, _


class IrSequence(Model):
    _inherit = 'ir.sequence'

    aprobacion_ids = One2many("cfd_mx.aprobacion", 'sequence_id',
                              'Aprobaciones')


class Aprobacion(Model):
    _name = 'cfd_mx.aprobacion'

    anoAprobacion = Integer("Año de aprobación", required=True)
    noAprobacion = Char("No. de aprobación", required=True)
    serie = Char("Serie", size=8)
    del_field = Integer("Del", required=True, oldname='del')
    al = Integer("Al", required=True)
    sequence_id = Many2one("ir.sequence", "Secuencia", required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: