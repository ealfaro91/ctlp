from odoo import models, fields, api, _
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
        'helpdesk.ticket.subcategory', string='Sub-Category',
        required=True, domain="[('category_id', '=', category_id)]"
    )
    location_id = fields.Many2one(
        'helpdesk.ticket.location', string='Location',
        domain="[('area_id', '=', area_id)]"
    )
    origen_id = fields.Many2one(
        'helpdesk.ticket.origen',
        string='Origen', domain="[('area_id', '=', area_id)]"
    )
    user_id = fields.Many2one('res.users', string='Assignee', related= 'category_id.user_id', store=True)
    has_origins = fields.Boolean(related='area_id.has_origins', store=True)
    has_locations = fields.Boolean(related='area_id.has_locations', store=True)


    @api.onchange('area_id')
    def _onchange_area_id(self):
        if self.area_id == self.ticket_id.area_id:
            raise ValidationError(_('The selected area is the same as the current area'))
        self.ticket_type_id = False
        self.category_id = False
        self.subcategory_id = False
        self.location_id = False
        self.origen_id = False

    @api.onchange('ticket_type_id')
    def _onchange_ticket_type_id(self):
        self.category_id = False
        self.subcategory_id = False

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.subcategory_id = False

    def change_area(self):
        self.sudo().ensure_one()
        self.sudo().ticket_id.write({
            'derived_from_area_id': self.ticket_id.area_id.id
        })
        self.sudo().ticket_id.write({
            'area_id': self.area_id.id,
            'team_id': self.env['helpdesk.ticket.team'].sudo().search([('area_id', '=', self.area_id.id)]).id,
            'type_id': self.ticket_type_id.id,
            'category_id': self.category_id.id,
            'subcategory_id': self.subcategory_id.id,
            'location_id': self.location_id.id,
            'origen_id': self.origen_id.id,
            'user_id': self.user_id.id,
        })
        self.env.cr.commit()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree',
            'domain': [('id', '!=', self.sudo().ticket_id.id)],
            'target': 'current',
            'name': 'Tickets'}


