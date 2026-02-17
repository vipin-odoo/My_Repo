import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DocumentDocument(models.Model):
    _inherit = "document.document"

    version_ids = fields.One2many(
        "document.document.version",
        "document_id",
        string="Versions",
        copy=False,
    )
    version_count = fields.Integer(compute="_compute_version_count")
    history_ids = fields.One2many(
        "document.document.annotation.history",
        "document_id",
        string="Annotation History",
        copy=False,
    )
    history_count = fields.Integer(compute="_compute_history_count")
    latest_version_id = fields.Many2one(
        "document.document.version",
        string="Latest Version",
        compute="_compute_latest_version",
        store=False,
    )
    is_pdf = fields.Boolean(compute="_compute_is_pdf", string="Is PDF")

    @api.depends("version_ids")
    def _compute_version_count(self):
        for record in self:
            record.version_count = len(record.version_ids)

    @api.depends("history_ids")
    def _compute_history_count(self):
        for record in self:
            record.history_count = len(record.history_ids)

    @api.depends("version_ids.version_number")
    def _compute_latest_version(self):
        for record in self:
            versions = record.version_ids.sorted("version_number", reverse=True)
            record.latest_version_id = versions[:1].id if versions else False

    @api.depends("file_name")
    def _compute_is_pdf(self):
        for record in self:
            record.is_pdf = bool(record.file_name and record.file_name.lower().endswith(".pdf"))

    def action_open_pdf_annotator(self):
        self.ensure_one()
        if not self.is_pdf:
            raise UserError(_("Annotation is supported only for PDF files."))

        return {
            "type": "ir.actions.client",
            "tag": "document_pdf_annotation.client_action",
            "name": _("Annotate PDF"),
            "params": {
                "document_id": self.id,
            },
        }

    def action_open_versions(self):
        self.ensure_one()
        return {
            "name": _("Versions"),
            "type": "ir.actions.act_window",
            "res_model": "document.document.version",
            "view_mode": "tree,form",
            "domain": [("document_id", "=", self.id)],
            "context": {"default_document_id": self.id},
        }

    def action_open_history(self):
        self.ensure_one()
        return {
            "name": _("Annotation History"),
            "type": "ir.actions.act_window",
            "res_model": "document.document.annotation.history",
            "view_mode": "tree,form",
            "domain": [("document_id", "=", self.id)],
            "context": {"default_document_id": self.id},
        }

    def _create_version_from_annotation_payload(self, annotation_payload, action_type="version_created"):
        self.ensure_one()
        if not self.is_pdf:
            raise UserError(_("Only PDF documents can be versioned through annotation."))

        annotation_payload = annotation_payload or {}
        next_version = (max(self.version_ids.mapped("version_number")) + 1) if self.version_ids else 1

        version_vals = {
            "document_id": self.id,
            "version_number": next_version,
            "file_data": self.file,
            "file_name": self.file_name,
            "annotation_data": json.dumps(annotation_payload),
            "created_by": self.env.user.id,
            "created_on": fields.Datetime.now(),
        }
        version = self.env["document.document.version"].create(version_vals)
        self._create_annotation_history_log(
            action_type=action_type,
            version=version,
            annotation_payload=annotation_payload,
        )
        return version

    def _create_annotation_history_log(self, action_type, version=False, annotation_payload=None):
        self.ensure_one()
        self.env["document.document.annotation.history"].create(
            {
                "document_id": self.id,
                "version_id": version.id if version else False,
                "user_id": self.env.user.id,
                "action_type": action_type,
                "action_timestamp": fields.Datetime.now(),
                "details": json.dumps(annotation_payload or {}),
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.is_pdf and r.file):
            record._create_version_from_annotation_payload(
                annotation_payload={"origin": "initial_upload"},
                action_type="version_created",
            )
        return records

    def write(self, vals):
        result = super().write(vals)
        if "file" in vals:
            for record in self.filtered(lambda r: r.is_pdf and r.file):
                record._create_version_from_annotation_payload(
                    annotation_payload={"origin": "file_update"},
                    action_type="version_created",
                )
        return result

    def get_pdf_binary_b64(self, version_id=False):
        self.ensure_one()
        if version_id:
            version = self.env["document.document.version"].browse(version_id).exists()
            if version and version.document_id == self:
                return version.file_data
        return self.file

    def save_annotation_version(self, annotation_payload):
        self.ensure_one()
        version = self._create_version_from_annotation_payload(
            annotation_payload=annotation_payload,
            action_type="version_created",
        )
        return {
            "version_id": version.id,
            "version_number": version.version_number,
        }
