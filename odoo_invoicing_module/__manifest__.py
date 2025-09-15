# __manifest__.py
{
    'name': 'Invoice Product Attribute Wizard',
    'version': '18.0.1.0.0',
    'sequence': -1000,
    'summary': 'Opens a wizard to select product attributes/variants when adding products to invoices.',
    'description': """
This module adds a wizard in account.move.line (Invoices) to select product
attributes and variants when a product with variants is chosen, similar to
the Sale Order product configurator.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'price': 300.00,  # Example price
    'currency': 'USD', # Supported currencies are EUR and USD
    'category': 'Customizations',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'crm',
        'contacts',
    ],
    'data': [
        "security/security_group.xml",
        'security/ir.model.access.csv',
        'views/account_move_lines.xml',
        'views/crm_inherit.xml',
        'views/crm_label.xml',
        'views/crm_trademark_history.xml',
        'views/invoice_report_inherit.xml',
        # 'views/account_move_send_wizard_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_move_inherit/static/src/**/*.js',
            'account_move_inherit/static/src/**/*.xml',
            'account_move_inherit/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
