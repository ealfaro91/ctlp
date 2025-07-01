
from odoo import models, fields


class PartnerAttachment(models.Model):
    _name = 'partner.attachment'
    _description = 'Partner Attachment'

    partner_id = fields.Many2one('res.partner', string='Partner')
    second_partner_id = fields.Many2one('res.partner', string='Partner')
    attachment = fields.Binary(string='Attachment', required=True)
    attachment_name = fields.Char(string='Attachment Name')
