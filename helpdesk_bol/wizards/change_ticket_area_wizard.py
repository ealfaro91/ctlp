from odoo import models, fields, api

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

    def change_area(self):
        self.ensure_one()
        self.ticket_id.write({
            'area_id': self.area_id.id,
            'type_id': self.ticket_type_id.id,
            'category_id': self.category_id.id,
            'subcategory_id': self.subcategory_id.id,
            'location_id': self.location_id.id,
            'user_id': self.user_id.id,
        })
        self.ticket_id.area_id = self.area_id.id
        return {'type': 'ir.actions.act_window_close'}
