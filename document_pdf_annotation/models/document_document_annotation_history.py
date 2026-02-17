from odoo import fields, models


class DocumentDocumentAnnotationHistory(models.Model):
    _name = "document.document.annotation.history"
    _description = "Document Annotation History"
    _order = "action_timestamp desc, id desc"

    document_id = fields.Many2one("document.document", required=True, ondelete="cascade", index=True)
    version_id = fields.Many2one("document.document.version", ondelete="set null", index=True)
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    action_type = fields.Selection(
        selection=[
            ("annotation_added", "Annotation Added"),
            ("annotation_updated", "Annotation Updated"),
            ("annotation_deleted", "Annotation Deleted"),
            ("version_created", "New Version Created"),
        ],
        required=True,
        default="annotation_added",
    )
    action_timestamp = fields.Datetime(required=True, default=fields.Datetime.now)
    details = fields.Text(string="Raw Details JSON")
