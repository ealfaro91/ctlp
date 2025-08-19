
from odoo import models, fields, api


class DocumentFileType(models.Model):
    _name = "document.file.type"
    _description = "Document File Type"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]
    _order = "create_date desc"

    active = fields.Boolean(
        string='Active',
        default=True,
        help="Indicates whether the document file type is active or not."
    )
    name = fields.Char(
        string="File Type",
        required=True,
        tracking=True,
        translate=True,
        help="The name of the document file type."
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="The sequence used to order the file types.",
    )




class DocumentDirectory(models.Model):
    _inherit = 'document.directory'

    area_id = fields.Many2one(
        comodel_name='helpdesk.ticket.area',
        string='Area',
        help="The area associated with the document directory, used for categorization and management.",
        tracking=True
    )
 #   document_file_type_ids = fields.Many2one(

    # unrevisioned_name = fields.Char(
    #         string='Test Name', copy=True, readonly=True)
        #
        #
        # def create(self, values):
        #     if 'unrevisioned_name' not in values:
        #         values['unrevisioned_name'] = values['name']
        #     return super(QcTest, self).create(values)
        #
        # @api.multi
        # def write(self, values):
        #     for test in self:
        #         if 'name' in values and not values.get('version', test.version):
        #             values['unrevisioned_name'] = values['name']
        #         return super(QcTest, test).write(values)
        #
        # def _copy_test(self):
        #     new_test = self.copy({
        #         'version': self.version,
        #         'active': False,
        #         'deactivate_date': fields.Date.today(),
        #         'parent_test': self.id,
        #     })
        #     return new_test
        #
        # @api.multi
        # def button_new_version(self):
        #     self.ensure_one()
        #     self._copy_test()
        #     revno = self.version
        #     self.write({
        #         'version': revno + 1,
        #         'name': '%s-%02d' % (self.unrevisioned_name, revno + 1)
        #     })
        #
        # @api.multi
        # def action_open_older_versions(self):
        #     result = self.env.ref('quality_control.action_qc_test').read()[0]
        #     result['domain'] = [('id', 'in', self.old_versions.ids)]
        #     result['context'] = {'active_test': False}
        #     return result
