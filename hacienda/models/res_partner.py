# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    civil_status = fields.Selection(
        [
            ("Soltero", "Soltero"),
            ("Casado", "Casado"),
            ("No aplica", "No aplica")
        ],
        string="Estado Civil",
        required=True
    )
    spouse_name = fields.Char(
        string="Nombre del Cónyuge",
        index=True
    )
    matrimonial_regime = fields.Selection(
        [
            ("Separación de Bienes", "Separación de Bienes"),
            ("Sociedad Conyugal", "Sociedad Conyugal")
        ],
        string="Régimen Matrimonial"
    )
    outdoor_number = fields.Char(string="Número exterior")
    beneficiary = fields.Char(string="Beneficiario Controlador")
    curp = fields.Char(string="CURP")
    birthday = fields.Date(string="Fecha de nacimiento")
    identificacion = fields.Selection(
        [
            ("INE o IFE", "INE o IFE"),
            ("Pasaporte", "Pasaporte"),
            ("No aplica", "No aplica")
        ],
        string="Identificación Oficial Vigente",
        required=True
    )
    invoice_number = fields.Char(
        string="Número de folio de identificación",
        required=True
    )
    occupation_id = fields.Many2one(
        "partner.occupation",
        string="Ocupación"
    )
    is_location_customer = fields.Boolean(
        string="Es cliente"
    )


