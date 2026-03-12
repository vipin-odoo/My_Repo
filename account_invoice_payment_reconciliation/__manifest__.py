{
    "name": "Invoice Payment Registration & Reconciliation",
    "summary": "Allow cash payment registration and invoice-side reconciliation actions.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_payment_register_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
