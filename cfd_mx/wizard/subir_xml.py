# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: jsolorzano@zeval.com.mx
#    Manager: Orlando Zentella ozentella@zeval.com.mx
############################################################################
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

from openerp.osv import osv, fields
import base64
import re

class subir_xml(osv.TransientModel):
    _name = 'cfd_mx.subir.xml'
    
    _columns = {
        'archivo_xml': fields.binary("XML"),
        'archivo_pdf': fields.binary("PDF")
    }
    
    def _get_campo(self, xml, campo):
        m = re.search('%s="(.*?)"'%campo, xml)
        if m:
            return m.group(1)
        return ""
        
    
    def action_subir(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        inv_obj = self.pool.get("account.invoice")
        invoice = inv_obj.browse(cr, uid, context["active_id"])
        xml = this.archivo_xml.decode("base-64")
        uuid = self._get_campo(xml, "UUID")
        fecha_timbrado = self._get_campo(xml, "FechaTimbrado")
        certificado_sat = self._get_campo(xml, "noCertificadoSAT")
        sello_sat = self._get_campo(xml, "selloSAT")
        cadena_sat = re.sub("(.{80})", "\\1\n", '||1.0|%s|%s|%s|%s||'%(uuid.lower(), fecha_timbrado,
                    sello_sat, certificado_sat), 0, re.DOTALL)
        vals = {
            'uuid': uuid.replace("-", ""),
            'fecha_timbrado': fecha_timbrado,
            'sello_sat': sello_sat,
            'certificado_sat': certificado_sat,
            'cadena_sat': cadena_sat
        }
        inv_obj.write(cr, uid, invoice.id, vals)
        att_obj = self.pool.get("ir.attachment")
        xml_att_values = {
          'name': uuid + ".xml",
          'datas': this.archivo_xml,
          'datas_fname': uuid + ".xml",
          'description': uuid,
          'res_model': "account.invoice",
          'res_id': invoice.id,
        }
        att_obj.create(cr, uid, xml_att_values, context=context)
        if this.archivo_pdf:
            pdf_att_values = {
                'name': uuid + ".pdf",
                'datas': this.archivo_pdf,
                'datas_fname': uuid + ".pdf",
                'description': uuid,
                'res_model': "account.invoice",
                'res_id': invoice.id,
            }
            att_obj.create(cr, uid, pdf_att_values, context=context)
        return True        
