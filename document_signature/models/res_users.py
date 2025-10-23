# -*- coding:  utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def init(self):
        # COLOCAMOS ESTO PORQUE LO EJECUTABA MASIVAMENTE PARA 7000 USUARIOS AL ACTUALIZAR"""
        # Evita regenerar contraseñas al actualizar módulos
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning("Saltando regeneración de contraseñas en res.users.init()")

        # No hacer nada (no llamar al super)
        return

    sign_signature = fields.Binary(string="Digital Signature", groups=False)
    sign_initials = fields.Binary(string="Digitial Initials", groups=False)
