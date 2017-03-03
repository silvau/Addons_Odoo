# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.fields import Char, Selection, Many2many, Boolean, Many2one, Float, Integer, Text, Binary
from openerp.models import Model, TransientModel, api, _
from openerp.exceptions import Warning, UserError, RedirectWarning, ValidationError
from openerp.tools import float_is_zero
from openerp.tools.misc import formatLang
from openerp.osv import osv

import openerp.addons.decimal_precision as dp

from openerp.addons.cfd_mx.cfdi_utis.validar_xml import validate_xml_schema
from openerp.addons.cfd_mx.cfdi_utis.files import TempFileTransaction
from openerp.addons.cfd_mx.cfdi_utis.nodo import Nodo
from openerp.addons.cfd_mx.cfdi_utis.amount_to_text_es_MX import amount_to_text
from openerp.addons.cfd_mx.cfdi_utis import openssl
from openerp.addons.cfd_mx.cfdi_utis import tralix
from openerp.addons.cfd_mx.cfdi_utis import finkok

import os
import inspect
import codecs
import base64
from datetime import date, datetime
import xml.etree.ElementTree as ET
from lxml import etree

import suds
from suds.client import Client
import zipfile
import logging
import qrcode
import re
from pytz import timezone
import tempfile
import sys

import unicodedata

def remove_accents(s):
    def remove_accent1(c):
        return unicodedata.normalize('NFD', c)[0]
    return u''.join(map(remove_accent1, s))

finkok_errors = {
    '201' : "UUID Cancelado exitosamente",
    '202' : "UUID Previamente cancelado",
    '203' : "UUID No corresponde el RFC del Emisor y de quien solicita la cancelación",
    '205' : "UUID No existe",
    '300' : "Usuario y contraseña inválidos",
    '301' : "XML mal formado",
    '302' : "Sello mal formado o inválido",
    '303' : "Sello no corresponde a emisor",
    '304' : "Certificado Revocado o caduco",
    '305' : "La fecha de emisión no esta dentro de la vigencia del CSD del Emisor",
    '306' : "El certificado no es de tipo CSD",
    '307' : "El CFDI contiene un timbre previo",
    '308' : "Certificado no expedido por el SAT",
    '401' : "Fecha y hora de generación fuera de rango",
    '402' : "RFC del emisor no se encuentra en el régimen de contribuyentes",
    '403' : "La fecha de emisión no es posterior al 01 de enero de 2012",
    '501' : "Autenticación no válida",
    '703' : "Cuenta suspendida",
    '704' : "Error con la contraseña de la llave Privada",
    '705' : "XML estructura inválida",
    '706' : "Socio Inválido",
    '707' : "XML ya contiene un nodo TimbreFiscalDigital",
    '708' : "No se pudo conectar al SAT",
}

class addendas(Model):
    _name = 'cfd_mx.conf_addenda'

    model_selection = Selection(selection=[])
    partner_ids = Many2many('res.partner', string="Clientes", domain=[('customer', '=', True )] )
    model = Char('Modelo de la addenda')

    def create_addenda(self, Nodo, invoice, comprobante):
        context = self._context or {}
        return True


#Esto es forma de pago (una sola exhibicion, etc)
class TipoPago(Model):
    _name = "cfd_mx.tipopago"
    name = Char("Descripcion", size=128, required=True)


