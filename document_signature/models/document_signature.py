# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
import pytz


class DocumentSignature(models.Model):
    _name = 'document.signature'

    POSITION_SELECTION =

    position = fields.Selection([
        ('top', 'Arriba'),
        ('footer', 'Pie de página'),
    ], string='Posición de la firma', default='bottom')
    # Otros campos como firma, usuario, estado, etc.
