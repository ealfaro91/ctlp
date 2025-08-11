
from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    # document_file_type_id = fields.Many2one(
    #     comodel_name="document.file.type",
    #     string="Document File Type",
    #     help="The type of the document file, used to categorize and manage different file types.",
    #     tracking=True
    # )


class DocumentFileType(models.Model):
    _name = "document.file.type"
    _description = "Document File Type"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]
    _order = "create_date desc"

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


class DocumentVersion(models.Model):
    _name = 'document.version'
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]


    version = fields.Integer(
          string='Version Number', default=0, readonly=True, copy=False)
    # deactivate_date = fields.Date(string='Deactivated date', readonly=True)
    # parent_test = fields.Many2one(
    #       comodel_name='qc.test', string='Parent Test', copy=False)
    # old_versions = fields.One2many(
    #         comodel_name='qc.test', string='Old Versions',
    #         inverse_name='parent_test', context={'active_test': False})
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
