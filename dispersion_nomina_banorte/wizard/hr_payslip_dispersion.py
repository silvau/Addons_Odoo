# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import pdb
import time
import base64
from openerp.osv import osv, fields
from dateutil import parser
from openerp.tools.translate import _

class hr_payslip_dispersion_banorte(osv.osv_memory):
    _name = 'hr.payslip_dispersion_banorte'
    _description = 'HR Payslip Dispersion Banorte'

    _columns = {
        'payslip_run': fields.many2many('hr.payslip.run', 'hr_banorte_rel'),
        'fecha_proceso': fields.date(),
        'txt_binary': fields.binary("File TXT"),
        'txt_filename': fields.char("Filename"),
        'consecutivo': fields.integer("Consecutivo", size=2),
    }
    _defaults = {
        'fecha_proceso' : fields.date.context_today,
        'consecutivo' : 1,
    }


    def generate_file(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        """
        function called from button
        """
        payslip_obj = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        users_obj = self.pool.get('res.users')
        user_rec = users_obj.browse(cr,uid,uid,context=None)
        my_date = parser.parse(this.fecha_proceso)
        proper_date_string = my_date.strftime('%Y%m%d')
        proper_consecutivo = str(this.consecutivo)
        if this.consecutivo < 10 :
            proper_consecutivo="0"+str(this.consecutivo)
        
        content = ""
        num_regs = 0
        amount_regs = 0.0
        for nomina  in this.payslip_run:
            payslip_ids=payslip_obj.search(cr,uid,[('payslip_run_id','=',nomina.id)])
            payslip_regs = payslip_obj.browse(cr,uid,payslip_ids,context=None)                
            for reg in payslip_regs:
                payslip_line_ids = payslip_line_obj.search(cr,uid,[('slip_id','=',reg.id),('code','ilike','_TOTAL')])
                payslip_lines = payslip_line_obj.browse(cr,uid,payslip_line_ids,context=None) 
                for payslip_line in payslip_lines:
                    linea="D"+proper_date_string
                    codigo_emp =(str)(payslip_line.employee_id.cod_emp)
                    if len(codigo_emp) > 11 :
                        codigo_emp=codigo_emp[:10]
                    if len(codigo_emp) < 10:
                        codigo_emp="0"*(10-len(codigo_emp))+codigo_emp

                    linea=linea+codigo_emp
                    linea=linea+" "*40+" "*40
                    cantidad=payslip_line.amount
                    partes=(str)(cantidad).split('.')
                    parte_decimal=partes[1][:2]
                    parte_entera=partes[0]
                    if len(parte_entera) > 13 :
                        parte_entera=parte_entera[:13]
                    if len(parte_entera) < 13:
                        parte_entera="0"*(13-len(parte_entera))+parte_entera
                    
                    linea=linea+parte_entera+parte_decimal
                    num_bank_rec=payslip_line.employee_id.bank_account_id.bank_bic
                   
                    if (not num_bank_rec) or len((str)(num_bank_rec))!= 3 :
                        raise osv.except_osv(_("Error!"), _("El empleado "+payslip_line.employee_id.name + u" no tiene asignado un número de banco receptor válido"
                                             )) 
                    num_bank_rec_str=(str)(num_bank_rec)
                    linea=linea+num_bank_rec_str
                    linea=linea+(str)(payslip_line.employee_id.tipo_cuenta)
                    
                    num_cta=(str)(payslip_line.employee_id.bank_account_id.acc_number)
                    if (len(num_cta) > 18) or (num_cta == "None") or (len(num_cta) < 9):
                        raise osv.except_osv(_("Error!"), _("El empleado "+payslip_line.employee_id.name + u" no tiene asignado un número de cuenta válido"
                          ))
                    if len(num_cta) < 18 :
                        num_cta="0"*(18-len(num_cta))+num_cta
                    linea=linea+num_cta
                    linea=linea+"0"+" "+"0"*8+" "*18
                    content=content+"\n"+linea
                    num_regs+=1
                    amount_regs+=cantidad
        
        num_regs_str=(str)(num_regs)
        if len(num_regs_str) < 6 :
            num_regs_str="0"*(6-len(num_regs_str))+num_regs_str
        partes=(str)(amount_regs).split('.')
        parte_decimal=partes[1][:2]
        parte_entera=partes[0]
        if len(parte_entera) > 13 :
            parte_entera=parte_entera[:13]
        if len(parte_entera) < 13:
            parte_entera="0"*(13-len(parte_entera))+parte_entera
 
        cabecera = "HNE"+str(user_rec.company_id.emisora)+proper_date_string+str(proper_consecutivo)+num_regs_str+parte_entera+parte_decimal+"0"*6+"0"*15+"0"*6+"0"*15+"0"*6+"0"+" "*77
        content=cabecera+content
        fname="NI"+str(user_rec.company_id.cod_serv)+proper_consecutivo+".PAG"
        self.write(cr, uid, this.id, {
            'txt_filename': fname,
            'txt_binary': base64.encodestring(content)
        }, context=context)
        return self._return_action(cr, uid, this.id, context=context)
    

    def _return_action(self, cr, uid, id, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'dispersion_nomina_banorte', 'view_hr_payslip_dispersion_banorte')
        view_id = view_rec and view_rec[1] or False
        return {
           'res_id': id,
           'view_type': 'form',
           'view_id' : [view_id],
           'view_mode': 'form',
           'res_model': 'hr.payslip_dispersion_banorte',
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context
        }

    def onchange_consecutivo(self, cr, uid, ids, field_value, context=None):
        if context is None:
            context = {}
        res = {'value': {}}
        if (not field_value) or (field_value < 0) or (field_value > 99):
            res['value'].update({'consecutivo': 1})
        return res




hr_payslip_dispersion_banorte()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

