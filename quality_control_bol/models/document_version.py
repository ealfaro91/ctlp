from odoo import models, fields, api, _


class DocumentVersion(models.Model):
    _name = "document.version"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]
    _description = "Document Version"

    @api.depends("attachment_id", "version")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.attachment_id.name} - (Version {record.version})"

    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        readonly=True
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Indicates whether the document version is active or not."
    )
    version = fields.Integer(
        string="Version Number",
        default=0,
        copy=False
    )
    deactivate_date = fields.Date(
        string="Deactivated date",
        readonly=True
    )
    parent_version_id = fields.Many2one(
        "document.version",
        string="Parent Version",
        copy=False
    )
    old_versions = fields.One2many(
        "document.version",
        "parent_version_id",
        string="Old Versions",
        context={"active_test": False}
    )
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Attachment",
        help="The attachment related to this document version.",
        tracking=True,
        required=True
    )
