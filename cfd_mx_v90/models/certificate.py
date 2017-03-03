# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp.fields import Char, Selection, One2many, Integer, Many2one, Binary, Date
from openerp.models import Model, api, _
from openerp.exceptions import Warning

from openerp.addons.cfd_mx.cfdi_utis.files import TempFileTransaction
from openerp.addons.cfd_mx.cfdi_utis import openssl


class certificate(Model):
    _name = 'cfd_mx.certificate'

    serial = Char("Número de serie", size=64, required=True)
    cer = Binary('Certificado', filters='*.cer,*.certificate,*.cert',
                 required=True)
    key = Binary('Llave privada', filters='*.key', required=True)
    key_password = Char('Password llave', size=64, invisible=False,
                        required=True)
    cer_pem = Binary('Certificado formato PEM',
                     filters='*.pem,*.cer,*.certificate,*.cert')
    key_pem = Binary('Llave formato PEM', filters='*.pem,*.key')
    pfx = Binary('Archivo PFX', filters='*.pfx')
    pfx_password = Char('Password archivo PFX', size=64, invisible=False)
    start_date = Date('Fecha inicio', required=False)
    end_date = Date('Fecha expiración', required=True)
    company_id = Many2one('res.company', 'Compañía', required=True,
            default=lambda self: self.env.user.company_id.id)

    @api.onchange('cer')
    def onchange_cer(self):
        tmpfiles = TempFileTransaction()
        if not isinstance(self.cer,(bool)):
            fname_cer = tmpfiles.decode_and_save(self.cer)
            self.serial = openssl.get_serial(fname_cer)
            self.start_date, self.end_date = openssl.get_dates(fname_cer)
            tmpfiles.clean()
        return {
            'value': {
                    'serial': self.serial,
                    'start_date': self.start_date,
                    'end_date': self.end_date
                     }
               }
 
    @api.multi
    def button_generate_pem(self):
        tmpfiles = TempFileTransaction()
        try:
            cer = tmpfiles.decode_and_save(self.cer)
            key = tmpfiles.decode_and_save(self.key)
            cer_pem = openssl.cer_to_pem(cer)
            key_pem = openssl.key_to_pem(key, self.key_password)
            tmpfiles.add_file(cer_pem)
            tmpfiles.add_file(key_pem)
            cer_pem_b64 = tmpfiles.load_and_encode(cer_pem)
            key_pem_b64 = tmpfiles.load_and_encode(key_pem)
        finally:
            tmpfiles.clean()
        self.write({'cer_pem': cer_pem_b64, 'key_pem': key_pem_b64})

    @api.multi
    def button_generate_pfx(self):
        if not self.cer_pem and self.key_pem:
            raise Warning("No se han subido o creado los archivos PEM")

        if not self.pfx_password:
            raise Warning("Se debe definir un password para el archivo pfx")
        tmpfiles = TempFileTransaction()
        try:
            cer_pem = tmpfiles.decode_and_save(self.cer_pem)
            key_pem = tmpfiles.decode_and_save(self.key_pem)
            pfx = openssl.cer_and_key_to_pfx(cer_pem, key_pem, self.pfx_password)
            tmpfiles.add_file(pfx)
            pfx_b64 = tmpfiles.load_and_encode(pfx)
        finally:
            tmpfiles.clean()
        self.write({'pfx': pfx_b64})

        return True



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: