
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
    has_subcategories = fields.Boolean(
        string='Has Subcategories',
        default=False,
        help="Indicates whether this document file type has subcategories.",
        tracking=True
    )
    is_parent_type = fields.Boolean(
        string='Is Parent Type',
        default=True,
        help="Indicates whether this document file type is a parent type.",
        tracking=True
    )

    parent_type_id = fields.Many2one(
        'document.file.type',
        string='Parent Type',
        ondelete='set null',
        help="The parent type of this document file type.",
        tracking=True,
        index=True,
        domain=[('parent_type_id', '=', False)]
    )
    child_type_ids = fields.One2many(
        'document.file.type',
        'parent_type_id',
        string='Child Types',
        help="The child types of this document file type.",
        tracking=True,
        index=True,
        copy=False
    )

    @api.onchange('parent_type_id')
    def _onchange_parent_type_id(self):
        for rec in self:
            if rec.parent_type_id:
                rec.is_parent_type = False

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
