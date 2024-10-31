# -*- coding: utf-8 -*-

import base64
from datetime import date
from lxml import etree

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    name_xml = fields.Char(
        string="nombre_xml",
        compute="button_crear_xml"
    )
    xml_file = fields.Binary(string="xml")
    affiliation_entity = fields.Char(string="Entidad-Adscripción")
    statement_date = fields.Date(string="Fecha de escritura")
    notary_name = fields.Char(string="Nombre de notario")
    statement_number = fields.Char(string="Número de escritura")
    contract_date = fields.Date(string="Fecha de contrato")
    notary_number = fields.Selection(
        [("etiqueta", "Etiqueta")],
        string="Número de notaria",
        requirement=True
    )
    appraised_value = fields.Monetary(
        string="Valor avalúo. Catastral o fiscal"
    )
    priority = fields.Selection(
        [
            ("1", "Normal"),
            ("2", "24 Horas con Operaciones")
        ],
        string="Pioridad"
    )
    alert_type_id = fields.Many2one(
        "alert.type",
        string="Tipo de Alerta"
    )

    def button_generate_xml(self):
        self.name_xml = "PruebaSAT.xml"
        archivo = etree.Element("archivo")
        informe = etree.SubElement(archivo, "informe")
        mes_reportado = etree.SubElement(informe, "mes_reportado")
        mes_reportado.text = "{}{}".format(date.today().year, date.today().month)
        sujeto_obligado = etree.SubElement(informe, "sujeto_obligado")
        clave_sujeto_obligado = etree.SubElement(sujeto_obligado, "clave_sujeto_obligado")
        clave_sujeto_obligado.text = self.partner_id.vat or ""
        clave_actividad = etree.SubElement(sujeto_obligado, "clave_actividad")
        clave_actividad.text = self.partner_id.occupation_id.code or ""
        aviso = etree.SubElement(informe, "aviso")
        referencia_aviso = etree.SubElement(aviso, "referencia_aviso")
        referencia_aviso.text = self.name or ""
        prioridad = etree.SubElement(aviso, "prioridad")
        prioridad.text = self.priority or ""
        alerta = etree.SubElement(aviso, "alerta")
        tipo_alerta = etree.SubElement(alerta, "tipo_alerta")
        tipo_alerta.text = self.alert_type_id.code or ""
        persona_aviso = etree.SubElement(aviso, "persona_aviso")
        tipo_persona = etree.SubElement(persona_aviso, "tipo_persona")
        persona_fisica = etree.SubElement(tipo_persona, "persona_fisica")
        nombre = etree.SubElement(persona_fisica, "nombre")
        nombre.text = self.partner_id.name or ""

        apellido_paterno = etree.SubElement(persona_fisica, "apellido_paterno")
        apellido_materno = etree.SubElement(persona_fisica, "apellido_materno")
        fecha_nacimiento = etree.SubElement(persona_fisica, "fecha_nacimiento")
        if self.partner_id.birthday:
            fecha_nacimiento.text = "{}{}{}".format(
                self.partner_id.birthday.year,
                self.partner_id.birthday.month,
                self.partner_id.birthday.day
            )
        else:
            fecha_nacimiento.text = ""
        rfc = etree.SubElement(persona_fisica, "rfc")
        rfc.text = self.partner_id.rfc or ""
        curp = etree.SubElement(persona_fisica, "curp")
        curp.text = self.partner_id.curp or ""
        pais_nacionalidad = etree.SubElement(persona_fisica, "pais_nacionalidad")
        actividad_economica = etree.SubElement(persona_fisica, "actividad_economica")
        actividad_economica.text = self.partner_id.occupation_id.code or ""

        tipo_domicilio = etree.SubElement(persona_aviso, "tipo_domicilio")
        nacional = etree.SubElement(tipo_domicilio, "nacional")
        colonia = etree.SubElement(nacional, "colonia")
        colonia.text = self.partner_id.street2 or ""
        calle = etree.SubElement(nacional, "calle")
        calle.text = self.partner_id.street or ""

        numero_exterior = etree.SubElement(nacional, "numero_exterior")
        numero_exterior.text = self.partner_id.outdoor_number or ""
        codigo_postal = etree.SubElement(nacional, "codigo_postal")
        codigo_postal = self.partner_id.zip or ""

        detalle_operaciones = etree.SubElement(aviso, "detalle_operaciones")
        datos_operacion = etree.SubElement(detalle_operaciones, "datos_operacion")
        fecha_operacion = etree.SubElement(datos_operacion, "fecha_operacion")
        fecha_operacion.text = "{}{}{}".format(
            self.invoice_date.year,
            self.invoice_date.month,
            self.invoice_date.day
        )
        tipo_operacion = etree.SubElement(datos_operacion, "tipo_operacion")
        figura_cliente = etree.SubElement(datos_operacion, "figura_cliente")
        figura_so = etree.SubElement(datos_operacion, "figura_so")
        caracteristicas_inmueble = etree.SubElement(datos_operacion, "caracteristicas_inmueble")
        tipo_inmueble = etree.SubElement(caracteristicas_inmueble, "tipo_inmueble")
        valor_pactado = etree.SubElement(caracteristicas_inmueble, "valor_pactado")
        colonia = etree.SubElement(caracteristicas_inmueble, "colonia")
        colonia.text = self.invoice_line_ids[0].product_id.colonia or ""
        calle = etree.SubElement(caracteristicas_inmueble, "calle")
        calle.text = self.invoice_line_ids[0].product_id.street or ""
        numero_exterior = etree.SubElement(caracteristicas_inmueble, "numero_exterior")
        codigo_postal = etree.SubElement(caracteristicas_inmueble, "codigo_postal")
        codigo_postal.text = self.invoice_line_ids[0].product_id.postal_code or ""
        dimension_terreno = etree.SubElement(caracteristicas_inmueble, "dimension_terreno")
        dimension_terreno = self.invoice_line_ids[0].product_id.m2 or ""
        dimension_construido = etree.SubElement(caracteristicas_inmueble, "dimension_construido")
        dimension_construido = self.invoice_line_ids[0].product_id.mc or ""
        folio_real = etree.SubElement(caracteristicas_inmueble, "folio_real")
        folio_real = self.invoice_origin or ""
        contrato_instrumento_publico = etree.SubElement(datos_operacion, "contrato_instrumento_publico")
        datos_contrato = etree.SubElement(contrato_instrumento_publico, "datos_contrato")
        fecha_contrato = etree.SubElement(datos_contrato, "fecha_contrato")
        fecha_contrato.text = str(self.contract_date) or ""
        datos_liquidacion = etree.SubElement(datos_operacion, "datos_liquidacion")
        fecha_pago = etree.SubElement(datos_liquidacion, "fecha_pago")
        forma_pago = etree.SubElement(datos_liquidacion, "forma_pago")
        forma_pago.text = self.forma_pago or ""
        instrumento_monetario = etree.SubElement(datos_liquidacion, "instrumento_monetario")
        moneda = etree.SubElement(instrumento_monetario, "moneda")
        moneda.text = ""
        monto_operacion = etree.SubElement(instrumento_monetario, "monto_operacion")
        #monto_operacion.text = self.amount_untaxed
        xml = etree.ElementTree(archivo)
        self.xml_file = base64.b64encode(
            etree.tostring(
                xml,
                encoding="UTF-8",
                xml_declaration=True,
                method="xml",
                pretty_print=True)
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content?model=%s&download=True&field=xml_file&id=%s&filename=%s"
                   % (self._inherit, self.id, self.name_xml),
            "target": "new",
        }