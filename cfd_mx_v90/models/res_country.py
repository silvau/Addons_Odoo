# -*- coding: utf-8 -*-

import pycountry
import os
import inspect
import csv

from openerp import api, fields, models, _


def get_import_datas_models(self, fname=""):
    current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    fname_model =  current_path+fname
    import_fields = []
    values = []
    with open(fname_model, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar="'")
        indx = 0
        for row in spamreader:
            if indx == 0:
                import_fields = row
            else:
                values.append(row)
            indx += 1
    res=self.load(import_fields, values)
    return True


class Pais(models.Model):
    _inherit = "res.country" 

    @api.one
    @api.depends('code')
    def _compute_code_alpha3(self):
        try:
            alpha3 = pycountry.countries.get(alpha2=self.code).alpha3
            self.code_alpha3 = alpha3
        except:
            pass

    code_alpha3 = fields.Char(string="Codigo (alpha3)", compute='_compute_code_alpha3')


class Ciudad(models.Model):
    _inherit = 'res.country.state.ciudad'
    
    state_id = fields.Many2one('res.country.state', 
        string='Estado', required=True)
    name = fields.Char(string='Name', size=256, required=True)

    @api.multi
    def get_import_datas_ciudad(self):
        fname = '/../data/res.country.state.ciudad.csv'
        get_import_datas_models(self, fname)
        return True


class Municipio(models.Model):
    _inherit = 'res.country.state.municipio'
    
    state_id = fields.Many2one('res.country.state', 
        string='State', required=True)
    ciudad_id = fields.Many2one('res.country.state.ciudad', string='City')
    name = fields.Char('Name', size=64, required=True)
    clave_sat = fields.Char("Clave SAT")

    @api.multi
    def get_import_datas_municipio(self):
        fname = '/../data/res.country.state.municipio.csv'
        get_import_datas_models(self, fname)
        return True

    @api.multi
    def get_load_datas_sat_municipio(self):
        fname = '/../data/c_Municipio.pdf.txt'
        current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        fname_model =  current_path+fname
        data = {}
        with open(fname_model) as f:
            for line in f:
                line = line.strip()
                if not line[0].isdigit():
                    continue
                values = line.split(" ")
                codigo = values[0]
                estado = values[1]
                nombre = " ".join(values[2:])
                data.setdefault(estado, []).append((codigo, nombre))

        import_fields = ['id', 'name', 'state_id.id', 'clave_sat']
        state_obj = self.env['res.country.state']
        for estado in data:
            faltan = [x[0] for x in data[estado]]
            nombres = {x:y for x,y in data[estado]}
            state_ids = state_obj.search( [('code', '=', estado), ('create_uid', '=', 1)] )
            for code, name in data[estado]:
                municipio_ids = self.search([
                    ('state_id', 'in', state_ids.ids), 
                    ('name', '=', name),
                    ('create_uid', '=', 1)
                ], order='name asc')
                if len(municipio_ids):
                    if code in faltan:
                        faltan.remove(code)
                    for m in municipio_ids:
                        vals = {
                            'clave_sat': code,
                        }
                        m.write(vals)
            values = []
            for code in faltan:
                nombre = nombres[code]
                val = ['municipio_sat_%s'%(code), nombre, state_ids.ids[0], code]
                values.append(val)
            res=self.load(import_fields, values)
        return True

class Colonia(models.Model):
    _inherit = 'res.country.state.municipio.colonia'
    
    municipio_id = fields.Many2one('res.country.state.municipio', 
        string='Municipio', required=True)
    name = fields.Char(string='Name', size=256, required=True)
    cp = fields.Char(string='Código Postal', size=10)

    @api.multi
    def get_import_datas_colonia(self):
        fname = '/../data/res.country.state.municipio.colonia.csv'
        get_import_datas_models(self, fname)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
