{
    "name": "Universal API Key Access",
    "version": "18.0.1.0.0",
    "summary": "Generate API keys by user_id/login and read any model records via key",
    "description": """
Expose JSON APIs to generate API keys and fetch model records (including one2many values).
""",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False,
}
