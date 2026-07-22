# -*- coding: utf-8 -*-
{
    'name': 'Sale Menu Restructure',
    'version': '19.0.1.1.0',
    'category': 'Sales/Sales',
    'summary': 'Reestructura menús de Ventas: Quotes y Sales Orders como raíz, oculta Productos y Reportes a no-admin',
    'description': """
        - Separa Cotizaciones (Quotes) y Órdenes de Venta (Sales Orders) como menús raíz
        - Quotes muestra solo cotizaciones (draft/sent)
        - Sales Orders muestra solo órdenes confirmadas (sale/done)
        - Al confirmar una cotización, redirige automáticamente a Sales Orders
        - Oculta Productos y Reportes para usuarios no administradores
    """,
    'author': 'Alphaqueb Consulting',
    'website': 'https://alphaqueb.com',
    'depends': ['sale'],
    'data': [
        'security/sale_menu_groups.xml',
        'views/sale_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_menu_restructure/static/src/js/sales_root_menu_patch.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
