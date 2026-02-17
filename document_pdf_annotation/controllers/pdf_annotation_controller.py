import json

from odoo import http
from odoo.http import request


class PdfAnnotationController(http.Controller):

    def _build_pdf_file_url(self, document, selected_version):
        if selected_version:
            return f"/web/content/document.document.version/{selected_version.id}/file_data?download=false"
        return f"/web/content/document.document/{document.id}/file?download=false"

    @http.route("/document_pdf_annotation/load", type="json", auth="user")
    def load_document_annotation_context(self, document_id, version_id=None):
        document = request.env["document.document"].browse(document_id).exists()
        if not document:
            return {"error": "Document not found"}

        version = False
        if version_id:
            version = request.env["document.document.version"].browse(version_id).exists()
            if not version or version.document_id != document:
                version = False

        selected_version = version or document.latest_version_id
        annotation_payload = {}
        if selected_version and selected_version.annotation_data:
            try:
                annotation_payload = json.loads(selected_version.annotation_data)
            except json.JSONDecodeError:
                annotation_payload = {}

        return {
            "document_id": document.id,
            "document_name": document.display_name,
            "file_b64": document.get_pdf_binary_b64(version_id=selected_version.id if selected_version else False),
            "file_url": self._build_pdf_file_url(document, selected_version),
            "active_version_id": selected_version.id if selected_version else False,
            "active_version_number": selected_version.version_number if selected_version else 0,
            "annotation_payload": annotation_payload,
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "created_by": v.created_by.display_name,
                    "created_on": v.created_on,
                }
                for v in document.version_ids.sorted("version_number", reverse=True)
            ],
        }

    @http.route("/document_pdf_annotation/save", type="json", auth="user")
    def save_document_annotations(self, document_id, annotation_payload=None):
        document = request.env["document.document"].browse(document_id).exists()
        if not document:
            return {"error": "Document not found"}

        result = document.save_annotation_version(annotation_payload=annotation_payload or {})
        return {
            "ok": True,
            **result,
        }

    @http.route("/document_pdf_annotation/log_action", type="json", auth="user")
    def log_annotation_action(self, document_id, action_type, version_id=None, details=None):
        document = request.env["document.document"].browse(document_id).exists()
        if not document:
            return {"error": "Document not found"}

        version = request.env["document.document.version"].browse(version_id).exists() if version_id else False
        document._create_annotation_history_log(
            action_type=action_type,
            version=version,
            annotation_payload=details or {},
        )
        return {"ok": True}
