# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Zenpar - http://www.zeval.com.mx/
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
import suds
import xml.etree.ElementTree as ET
import base64
import urllib2
import os
from soap_hacienda import ConsultaCFDI
import re
from datetime import datetime

class subir_xml(osv.TransientModel):
    _name = "import_factura.subir"

   
    def _validar_en_hacienda(self, cr, uid, xml, context=None):
        try:
            root = ET.fromstring(xml)
        except:
            raise osv.except_osv("Error", "El archivo XML parece estar mal formado")
        total = emisor = receptor = uuid = False
        total = float(root.attrib.get("total", False))
        for child in root:
            if child.tag.endswith("Emisor"):
                emisor = child.attrib["rfc"]
            elif child.tag.endswith("Receptor"):
                receptor = child.attrib["rfc"]
                #receptor_nombre = child.attrib["nombre"]
            elif child.tag.endswith("Complemento"):
                for child2 in child:
                    if child2.tag.endswith("TimbreFiscalDigital"):
                        uuid = child2.attrib["UUID"]
        if not all([total, emisor, receptor, uuid]):
            raise osv.except_osv("Error", "El archivo XML no parece ser un CFDI")
  
        user_company = self.pool.get("res.users").browse(cr, uid, uid).company_id
        #if user_company.partner_id.vat != emisor:
        #    raise osv.except_osv("Error", u"El comprobante no es de la compañía")  
        integer, decimal = str(total).split('.')
        padded_total = integer.rjust(10, '0') + '.' + decimal.ljust(6, '0')
        data = '?re=%s&rr=%s&tt=%s&id=%s'%(emisor, receptor, padded_total, uuid)

        #Checar si hay internet
        import socket
        try:
            response=urllib2.urlopen('http://google.com',timeout=2)
        except urllib2.URLError:
            raise osv.except_osv("Error", "Parece que no hay conexion a internet")            
        except socket.timeout:
            raise osv.except_osv("Error", "Parece que no hay conexion a internet")
        
        #Esto manda llamar el webserive usando suds (manda error en algunas plataformas)
        #---------------
        #wsdl = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl"
        #client = suds.client.Client(wsdl)
        #resp = client.service.Consulta(data)
        #return uuid, resp
        
        #Esto usa el server de zeval
        #----------------
        #resp = urllib2.urlopen("http://zeval.com.mx/cgi-bin/valida_cfdi.py" + data).read().split("\n")
        #return uuid, resp[0], resp[1]
        
        #Esto manda el soap directamente con pycurl (ver soap_hacienda.py)
        #----------------
        resp = ConsultaCFDI(data)
        print "USANDO SOAP"
        m = re.search("CodigoEstatus>(.*?)</a:CodigoEstatus><a:Estado>(.*?)</a:Estado>", resp)
        if not m:
            raise osv.except_osv("Error", "Hubo un error al consultar hacienda")
        return uuid, m.group(1), m.group(2)

      
       

