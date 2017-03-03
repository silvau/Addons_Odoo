# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _


class regimen(models.Model):
    _name = "cfd_mx.regimen"

    name = fields.Char("Regimen Fiscal", size=128)

ADDRESS_FIELDS2 = ('street', 'street2', 'colonia_id', 'zip', 'city', 'ciudad_id', 'municipio_id', 'state_id', 'country_id', 'noExterior', 'noInterior')

class partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    xml_cfdi_sinacento = fields.Boolean(string='XML CFDI sin acentos', default=False)
    regimen_id = fields.Many2one('cfd_mx.regimen', string="Regimen Fiscal")
    metodo_pago = fields.Many2one("cfd_mx.formapago", string="Metodo de pago")
    noInterior = fields.Char(string='No. interior',size=64)
    noExterior = fields.Char(string='No. exterior',size=64)
    


    def _address_fields_2(self, cr, uid, context=None):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        return list(ADDRESS_FIELDS2)

    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
              "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        if getattr(address, 'noExterior', None):
            args['noExterior'] = address.noExterior or ''
        if getattr(address, 'noInterior', None):
            args['noInterior'] = address.noInterior or ''
        # if getattr(address, 'colonia_name', None):
        #     args['colonia_name'] = address.colonia_id and address.colonia_id.name or ''
        if getattr(address, 'ciudad_name', None):
            args['ciudad_name'] = address.ciudad_id and address.ciudad_id.name or ''
        if getattr(address, 'municipio_name', None):
            args['municipio_name'] = address.municipio_id and address.municipio_id.name or ''

        for field in self._address_fields_2(cr, uid, context=context):
            try:
                args[field] = getattr(address, field) or ''
            except:
                pass
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: