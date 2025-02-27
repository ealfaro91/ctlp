
from datetime import timedelta
from dateutil.relativedelta import relativedelta

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
    preferred_substance_id =  fields.Many2one('preferred.substance', string='Impact Substance')
    behavior_id = fields.Char(string='Impact Behavior')
    psychiatric_dx = fields.Char(string='Psychiatric Dx')
    tp_axis_2 = fields.Char(string='TP/Axis 2')
    medical_report_axis_3 = fields.Char(string='Medical Report/Axis 3')
    eeg = fields.Char(string='EEG')
    registration = fields.Char(string='Registration')
    therapist_id = fields.Many2one('res.partner', string='Therapist')
    status_id = fields.Many2one('res.partner.status', string='Status')
    follow_up_date = fields.Date(string='Follow-up Date')
    comment = fields.Text(string='Comment')
    blood_type = fields.Selection([
        ('A', 'A'), ('B', 'B'),
        ('AB', 'AB'), ('O', 'O')],
        string='Blood Type'
    )
    allergies = fields.Char(string='Allergies')
    hospital = fields.Char(string='Emergency Hospital')
    prognosticate = fields.Char(string='Prognosticate')
    right_to_care = fields.Selection([
        ('yes', 'Yes'), ('no', 'No'), ('at_3_months', 'at 3 Months')],
        string='Right continuous care'
    )

    weekly_activity_counter = fields.Integer(
        string='Weekly activity Counter',
        default=0,
        help="Tracks the number of weekly activities created for this partner."
    )
    biweekly_activity_counter = fields.Integer(
        string='Biweekly activity Counter',
        default=0,
        help="Tracks the number of biweekly activities created for this partner."
    )
    monthly_activity_counter = fields.Integer(
        string='Monthly activity Counter',
        default=0,
        help="Tracks the number of monthly activities created for this partner."
    )
    last_weekly_activity_id = fields.Many2one(
        'mail.activity', string='Last weekly activity',
        help="Last activity created for this partner."
    )
    last_biweekly_activity_id = fields.Many2one(
        'mail.activity', string='Last biweekly activity',
        help="Last activity created for this partner."
    )
    last_monthly_activity_id = fields.Many2one(
        'mail.activity', string='Last monthly activity',
        help="Last activity created for this partner."
    )
    partner_attachment_ids = fields.One2many(
        'partner.attachment', 'partner_id', string='Attachments'
    )
    second_partner_attachment_ids = fields.One2many(
        'partner.attachment', 'second_partner_id', string='Attachments'
    )

    def _cron_create_weekly_activities(self):
        """ Creates an activity weekly for 12 weeks"""
        today = fields.Date.today()
        partners = self.search([
            ('real_exit_date', '!=', False),
            ('weekly_activity_counter', '<', 12)
        ])

        for partner in partners:
            next_activity_date = partner.real_exit_date + timedelta(weeks=partner.weekly_activity_counter + 1)
            if today >= next_activity_date:
                partner.last_weekly_activity_id = self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                    'date_deadline': fields.Date.today(),
                    'user_id': self.user_id.id or self.env.user.id,  # Assign to the partner's user or the current user
                })
                partner.weekly_activity_counter += 1

    def _cron_create_biweekly_activities(self):
        """ Creates an activity biweekly for 12 weeks"""
        today = fields.Date.today()
        partners = self.search([
            ('real_exit_date', '!=', False),
            ('biweekly_activity_counter', '<', 12)
        ])

        for partner in partners:
            next_activity_date = partner.real_exit_date + timedelta(weeks=(partner.biweekly_activity_counter + 1) * 2)
            if today >= next_activity_date:
                partner.last_biweekly_activity_id = self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                    'date_deadline': fields.Date.today(),
                    'user_id': self.user_id.id or self.env.user.id,  # Assign to the partner's user or the current user
                })
                partner.biweekly_activity_counter += 1

    def _cron_create_monthly_activities(self):
        """ Creates an activity monthly for 24 weeks"""
        today = fields.Date.today()
        partners = self.search([
            ('real_exit_date', '!=', False),
            ('monthly_activity_counter', '<', 24)
        ])

        for partner in partners:
            next_activity_date = partner.real_exit_date + relativedelta(months=(partner.monthly_activity_counter + 1))
            if today >= next_activity_date:
                partner.last_monthly_activity_id = self.env['mail.activity'].create({
                    'res_model_id': self.env['ir.model']._get('res.partner').id,
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                    'date_deadline': fields.Date.today(),
                    'user_id': self.user_id.id or self.env.user.id,  # Assign to the partner's user or the current user
                })
                partner.monthly_activity_counter += 1

    def _cron_create_birthday_annual_activities(self):
        """ Creates an activity for each partner's birthday or real exit date."""
        partners = self.env['res.partner'].search([('real_exit_date', '!=', False)])
        today = fields.Date.today()

        for partner in partners:
            if partner.birth_date:
                if partner.birth_date.month == today.month and partner.birth_date.day == today.day:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'res_id': partner.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                        'date_deadline': today,
                        'user_id': partner.user_id.id or self.env.user.id,  # Assign to the partner's user or the current user
                    })
                if partner.real_exit_date.month == today.month and partner.real_exit_date.day == today.day:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'res_id': partner.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                        'date_deadline': today,
                        'user_id': partner.user_id.id or self.env.user.id,})  # Assign to the partner's user or the current user


    @api.onchange('entry_date', 'exit_date')
    def onchange_entry_date(self):
        if self.entry_date and self.exit_date:
            if self.entry_date > self.exit_date:
                self.exit_date = False

    @api.model
    def _cron_create_activities(self):
        for partner in partners:
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get('res.partner').id,
                'res_id': partner.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  # Default to "To Do"
                'date_deadline': today,
                'user_id': partner.user_id.id or self.env.user.id,  # Assign to the partner's user or the current user
            })