#Esto es metodo de pago (transferencia, etc)
class FormaPago(Model):
    _name = 'cfd_mx.formapago'

    name = Char(string="Descripcion", size=64, required=True)
    clave = Char(string="Clave", help="Clave del catálogo del SAT")
    banco = Boolean(string="Banco", help="Activar este checkbox para que pregunte número de cuenta")
    pos_metodo = Many2one('account.journal', domain=[('journal_user', '=', 1)],
            string="Metodo de pago del TPV")


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'discount', 
        'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual')
    def _get_discount(self):
        descuento = 0.0
        for line in self.invoice_line_ids:
            if line.discount:
                descuento +=  ((line.discount or 0.0) / 100.0) * (line.price_unit * line.quantity)
        self.discount = descuento

    @api.one
    @api.depends('cfd_mx_pac')
    def _get_cfd_mx_pac(self):
        self.cfd_mx_pac = self.company_id.cfd_mx_pac


    # Fields 
    discount = Float(string='Descuento', compute='_get_discount')
    cuentaBanco = Char(string='Ultimos 4 digitos cuenta', size=4, default='')
    anoAprobacion = Integer(string=u"Año de aprobación")
    noAprobacion = Char(string="No. de aprobación")
    serie = Char(string="Serie", size=8)
    formapago_id = Many2one('cfd_mx.formapago', string=u'Método de Pago')
    tipopago_id = Many2one('cfd_mx.tipopago', string=u'Forma de Pago')
    sello = Char(string="Sello")
    cadena = Text(string="Cadena original")
    noCertificado = Char(string="No. de serie del certificado", size=64)
    cantLetra = Char(string="Cantidad en letra", size=256)
    hora = Char(string="Hora", size=8)
    uuid = Char(string='Timbre fiscal', size=32)
    hora_factura = Char(string='Hora', size=16)
    qrcode = Binary(string="Codigo QR")
    test = Boolean(string="Timbrado en modo de prueba")
    sello_sat = Char(string="Sello del SAT", size=64)
    certificado_sat = Char(string="No. Certificado del SAT", size=64)
    fecha_timbrado = Char(string="Fecha de Timbrado", size=32)
    cadena_sat = Text(string="Cadena SAT")
    mandada_cancelar = Boolean(string='Mandada cancelar', default=False)
    tipo_cambio = Float(string="Tipo de cambio")
    mensaje_pac = Text(string='Ultimo mensaje del PAC')
    cfd_mx_pac = Char(string='PAC',compute='_get_cfd_mx_pac')
    xml_cfdi_sinacento = Boolean(related="partner_id.xml_cfdi_sinacento", string='XML CFDI sin acentos')


    # @api.one
    # @api.constrains('uuid')
    # def _check_unique_uuid(self):
    #     if not self.uuid:
    #         return True
    #     inv_ids = self.search([('uuid', 'ilike', self.uuid)])
    #     if inv_ids:
    #         raise UserError('Invoice UUID must be unique')

    @api.model
    def create(self, vals):
        onchanges = {
            'onchange_metododepago': ['partner_id', 'formapago_id', 'cuentaBanco'],
        }
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field])
        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)
        return invoice        

    @api.multi
    def action_cancel_draft(self):
        res = super(AccountInvoice, self).action_cancel_draft()
        self.write({
            'sello_sat': False,
            'certificado_sat': False,
            'fecha_timbrado': False,
            'cadena_sat': False,
            'uuid': False,
            'test': False,
            'qrcode': False,
            'mandada_cancelar': False,
            'mensaje_pac': False,
        })
        return res

    @api.one
    def copy(self, default=None):
        if default is None: default = {}
        default.update({
            'sello_sat': False,
            'certificado_sat': False,
            'fecha_timbrado': False,
            'cadena_sat': False,
            'uuid': False,
            'test': False,
            'qrcode': False,
            'mandada_cancelar': False,
            'mensaje_pac': False,
        })
        new_id = super(AccountInvoice, self).copy(default=default)
        return new_id

    ##
    ## Cancelar CFDI
    ##
    @api.multi
    def action_cancel(self):
        res = self.action_cancel_cfdi()
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def action_cancel_cfdi(self):
        #Si es de proveedor no hacer nada
        if self.type.startswith("in"):
            return True

        #Si no es el journal adecuado no hacer nada
        if self.journal_id.id not in [x.id for x in self.company_id.cfd_mx_journal_ids]:
            return True

        if self.state != 'open':
            raise UserError("El estado no es 'Abierto")

        self._cancel_cfdi()
        self.write({'mandada_cancelar': True})
        return True

    @api.multi
    def _cancel_cfdi(self):
        rfc = self.company_id.partner_id.vat
        uuid = self.uuid

        #Obtener el certificado con el que se firmo el cfd
        certificate_obj = self.env["cfd_mx.certificate"]
        certificate = certificate_obj.search(
                [('serial', '=', self.noCertificado)])

        if certificate:
            pfx_data_b64 = certificate[0].pfx
            pfx_password = certificate[0].pfx_password
            cer_file = certificate[0].cer_pem
            key_file = certificate[0].key_pem
        else:
            raise UserError("El certificado %s no existe" % (self.noCertificado))

        res = ''
        if self.company_id.cfd_mx_pac == 'zenpar':
            config_obj = self.env['ir.config_parameter']
            password = config_obj.get_param('cfd_mx.password')
            url = config_obj.get_param('cfd_mx.host')
            client = Client(url)
            res = client.service.cancelar(rfc, uuid, pfx_data_b64, pfx_password,
                                          password)

        elif self.company_id.cfd_mx_pac == 'finkok':
            if not self.test and not self.company_id.cfd_mx_finkok_host_cancel:
                raise UserError("No se ha definido la direccion para la cancelacion de Finkok")
            if self.test and not self.company_id.cfd_mx_finkok_host_cancel_test:
                raise UserError("No se ha definido la direccion para la cancelacion de Finkok modo pruebas")
            if not self.company_id.cfd_mx_finkok_user or not self.company_id.cfd_mx_finkok_key:
                raise UserError("No se ha definido user y password de Finkok")
            hostname = self.company_id.cfd_mx_finkok_host_cancel if not self.test else self.company_id.cfd_mx_finkok_host_cancel_test
            username = self.company_id.cfd_mx_finkok_user
            password = self.company_id.cfd_mx_finkok_key
            invoices = [self._format_uuid(uuid)]
            soapresp = finkok.cancelar(hostname, invoices, username, password, rfc, cer_file, key_file)
            message = ''
            try:
                if not soapresp["Acuse"]:
                    message += 'El SAT todavía no tiene este documento disponible para cancelación, inténtelo mas tarde \n'
                    res += 'El SAT todavía no tiene este documento disponible para cancelación, inténtelo mas tarde \n'
                for folios in soapresp["Folios"]:
                    for folio in folios[1]:
                        estatus_uuid = folio["EstatusUUID"]
                        estatus_uuid_msg = 'Estatus %s: %s \n'%(estatus_uuid, finkok_errors.get(estatus_uuid))
                        if estatus_uuid in ['201', '202']:
                            pass
                        else:
                            message += '%s \n'%(estatus_uuid_msg.encode("iso-8859-1"))
                        res += '%s \n'%(estatus_uuid_msg.encode("iso-8859-1"))
                res += '%s'%(soapresp)
            except ValueError, e:
                message += str(e)
            except Exception, e:
                message += str(e)
            if message:
                raise UserError("Error al Cancelar el XML \n\n %s "%( message.upper() ))
                return False
        else:
            raise UserError("No se puede cancelar con el PAC seleccionado")
        self.write({'mandada_cancelar': True, 'mensaje_pac': res})
        return True

    @api.multi
    def get_status_cancel_cfdi(self):
        inv = self
        dict_folios = {}
        cancelacfd = inv.mensaje_pac
        if cancelacfd:
            string_1 = '<s:Envelope'
            string_2 = '</s:Envelope>'
            s_from = cancelacfd.find(string_1)
            s_to = cancelacfd.find(string_2)
            msg_cancel_cfdi = cancelacfd[s_from:(s_to + len(string_2) )]
            msg_cancel_cfdi = '<?xml version="1.0"?>'+msg_cancel_cfdi
            envelope = ET.fromstring(msg_cancel_cfdi)
            body = envelope.getchildren()[0]
            child = body.getchildren()[0]
            if "cancelacfdresponse" in child.tag.lower():
                cancelacfdresponse = child.getchildren()[0]
                folios = cancelacfdresponse.getchildren()[0]
                for f in folios:            
                    if "estatusuuid" in f.tag.lower():
                        dict_folios['estatusuuid'] = f.text.encode("iso-8859-1")
                    elif "uuid" in f.tag.lower():
                        dict_folios['uuid'] = f.text.encode("iso-8859-1")

        return dict_folios

    # @api.onchange('partner_id', 'company_id')
    # def _onchange_partner_id(self):
    #     res = super(AccountInvoice, self)._onchange_partner_id()
    #     self.onchange_metododepago()
    #     # self.formapago_id = self.partner_id.metodo_pago and self.partner_id.metodo_pago.id or None

    @api.multi
    @api.onchange('partner_id', 'formapago_id')
    def onchange_metododepago(self):
        if not self.partner_id:
            self.update({
                'formapago_id': False,
                'cuentaBanco': False,
            })
            return

        if not self.formapago_id:
            self.formapago_id = self.partner_id.metodo_pago and self.partner_id.metodo_pago.id or None
        cuenta = ''
        if self.formapago_id and self.formapago_id.banco:
            if not self.partner_id:
                raise UserError("No se ha definido cliente")
            if self.partner_id.bank_ids:
                for bank in self.partner_id.bank_ids:
                    cuenta = bank.acc_number[-4:]
                    break
            else:
                cuenta = 'xxxx'
        self.cuentaBanco = cuenta

    def get_xml_sinacento(self, xml):
        if self.xml_cfdi_sinacento:
            xml = remove_accents(xml)
        return xml

    def get_temp_file_trans(self):
        return TempFileTransaction()
    
    def get_openssl(self):
        return openssl

    def _format_uuid(self, uuid):
        return uuid[0:8]+'-'+uuid[8:12]+'-'+uuid[12:16]+'-'+uuid[16:20]+'-'+uuid[20:32]  


    @api.multi
    def make_qrcode(self):        
        uuid = self._format_uuid(self.uuid)
        self.write({
            'qrcode': self._make_qrcode(uuid)
        })

    @api.multi
    def _make_qrcode(self, uuid):        
        total = self.amount_total
        integer, decimal = str(total).split('.')
        padded_total = integer.rjust(10, '0') + '.' + decimal.ljust(6, '0')
        data = '?re=%s&rr=%s&tt=%s&id=%s' % (
                                    self.company_id.vat,
                                    self.partner_id.vat, 
                                    padded_total, 
                                    uuid
                                )
        img = qrcode.make(data)
        fp, tmpfile = tempfile.mkstemp()
        img.save(tmpfile, 'PNG')
        res = base64.b64encode(open(tmpfile, 'rb').read())
        os.unlink(tmpfile)
        return res

    @api.multi
    def _sign_cfdi(self, company_id, xml_data_b64, test):
        if company_id.cfd_mx_pac == 'zenpar':
            test = test and 1 or 0
            rfc = company_id.partner_id.vat
            config_obj = self.env['ir.config_parameter']
            password = config_obj.get_param('cfd_mx.password')
            url = config_obj.get_param('cfd_mx.host')
            client = Client(url)
            return client.service.timbrar(xml_data_b64, test, rfc, password)

        elif company_id.cfd_mx_pac == 'tralix':
            if not company_id.cfd_mx_tralix_key:
                raise UserError("No se ha definido el customer key para el timbrado de Tralix")
            if not test and not company_id.cfd_mx_tralix_host:
                raise UserError("No se ha definido la direccion para el timbrado de Tralix")
            if test and not company_id.cfd_mx_tralix_host_test:
                raise UserError("No se ha definido la direccion para el timbrado de Tralix modo pruebas")
            hostname = company_id.cfd_mx_tralix_host if not test else company_id.cfd_mx_tralix_host_test
            xml_data = xml_data_b64.decode('base64').decode('utf-8').encode('utf-8')
            return tralix.timbrar(xml_data, company_id.cfd_mx_tralix_key,
                                  hostname)
        elif company_id.cfd_mx_pac == 'finkok':
            if not test and not company_id.cfd_mx_finkok_host:
                raise UserError("No se ha definido la direccion para el timbrado de Finkok")
            if test and not company_id.cfd_mx_finkok_host_test:
                raise UserError("No se ha definido la direccion para el timbrado de Finkok modo pruebas")
            if not company_id.cfd_mx_finkok_user or not company_id.cfd_mx_finkok_key:
                raise UserError("No se ha definido user y password de Finkok")
            hostname = company_id.cfd_mx_finkok_host if not test else company_id.cfd_mx_finkok_host_test
            username = company_id.cfd_mx_finkok_user
            password = company_id.cfd_mx_finkok_key
            return finkok.timbrar(hostname, username, password, xml_data_b64)

        else:
            raise UserError("PAC '%s' no es valido" % (company_id.cfd_mx_pac))

    @api.multi
    def _get_certificate(self, company_id):
        certificate_obj = self.env["cfd_mx.certificate"]
        certificate = certificate_obj.search(['&',
            ('company_id', '=', company_id.id),
            ('end_date', '>', date.today().strftime("%Y-%m-%d"))])

        if not certificate:
            raise UserError("No tiene certificados vigentes")

        if not certificate[0].cer_pem or not certificate[0].key_pem:
            raise UserError("No esta el certificado y la llave en formato PEM")

        return certificate

    @api.multi
    def _get_aprobacion(self):
        if not self.journal_id.sequence_id:
            raise UserError("No hay definida una secuencia en el diario")
        try:
            number = int(self.number)
        except ValueError:
            raise UserError("El folio no debe contener letras")

        aprobacion_ids = self.env["cfd_mx.aprobacion"].search(['&', '&',
                ('sequence_id', '=', self.journal_id.sequence_id.id),
                ('del_field', '<=', number),
                ('al', '>=', number)])

        if not aprobacion_ids:
            raise UserError("Este folio no esta aprobado (%s)" % (number))
        if len(aprobacion_ids) != 1:
            raise UserError("Este folio tiene mas de un numero de aprobacion")

        return self.env("cfd_mx.aprobacion").browse(aprobacion_ids)[0].id

    def cant_letra(self, currency, amount):
        if currency.name == 'MXN':
            nombre = currency.nombre_largo or 'pesos'
            siglas = 'M.N.'
        else:
            nombre = currency.nombre_largo or ''
            siglas = currency.name
        return amount_to_text().amount_to_text_cheque(float(amount), nombre,
                                                      siglas).capitalize()

    @api.multi
    def validar_xml(self, xml_sellado):
        current_path = os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe())))
        tmpfiles = TempFileTransaction()
        path_xsd = self._context.get('xml_xsd', '')
        path_xsd = current_path + path_xsd
        validar_xml = ""
        try:
            fname_xml = tmpfiles.save(xml_sellado, 'xml_sin_sello_validar')
            validate = validate_xml_schema(path_xsd, fname_xml)
            validar_xml = validate.validate_xml()
            validar_xml = validate.return_validate()
        except ValueError, e:
            validar_xml = str(e)
        except Exception, e:
            validar_xml = str(e)
        tmpfiles.clean()
        return validar_xml

    @api.multi
    def sellar_xml(self, xml):
        company_id = self.company_id
        version = self.company_id.cfd_mx_version
        tmpfiles = TempFileTransaction()
        xml = self.get_xml_sinacento(xml)
        fname_xml = tmpfiles.save(xml, 'xml_sin_sello')

        current_path = os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe())))

        version = '3.2'
        if version == '2.2':
            fname_xslt = current_path+'/SAT/xslt/cadenaoriginal_2_2.xslt'
        elif version == '3.2':
            fname_xslt = current_path+'/SAT/xslt/cadenaoriginal_3_2.xslt'

        fname_cadena = tmpfiles.create("cadenaori")
        os.system("xsltproc --output %s %s %s" % (fname_cadena, fname_xslt,
                                                  fname_xml))

        certificate = self._get_certificate(company_id)
        fname_cer_pem = tmpfiles.decode_and_save(certificate.cer_pem)
        fname_key_pem = tmpfiles.decode_and_save(certificate.key_pem)

        sello = openssl.sign_and_encode(fname_cadena, fname_key_pem)
        certificado = ''.join(open(fname_cer_pem).readlines()[1:-1])
        certificado = certificado.replace('\n', '')

        cadena = open(fname_cadena, 'rb').read()
        tmpfiles.clean()
        return sello, certificado, certificate.serial, cadena

    #
    # Nodos CFDI
    #
    @api.multi
    def get_nodo_comprobante(self):
        comprobante = None
        version = self.company_id.cfd_mx_version
        test = self.company_id.cfd_mx_test
        ns = version == '3.2' and 'cfdi:' or ''
        if version == '2.2':
            comprobante = Nodo(ns+'Comprobante', {
                'version': '2.2',
                'xmlns': "http://www.sat.gob.mx/cfd/2",
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv22.xsd" 
            })
        elif version == '3.2':
            comprobante = Nodo(ns+'Comprobante', {
                'version': '3.2',
                'xmlns:cfdi': "http://www.sat.gob.mx/cfd/3",
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/3  http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd" 
            })
        else:
            raise UserError("Versión de CFD no valida")

        if version == '2.2':
            aprobacion = self._get_aprobacion()
            comprobante.atributos.update({
                'noAprobacion': aprobacion.noAprobacion,
                'anoAprobacion': aprobacion.anoAprobacion,
                'serie': aprobacion.serie or '',
            })
        return comprobante

    @api.multi
    def get_nodo_comprobante_data(self, comprobante):
        dp = self.env['decimal.precision'].precision_get('Account')
        # Hora de la factura en zona horaria del usuario

        tz = self.env.user.tz
        if not tz:
            raise UserError("El usuaerio no tiene definido Zona Horaria")

        hora_factura_utc = datetime.now(timezone("UTC"))
        hora_factura_local = hora_factura_utc.astimezone(timezone(tz)).strftime("%H:%M:%S")

        #Tipo de cambio
        #--------------
        #Si es pesos poner 1 directo
        if self.currency_id.name == 'MXN':
            rate = 1.0
        #Si no, obtener el tipo de cambio
        #Esto funciona aunque la moneda base no sea el peso
        else:
            model_data = self.env["ir.model.data"]
            mxn_rate = model_data.get_object('base', 'MXN').rate
            rate = (1.0 / self.currency_id.rate) * mxn_rate

        comprobante.atributos.update({
            'serie': self.journal_id.serie or '',
            'Moneda': self.currency_id.name,
            'TipoCambio': round(rate, 4), #De acuerdo al diario oficial de la federacion son 4 decimales
            'NumCtaPago': self.cuentaBanco,
            'LugarExpedicion': self.journal_id and self.journal_id.lugar or "",
            'metodoDePago': self.formapago_id and self.formapago_id.clave or "NA",
            'formaDePago': self.tipopago_id and self.tipopago_id.name or "Pago en una sola exhibicion",
            'fecha': str(self.date_invoice) + "T" + hora_factura_local,
            'folio': self.number,
            'tipoDeComprobante': (self.type == 'out_invoice' and 'ingreso') or (self.type == 'out_refund' and 'egreso'),
            'subTotal': round((self.amount_untaxed or 0.0), dp),
            'total': round((self.amount_total or 0.0), dp),
        })
        if self.discount:
            comprobante.atributos.update({'descuento': round(self.discount, dp)})

    @api.multi
    def get_nodo_comprobante_emisor(self, comprobante):
        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''

        partner_data = self.company_id.partner_id

        emisor = Nodo(ns+'Emisor', {
            'rfc': partner_data.vat or "",
            'nombre': partner_data.name or "",
        }, comprobante)

        domicilioFiscal = Nodo(ns+'DomicilioFiscal', {
            'calle': partner_data.street or "",
            'noExterior': partner_data.noExterior or "",
            'noInterior': partner_data.noInterior or "",
            'localidad': partner_data.city or "",
            'colonia': partner_data.street2 or "",
            'municipio': partner_data.city or "",
            'estado': partner_data.state_id and partner_data.state_id.name or "",
            'pais': partner_data.country_id and partner_data.country_id.name or "",
            'codigoPostal': partner_data.zip or "",
        }, emisor)

        regimenFiscal = Nodo(ns+'RegimenFiscal', {
            'Regimen': partner_data.regimen_id and partner_data.regimen_id.name or ""
        }, emisor)

    @api.multi
    def get_nodo_comprobante_receptor(self, comprobante):
        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''

        partner_data = self.partner_id
        receptor = Nodo(ns +'Receptor', {
            'rfc': partner_data.vat or "",
            'nombre': partner_data.name or "",
        }, comprobante)

        domicilio = Nodo(ns+'Domicilio', {
            'calle': partner_data.street or "",
            'noExterior': partner_data.noExterior or "",
            'noInterior': partner_data.noInterior or "",
            'localidad': partner_data.city or "",
            'colonia': partner_data.street2 or "",
            'municipio': partner_data.city or "",
            'estado': partner_data.state_id and partner_data.state_id.name or "",
            'pais': partner_data.country_id and partner_data.country_id.name or "",
            'codigoPostal': partner_data.zip or "",
        }, receptor)

    @api.multi
    def get_nodo_comprobante_conceptos(self, comprobante):
        dp = self.env['decimal.precision']
        dp_account = dp.precision_get('Account')
        dp_product = dp.precision_get('Product Price')

        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''

        conceptos = Nodo(ns+'Conceptos', padre=comprobante)
        for line in self.invoice_line_ids:
            concepto = Nodo(ns+'Concepto', {
                'descripcion': line.name or "",
                'importe': round(line.price_subtotal, dp_account),
                'valorUnitario': round(line.price_unit, dp_product),
                'cantidad': round(line.quantity, dp_account),
                'unidad': line.uom_id and line.uom_id.name or "",
                'noIdentificacion': line.product_id and line.product_id.default_code or ""
            }, conceptos)


    @api.multi
    def get_nodo_comprobante_impuestos(self, comprobante):
        dp = self.env['decimal.precision'].precision_get('Account')
        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''


        impuestos_traslados = {}
        impuestos_retenidos = {}
        tasas = {}
        cfd_mx_impuestos = {}

        nombres_impuestos = {
            'iva': 'IVA',
            'ieps': 'IEPS',
            'iva_ret': 'IVA',
            'isr_ret': 'ISR'
        }

        for line in self.invoice_line_ids:
            #Por cada partida ver que impuestos lleva.
            #Estos impuestos tienen que tener una de las 4 categorias (iva, ieps, retencion iva, retencion isr)
            for tax in line.invoice_line_tax_ids:
                if not tax.categoria:
                    raise UserError("El impuesto %s no tiene categoria CFD"%(tax.name) )
                # impuesto = nombres_impuestos[tax.categoria]
                impuesto = tax.categoria
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                comp = tax.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)

                importe = comp['total_included'] - comp['total_excluded']
                importe = round(importe, dp)
                if tax.amount_type == 'percent':
                    tasas[impuesto] = round(abs(tax.amount), dp)
                #Traslados
                if tax.categoria in ('iva', 'ieps'):
                    impuestos_traslados.setdefault(impuesto, []).append(importe)
                #Retenciones
                else:
                    impuestos_retenidos.setdefault(impuesto, []).append(importe)


        impuestos = Nodo(ns+'Impuestos', padre=comprobante)
        retenciones = Nodo(ns+'Retenciones', padre=impuestos)
        traslados = Nodo(ns+'Traslados', padre=impuestos)

        totalImpuestosTrasladados = 0
        totalImpuestosRetenidos = 0
        if len(self.tax_line_ids) == 0:
            traslado = Nodo(ns + 'Traslado', {
                  'impuesto':'IVA',
                  'tasa': '0.00',
                  'importe': '0.00'},
                traslados)

        for impuesto in impuestos_retenidos:
            n_impuesto = nombres_impuestos[impuesto]
            importe = abs(sum(impuestos_retenidos[impuesto]))
            Nodo(ns+'Retencion', {
                    'impuesto': n_impuesto,
                    'importe': importe
                }, retenciones)
            totalImpuestosRetenidos += importe

        for impuesto in impuestos_traslados:
            n_impuesto = nombres_impuestos[impuesto]
            importe = sum(impuestos_traslados[impuesto])
            Nodo(ns+'Traslado', {
                    'impuesto': n_impuesto,
                    'importe': importe,
                    'tasa': tasas[impuesto]
                }, traslados)
            totalImpuestosTrasladados += importe

        # if totalImpuestosTrasladados:        
        # if totalImpuestosRetenidos:
        impuestos.atributos['totalImpuestosTrasladados'] = totalImpuestosTrasladados
        impuestos.atributos['totalImpuestosRetenidos'] = totalImpuestosRetenidos
        return True

    @api.multi
    def get_nodo_comprobante_addenda(self, comprobante):
        context = self._context or {}

        dp = self.env['decimal.precision'].precision_get('Account')
        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''

        # ************************ Addenda *********************************
        nodo_addenda = False
        conf_addenda_obj = self.env['cfd_mx.conf_addenda']
        for conf_addenda in conf_addenda_obj.search([('partner_ids', 'in', self.partner_id.ids)]):
            context.update({'model_selection': conf_addenda.model_selection})
            addenda_obj = self.env[conf_addenda.model_selection]
            addenda = addenda_obj.with_context(**context).create_addenda(Nodo, self, comprobante)
            if conf_addenda.model_selection == "cfd_mx.addenda_detallista" or 'complemento' in conf_addenda.model_selection:
                nom_nodo = "Complemento"
            else:
                nom_nodo = "Addenda"
            nodo_addenda = Nodo(ns+nom_nodo).append(addenda)
            addenda_obj.with_context(**context).set_namespace(comprobante, nodo_addenda)
            break
        return nodo_addenda

    @api.multi
    def get_nodo_comprobante_sellar(self, comprobante):
        xml = comprobante.toxml()
        sello, certificado, serial, cadena = self.sellar_xml(xml)
        comprobante.atributos.update({
            'sello': sello,
            'certificado': certificado,
            'noCertificado': serial
        })

        return sello, certificado, serial, cadena

    @api.multi
    def get_nodo_comprobante_timbrar(self, comprobante):
        test = self.company_id.cfd_mx_test
        version = self.company_id.cfd_mx_version
        cfd = self.get_xml_sinacento(comprobante.toxml())
        res = ''
        if version == '3.2':
            cfd_b64 = base64.b64encode(cfd.encode("utf-8"))
            res = self._sign_cfdi(self.company_id, cfd_b64, test)
            if res.startswith('ERROR'):
                m = re.search('text = "(.*?)"', res, re.DOTALL)
                error = m and m.group(1) or res
                raise UserError(error)
        return res

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        if self.type != 'out_invoice':
            return super(AccountInvoice, self).invoice_print()
        return self.env['report'].get_action(self, 'cfd_mx.report_invoice_mx')
    
    @api.multi
    def get_nodo_comprobante_adjuntos(self, cfd):
        attachment_obj = self.env['ir.attachment']
        cfd_b64 = base64.b64encode(cfd.encode("utf-8"))
        fname = "cfd_" + self.number + ".xml"
        attachment_values = {
            'name': fname,
            'datas': cfd_b64,
            'datas_fname': fname,
            'description': 'Comprobante Fiscal Digital',
            'res_model': self._name,
            'res_id': self.id,
        }
        attachment_obj.create(attachment_values)

        data = {
            'ids': self,
            'model': 'account.invoice',
        }        

    @api.multi
    def get_nodo_comprobante_write_cfd(self, cfd, sello, certificado, serial, cadena):
        version = self.company_id.cfd_mx_version
        test = self.company_id.cfd_mx_test

        # Hora de la factura en zona horaria del usuario
        tz = self.env.user.tz
        hora_factura_utc = datetime.now(timezone("UTC"))
        hora_factura_local = hora_factura_utc.astimezone(timezone(tz)).strftime("%H:%M:%S")

        #Tipo de cambio
        #--------------
        #Si es pesos poner 1 directo
        if self.currency_id.name == 'MXN':
            rate = 1.0
        #Si no, obtener el tipo de cambio
        #Esto funciona aunque la moneda base no sea el peso
        else:
            model_data = self.env["ir.model.data"]
            mxn_rate = model_data.get_object('base', 'MXN').rate
            rate = (1.0 / self.currency_id.rate) * mxn_rate

        if version == '2.2':
            aprobacion = self._get_aprobacion()
            comprobante.atributos.update({
                'noAprobacion': aprobacion.noAprobacion,
                'anoAprobacion': aprobacion.anoAprobacion,
                'serie': aprobacion.serie or '',
            })

        #Nombre largo de la moneda. Si es MXN poner 'pesos' a menos que se haya puesto algo en el campo de nombre largo
        #Si no es MXN poner lo que está en el campo de nombre largo o en su defecto el código de la moneda
        self.cantLetra = self.cant_letra(self.currency_id, self.amount_total)

        uuid = re.search('UUID="(.*?)"', cfd).group(1)
        fecha_timbrado = re.search('FechaTimbrado="(.*?)"', cfd).group(1)
        sello_sat = re.search('selloSAT="(.*?)"', cfd).group(1)
        certificado_sat = re.search('noCertificadoSAT="(.*?)"', cfd).group(1)

        sello = re.sub("(.{100})", "\\1\n", sello, 0, re.DOTALL) #saltos de linea cada 100 caracteres
        values = {
            'hora_factura': hora_factura_local,
            'sello': sello,
            'cadena': cadena,
            'noCertificado': serial,
            'cantLetra': self.cantLetra,
            'tipo_cambio': rate,
        }
        if version == '2.2':
            values.update({
                'serie': aprobacion.serie,
                'noAprobacion': aprobacion.noAprobacion,
                'anoAprobacion': aprobacion.anoAprobacion
            })
        elif version == '3.2':
            values.update({
                'uuid': uuid.replace('-',''),
                'serie': self.journal_id.serie or '',
                'qrcode': self._make_qrcode(uuid),
                'test': test,
                'sello_sat': sello_sat,
                'certificado_sat': certificado_sat,
                'fecha_timbrado': fecha_timbrado,
                'cadena_sat': re.sub("(.{80})", "\\1\n", '||1.0|%s|%s|%s|%s||'%(uuid.lower(), fecha_timbrado,
                    sello_sat, certificado_sat), 0, re.DOTALL)
            })
        self.write(values)

    @api.multi
    def action_create_cfd(self):
        
        current_path = os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe())))

        version = self.company_id.cfd_mx_version
        ns = version == '3.2' and 'cfdi:' or ''

        #Si ya tiene UUID no hacer nada
        if self.uuid:
            return True
        #Si no es el journal adecuado no hacer nada
        if self.journal_id.id not in [x.id for x in self.company_id.cfd_mx_journal_ids]:
            return True
        #Si es de proveedor no hacer nada
        if self.type.startswith("in"):
            return True
        #Si no hay terminos de pago mandar warning
        if not self.payment_term_id:
            raise UserError("No se definio termino de pago")
        #Si no hay metodo de pago y es factura de cliente mandar warning
        if not self.formapago_id and not self.type.startswith("in"):
            raise UserError("No se definio metodo de pago")

        self.partner_id.validate_vat()

        sello = certificado = serial = cadena = None
        comprobante = None
        nodo_addenda = None

        message = ''
        try:
            comprobante = self.get_nodo_comprobante()
            self.get_nodo_comprobante_data(comprobante)
            self.get_nodo_comprobante_emisor(comprobante)
            self.get_nodo_comprobante_receptor(comprobante)
            self.get_nodo_comprobante_conceptos(comprobante)
            self.get_nodo_comprobante_impuestos(comprobante)
            sello, certificado, serial, cadena = self.get_nodo_comprobante_sellar(comprobante)
            nodo_addenda = self.get_nodo_comprobante_addenda(comprobante)

            xml = comprobante.toxml()
            message = self.with_context(xml_xsd='/SAT/xsd/cfdv32.xsd').validar_xml(xml)
        except ValueError, e:
            message = str(e)
        except Exception, e:
            message = str(e)

        if message:
            raise UserError("Error al Generar el XML \n\n %s "%( message.upper() ))
            return False
        message = ''
        try:
            cfd = comprobante.toxml()
            cfd = self.get_nodo_comprobante_timbrar(comprobante)
            if nodo_addenda:
                xml_add = nodo_addenda.toxml(header=False)
                end_tag = "</"+ns+"Comprobante>"
                cfd = cfd.replace(end_tag, xml_add + end_tag)
            cfd = self.get_xml_sinacento(cfd)
            self.get_nodo_comprobante_write_cfd(cfd, sello, certificado, serial, cadena)
            self.get_nodo_comprobante_adjuntos(cfd)
        except ValueError, e:
            message = str(e)
        except Exception, e:
            message = str(e)
        if message:
            raise UserError("Error al Generar el XML \n\n %s "%( message.upper() ))
            return False
        self.invoice_print()
        return True


    def _get_xml_datas(self, xml_sellado):
        res = {
            'importe_total': 0.0,
            'version': '1.0',
            'tipo_comprobante': 'ingreso',
            'certificado_sat': '',
            'certificado_emisor': '',
            'fecha_emision': '',
            'fecha_certificacion': '',
            'uuid': '',
            'rfc_emisor': '',
            'nombre_emisor': '',
            'rfc_receptor': '',
            'nombre_receptor': ''
        }
        try:
            root = ET.fromstring(xml_sellado)
        except:
            pass
        res['importe_total'] = float(root.attrib.get("total", False))
        res['version'] = root.attrib.get('version')
        res['tipo_comprobante'] = root.attrib.get('tipoDeComprobante')
        res['certificado_emisor'] = root.attrib.get('noCertificado')
        res['fecha_emision'] = root.attrib.get('fecha')
        for child in root:
            if child.tag.endswith("Emisor"):
                res['nombre_emisor'] = unicode(child.attrib["nombre"]).encode('utf-8')
                res['rfc_emisor'] = child.attrib["rfc"]
            elif child.tag.endswith("Receptor"):
                res['nombre_receptor'] = unicode(child.attrib["nombre"]).encode('utf-8')
                res['rfc_receptor'] = child.attrib["rfc"]
            elif child.tag.endswith("Complemento"):
                for child2 in child:
                    if child2.tag.endswith("TimbreFiscalDigital"):
                        res['uuid'] = child2.attrib["UUID"]
                        res['certificado_sat'] = child2.attrib["noCertificadoSAT"]
                        res['fecha_certificacion'] = child2.attrib["FechaTimbrado"]
        return res


    def _reporte_validacion_xml(self, xml_sellado):
        xml_datas = self._get_xml_datas(xml_sellado)
        validar_xml = """
            <table class="small"  width="95%" style="border-collapse: separate; border-spacing: 0 0px; padding: 0px; padding-top: 0px; padding-bottom: 0px; " cellpadding="0" cellspacing="0" >
                <tbody>
                    <tr><td colspan="2" align="center" bgcolor="#dfe1d2"><h2>Reporte de validación</h2></td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Versión:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{version}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Tipo Comprobante:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{tipo_comprobante}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Certificado SAT:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{certificado_sat}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Certificado Emisor:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{certificado_emisor}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Fecha Emisión:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{fecha_emision}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Fecha Certificación:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{fecha_certificacion}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">UUID:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{uuid}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Importe Total:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{importe_total}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">RFC Emisor:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{rfc_emisor}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Nombre Emisor:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{nombre_emisor}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">RFC Receptor:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{rfc_receptor}</td></tr>
                    <tr><td class="small" style="color:black; font-weight:bold; border-bottom: 1px solid #dfe1d2;" width="25%">Nombre Receptor:</td><td width="75%" style="border-bottom: 1px solid #dfe1d2;">{nombre_receptor}</td></tr> 
                </tbody>
            </table>
            <br />
            <br />
        """.format(**xml_datas)
        return validar_xml


