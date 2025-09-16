{
    'name': 'Delivery Slip Email',
    'version': '17.0.1.0.0',
    'summary': 'Send delivery slip via email to delivery address',
    'description': """
        Adds a button to send delivery slip as email attachment to the delivery and external company.
    """,
    'author': 'Md. Shaheen Hossain',
    'website': 'https://eagle-erp.com',
    'category': 'Inventory/Delivery',
    'depends': ['stock', 'sale', 'mail', 'l10n_din5008_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'wizard/delivery_slip_email_wizard_views.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'delivery_slip_email/static/src/css/report.css',
    #     ],
    #     # Optional for backend styling:
    #     'web.assets_backend': [
    #         'delivery_slip_email/static/src/css/report.css',
    #     ],
    #     # Optional for PDF or QWeb reports:
    #     'web.report_assets_common': [
    #         'delivery_slip_email/static/src/css/report.css',
    #     ],
    # },


    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
