{
    "name": "Documents PDF Annotation & Versioning",
    "summary": "Annotate PDFs in Documents with versioning and audit history",
    "version": "18.0.1.0.0",
    "author": "Custom",
    "license": "LGPL-3",
    "website": "https://example.com",
    "category": "Productivity/Documents",
    "depends": ["documents", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/documents_document_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pdf_document_annotator/static/src/scss/pdf_annotator.scss",
            "pdf_document_annotator/static/src/xml/pdf_annotator_templates.xml",
            "pdf_document_annotator/static/src/js/pdf_annotator_action.js",
        ],
    },
    "application": False,
    "installable": True,
}
