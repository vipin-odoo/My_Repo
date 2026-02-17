{
    "name": "Document PDF Annotation & Versioning",
    "summary": "Annotate PDF files with versioning and user activity tracking.",
    "version": "18.0.1.0.0",
    "category": "Documents",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/document_document_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "document_pdf_annotation/static/src/js/pdf_annotation_client_action.js",
            "document_pdf_annotation/static/src/xml/pdf_annotation_templates.xml",
            "document_pdf_annotation/static/src/scss/pdf_annotation.scss",
        ],
    },
    "application": False,
    "installable": True,
}
