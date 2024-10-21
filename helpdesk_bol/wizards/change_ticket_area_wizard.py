from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ChangeTicketAreaWizard(models.TransientModel):
    _name = 'change.ticket.area.wizard'
    _description = 'Wizard to Change Ticket Area'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True)
    area_id = fields.Many2one('helpdesk.ticket.area', string='New Area', required=True)
    code = fields.Char(string='Code', store=True, related='area_id.code')
    ticket_type_id = fields.Many2one(
        'helpdesk.ticket.type', string='Ticket Type',
        required=True, domain="[('area_id', '=', area_id)]"
    )
    category_id = fields.Many2one(
        'helpdesk.ticket.category', string='Category',
        required=True, domain="[('type_id', '=', ticket_type_id)]"
    )
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory', string='Sub-category',
        required=True, domain="[('category_id', '=', category_id)]"
    )
    location_id = fields.Many2one(
        'helpdesk.ticket.location', string='Location',
        domain="[('category_id', '=', category_id)]"
    )
    user_id = fields.Many2one('res.users', string='Assignee', related= 'category_id.user_id', store=True)

    @api.onchange('area_id')
    def _onchange_area_id(self):
        if self.area_id == self.ticket_id.area_id:
            raise ValidationError('The selected area is the same as the current area')
        self.ticket_type_id = False
        self.category_id = False
        self.subcategory_id = False
        self.location_id = False

    @api.onchange('ticket_type_id')
    def _onchange_ticket_type_id(self):
        self.category_id = False
        self.subcategory_id = False
        self.location_id = False

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.subcategory_id = False
        self.location_id = False

    def change_area(self):
        self.ensure_one()
        message = {
            'title': "Changed area",
            'message': "The ticket area has been changed from  %s to %s." % (
            self.ticket_id.area_id.name, self.area_id.name),
            'type': 'success',
            'sticky': False,
        }
        self.ticket_id.write({
            'area_id': self.area_id.id,
            'team_id': self.env['helpdesk.ticket.team'].search([('area_id', '=', self.area_id.id)]).id,
            'type_id': self.ticket_type_id.id,
            'category_id': self.category_id.id,
            'subcategory_id': self.subcategory_id.id,
            'location_id': self.location_id.id,
            'user_id': self.user_id.id,
        })
        self.env.user.notify_info(message['message'], title=message['title'], sticky=message['sticky'])
        return {'type': 'ir.actions.act_window_close'}
