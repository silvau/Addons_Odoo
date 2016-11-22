# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class partner(osv.Model):
    _inherit = "res.partner"
    
      
    _columns = {
        'revisar_version_dibujo': fields.boolean("Revisar Version Dibujo", help="Si está activo, el producto debe tener una version de dibujo capturada"),
        'revisar_fecha_autorizacion_dibujo': fields.boolean("Revisar Fecha de Autorizacion del Dibujo", help="Si está activo, el producto debe tener una fecha de autorizacion del dibujo capturada"),
        'revisar_version_especificacion': fields.boolean("Revisar Version de Especificacion", help="Si está activo, el producto debe tener una version de especificacion capturada"),
        'revisar_fecha_especificacion': fields.boolean("Revisar Fecha de Especificacion", help="Si está activo, el producto debe tener una fecha de especificacion capturada"),
    }
    
