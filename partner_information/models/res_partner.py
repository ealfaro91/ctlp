
from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    key = fields.Char(string='Key')
    first_name = fields.Char(string='First Name')
    second_name = fields.Char(string='Second Name')
    last_name = fields.Char(string='Last Name')
    middle_name = fields.Char(string='Middle Name')
    age = fields.Integer(string='Age')
    birth_date = fields.Date(string='Birth date')
    genre = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Genre')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')],
        string='Marital Status'
    )
    entry_date = fields.Date(string='Entry Date')
    exit_date = fields.Date(string='Exit Date')
    real_exit_date = fields.Date(string='Real Exit Date')
    origin_city_id = fields.Many2one(
        'res.city', string='Origin City',
        domain="[('state_id', '=', origin_state_id)]"
    )
    origin_state_id = fields.Many2one(
        'res.country.state', string='Origin State',
        domain="[('country_id', '=', origin_country_id)]"
    )
    origin_country_id = fields.Many2one('res.country', string='Origin Country')
    parent_familiar_name = fields.Char(string='Parent Name')
    parent_last_name = fields.Char(string='Parent Last Name')
    relation_id = fields.Many2one('res.partner.relation', string='Relation')
    parent_phone = fields.Char(string='Parent Phone')
    primary_axis_1 = fields.Char(string='Primary/Axis 1')
    preferred_substance_id =  fields.Many2one('preferred.substance', string='Preferred Substance')
    behavior_id = fields.Char(string='Behavior')
    psychiatric_dx = fields.Char(string='Psychiatric Dx')
    tp_axis_2 = fields.Char(string='TP/Axis 2')
    medical_report_axis_3 = fields.Char(string='Medical Report/Axis 3')
    eeg = fields.Char(string='EEG')
    registration = fields.Char(string='Registration')
    therapist_id = fields.Many2one('res.partner', string='Therapist')
    status_id = fields.Many2one('res.partner.status', string='Status')
    follow_up_date = fields.Date(string='Follow-up Date')
    comment = fields.Text(string='Comment')

    @api.onchange('entry_date', 'exit_date')
    def onchange_entry_date(self):
        if self.entry_date and self.exit_date:
            if self.entry_date > self.exit_date:
                self.exit_date = False
