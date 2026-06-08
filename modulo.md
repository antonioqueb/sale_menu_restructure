## ./__init__.py
```py
# -*- coding: utf-8 -*-
from . import models
```

## ./__manifest__.py
```py
# -*- coding: utf-8 -*-
{
    'name': 'Sale Menu Restructure',
    'version': '19.0.1.0.0',
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
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

## ./models/__init__.py
```py
# -*- coding: utf-8 -*-
from . import sale_order
```

## ./models/sale_order.py
```py
# -*- coding: utf-8 -*-
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Si la orden se crea desde el menú "Sales Orders" (bandera de contexto
        'create_confirmed_order'), nace ya confirmada: se ejecuta la lógica
        completa de confirmación (action_confirm), sin pasar por cotización.
        """
        orders = super().create(vals_list)

        if self.env.context.get('create_confirmed_order'):
            for order in orders:
                # Solo confirmamos órdenes en borrador y con líneas, para evitar
                # confirmar borradores vacíos accidentalmente.
                if order.state == 'draft' and order.order_line:
                    order.with_context(skip_sale_order_redirect=True).action_confirm()

        return orders

    def action_confirm(self):
        """
        Override para redirigir al usuario a la vista de Sales Orders
        después de confirmar una cotización.
        """
        res = super().action_confirm()

        # Cuando la confirmación ocurre durante la creación de la orden
        # (orden que nace confirmada), no redirigimos: el resultado se ignora.
        if self.env.context.get('skip_sale_order_redirect'):
            return res

        # Si la confirmación fue exitosa y estamos en la UI (no en batch/cron),
        # redirigimos al formulario de la orden dentro del menú Sales Orders
        if self and len(self) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.id,
                'view_mode': 'form',
                'views': [(False, 'form')],
                'target': 'current',
                'context': dict(self.env.context),
            }

        return res
```

## ./security/sale_menu_groups.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Products: solo visible para administradores de ventas -->
    <menuitem id="sale.product_menu_catalog"
              parent="sale.sale_menu_root"
              groups="sales_team.group_sale_manager"/>

    <!-- Reporting: menú original solo visible para administradores de ventas -->
    <menuitem id="sale.menu_sale_report"
              parent="sale.sale_menu_root"
              groups="sales_team.group_sale_manager"/>

    <!-- Menú de Reportes para usuarios básicos -->
    <menuitem id="menu_sale_report_user"
              name="Reporting"
              parent="sale.sale_menu_root"
              sequence="90"
              groups="sales_team.group_sale_salesman"/>

    <!-- Estado de Cuenta dentro del menú de reportes para usuarios básicos -->
    <menuitem id="menu_account_statement_user"
              name="Estado de Cuenta"
              parent="menu_sale_report_user"
              action="account_statement_report.action_account_statement_wizard"
              sequence="1"
              groups="sales_team.group_sale_salesman"/>

    <!-- Customers en menú principal de Ventas -->
    <record id="action_sale_customers" model="ir.actions.act_window">
        <field name="name">Clientes</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">list,kanban,form,activity</field>
        <field name="domain">[('customer_rank', '&gt;', 0)]</field>
        <field name="context">{'default_customer_rank': 1}</field>
    </record>

    <menuitem id="menu_sale_customers_root"
              name="Customers"
              parent="sale.sale_menu_root"
              action="action_sale_customers"
              sequence="15"/>

</odoo>```

## ./views/sale_menu_views.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Desactivar menú "Orders" original -->
    <record id="sale.sale_order_menu" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>

    <!-- Acción: Quotes (solo draft y sent) -->
    <record id="action_quotations_only" model="ir.actions.act_window">
        <field name="name">Quotes</field>
        <field name="res_model">sale.order</field>
        <field name="view_mode">list,kanban,form,calendar,pivot,graph,activity</field>
        <field name="domain">[('state', 'in', ('draft', 'sent'))]</field>
        <field name="context">{'default_state': 'draft'}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create a new quotation, the first step of a new sale!
            </p>
        </field>
    </record>

    <!-- Acción: Sales Orders (solo sale y done) -->
    <record id="action_sales_orders_only" model="ir.actions.act_window">
        <field name="name">Sales Orders</field>
        <field name="res_model">sale.order</field>
        <field name="view_mode">list,kanban,form,calendar,pivot,graph,activity</field>
        <field name="domain">[('state', 'in', ('sale', 'done'))]</field>
        <field name="context">{'create_confirmed_order': True}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                No sales orders yet.
            </p>
        </field>
    </record>

    <!-- Quotes (1) → Holds (3 otro módulo) → Sales Orders (10) -->
    <menuitem id="menu_quotes_root"
              name="Quotes"
              parent="sale.sale_menu_root"
              action="action_quotations_only"
              sequence="1"/>

    <menuitem id="menu_sales_orders_root"
              name="Sales Orders"
              parent="sale.sale_menu_root"
              action="action_sales_orders_only"
              sequence="10"/>

</odoo>```