#Para que tambien se mande el xml

class MailComposeMessage(Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposeMessage, self).onchange_template_id(template_id,
                composition_mode, model, res_id)

        if self.env.context.get('active_model', False) == 'account.invoice':
            invoice = self.env["account.invoice"].browse(self.env.context['active_id'])
            if not invoice.number:
                return res

            xml_name = "cfd_" + invoice.number + ".xml"
            xml_id = self.env["ir.attachment"].search([('name', '=', xml_name)])
            if xml_id:
                res['value'].setdefault('attachment_ids', []).append(xml_id[0].id)

        return res


from openerp import api, models

class report_invoice_mx(models.AbstractModel):
    _name = 'report.cfd_mx.report_invoice_mx'
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        model_obj = self.env['ir.model.data']
        report = report_obj._get_report_from_name('cfd_mx.report_invoice_mx')
        docs = self.env[ report.model ].browse(self._ids)

        tipo_cambio = {}
        for invoice in docs:
            tipo_cambio[invoice.id] = 1.0
            if invoice.uuid:
                if invoice.currency_id.name=='MXN':
                    tipo_cambio[invoice.id] = 1.0
                else:
                    tipo_cambio[invoice.id] = model_obj.with_context(date=invoice.date_invoice).get_object('base', 'MXN').rate

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
            'tipo_cambio': tipo_cambio
        }
        return report_obj.render('cfd_mx.report_invoice_mx',  docargs)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: