# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Zenpar - http://www.zeval.com.mx/
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
import os
import tempfile
import qrcode
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import time

class import_fac(osv.TransientModel):
    _name = "subir_factura.import.fac"

    _columns = {
        'codigo': fields.char(u"Código"),
        'estado': fields.char(u"Estado"),
        'ok': fields.boolean("Ok"),
        'xml': fields.binary(u'Archivo xml', required=True),
        'pdf': fields.binary(u'Archivo pdf', required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
    }
    
    def _get_default_moneda(self, cr, uid, context=None):
        res = self.pool.get('res.currency').search(cr, uid, [('name','=','MXN')], context=context)
        return res and res[0] or False

    _defaults = {

        'moneda': _get_default_moneda,

    }

    def action_subir(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid,ids[0])
        xml = base64.decodestring(this.xml)
        uuid, codigo, estado = self.pool.get("import_factura.subir")._validar_en_hacienda(cr, uid, xml)
        ok = True if codigo.startswith('S') and estado == 'Vigente' else False
        self.write(cr, uid, this.id, {'ok': ok, 'estado': estado, 'codigo': codigo})
        return {
            'view_mode': 'form',
            'view_type': 'form',
            'name': 'Importar factura',
            'res_model': 'subir_factura.import.fac',
            'res_id': this.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [],
            'target': 'new'
        }
        
    def action_procesar(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid,ids[0])
        xml = base64.decodestring(this.xml)
        data = self.get_invoice_data(cr, uid, xml, this)
        invoice_obj = self.pool.get("account.invoice")
        data["currency_id"] = this.moneda.id
        data["creada_de_xml"] = True
        if invoice_obj.search(cr, uid, [('uuid','=',data["uuid"])]):
            raise osv.except_osv("Error", "Ya se tiene en el sistema una factura con el UUID %s"%data["uuid"])
        res_id = invoice_obj.create(cr, uid, data) 
        att_obj = self.pool.get("ir.attachment")
        xml_att_values = {
          'name': data["uuid"] + ".xml",
          'datas': this.xml,
          'datas_fname': data["uuid"] + ".xml",
          'description': data["uuid"],
          'res_model': "account.invoice",
          'res_id': res_id,
        }
        pdf_att_values = {
            'name': data["uuid"] + ".pdf",
            'datas': this.pdf,
            'datas_fname': data["uuid"] + ".pdf",
            'description': data["uuid"],
            'res_model': "account.invoice",
            'res_id': res_id,
        }
        att_obj.create(cr, uid, xml_att_values, context=context)
        att_obj.create(cr, uid, pdf_att_values, context=context)
        invoice_obj.button_compute(cr, uid, [res_id], context=context)
        view_ids=self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'account.invoice'),('name','=','account.invoice.form'),], context=context)
        

        return {
            'view_mode': 'form',
            'view_type': 'form',
            'view_id' : view_ids and view_ids[0] or 0,
            'name': 'Invoice',
            'res_model': 'account.invoice',
            'res_id': res_id,
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [],
        }
            
    def get_invoice_data(self, cr, uid, xml, wizard, context=None):
        if context is None: context = {}
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        journal_ids = self.pool.get("account.journal").search(cr, uid, [('type', '=', 'sale'), ('company_id', '=', uid_company_id)], limit=1)
        data = {
            'type': 'out_invoice',
            'journal_id': journal_ids and journal_ids[0] or False
        }
        root = ET.fromstring(xml)
        partner_obj = self.pool.get("res.partner")
        data["date_invoice"] = root.attrib["fecha"].split("T")[0]
        data["hora_factura"] = root.attrib["fecha"].split("T")[1]
        data["sello"] = root.attrib["sello"]
        data["cuentaBanco"] = 'NumCtaPago' in root.attrib and root.attrib["NumCtaPago"] or ""
        data["tipo_cambio"] = 'TipoCambio' in root.attrib and root.attrib["TipoCambio"] or 1.0
        if root.attrib.get("folio", False):
            data["origin"] = root.attrib["folio"]
        descuento = root.attrib.get("descuento", None)
        data["check_total"] = root.attrib["total"]
        for node in root:
            if node.tag.endswith("Receptor"):
                vat = node.attrib["rfc"]
                partner_id = partner_obj.search(cr, uid, [('vat', '=', vat)])
                if not partner_id:
                    raise osv.except_osv("Error", u"No se encontró en el sistema un cliente con el RFC %s"%vat)
                partner = partner_obj.browse(cr, uid, partner_id[0])
                data["partner_id"] = partner.id
                data["account_id"] = partner.property_account_receivable.id
            if node.tag.endswith("Emisor"):
                company_vat = node.attrib["rfc"]
            elif node.tag.endswith("Conceptos"):
                analytic_id = False
                ir_values = self.pool.get("ir.values")
                client_taxes_id = ir_values.get_default(cr, uid, 'product.product', 'taxes_id', company_id=uid_company_id)
                taxes = isinstance(client_taxes_id, list) and client_taxes_id[0] or client_taxes_id
                for concepto in node:
                    line_vals = {}
                    line_vals["product_id"] = False
                    line_vals['invoice_line_tax_id'] = [(4,taxes)]
                    line_vals["name"] = concepto.attrib["descripcion"]
                    line_vals["quantity"] = concepto.attrib["cantidad"]
                    line_vals["price_unit"] = concepto.attrib["valorUnitario"]
                    data.setdefault("invoice_line", []).append((0,0,line_vals))
                if descuento:
                    disc_line_vals = {
                        'name': 'Descuento',
                        'quantity': 1,
                        'price_unit': -float(descuento),
                        'account_id': self.pool.get("account.invoice.line")._default_account_id(cr, uid),
                        'invoice_line_tax_id': [(4, taxes)]
                    }
                    data.setdefault("invoice_line", []).append((0,0,disc_line_vals))
            elif node.tag.endswith("Complemento"):
                for nodecomp in node:
                    if nodecomp.tag.endswith("TimbreFiscalDigital"):
                        data["uuid"] = nodecomp.attrib["UUID"].replace("-", "")
                        data["fecha_timbrado"] = nodecomp.attrib["FechaTimbrado"]
                        data["sello_sat"] = nodecomp.attrib["selloSAT"]
                        data["sello"] = nodecomp.attrib["selloCFD"]
                        data["certificado_sat"] = nodecomp.attrib["noCertificadoSAT"]
                        if data["sello_sat"][0]=="2":
                            data["test"]=True
                        else:
                            data["test"]=False
                        data["cadena_sat"] = re.sub("(.{80})", "\\1\n", '||1.0|%s|%s|%s|%s||'%(data["uuid"].lower(), data["fecha_timbrado"],
                        data["sello_sat"], data["certificado_sat"]), 0, re.DOTALL)
        data["qrcode"]=self._make_qrcode({
                                        'amount_total': data["check_total"],
                                        'client_vat':vat,
                                        'company_vat':company_vat,
                                        'uuid':data["uuid"]
                                        })

            
        return data


    def _make_qrcode(self, info):
        total = info["amount_total"]
        integer, decimal = str(total).split('.')
        padded_total = integer.rjust(10, '0') + '.' + decimal.ljust(6, '0')
        data = '?re=%s&rr=%s&tt=%s&id=%s'%(info["company_vat"], info["client_vat"],\
                                           padded_total, info["uuid"])
        img = qrcode.make(data)
        fp, tmpfile = tempfile.mkstemp()
        img.save(tmpfile, 'PNG')
        res = base64.b64encode(open(tmpfile, 'rb').read())
        os.unlink(tmpfile)
        return res
