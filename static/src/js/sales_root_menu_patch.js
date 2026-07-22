/** @odoo-module **/
import { menuService } from "@web/webclient/menus/menu_service";

// REGLA DE NEGOCIO: entrar a la app de Ventas SIEMPRE abre Sales Orders.
// El webclient nativo usa la acción del menú raíz en el primer acceso, pero
// al re-seleccionar la app (con pestañas/estado previo) puede caer al primer
// submenú por secuencia. Este parche intercepta la selección del raíz de
// Ventas y dispara la acción correcta de forma determinista.
const SALES_ROOT_XMLID = "sale.sale_menu_root";
const SALES_ACTION_XMLID = "sale_menu_restructure.action_sales_orders_only";

const originalStart = menuService.start.bind(menuService);
menuService.start = async (env, deps) => {
    const service = await originalStart(env, deps);
    const originalSelectMenu = service.selectMenu.bind(service);
    service.selectMenu = async (menu) => {
        try {
            const resolved = typeof menu === "number" ? service.getMenu(menu) : menu;
            if (resolved && resolved.xmlid === SALES_ROOT_XMLID) {
                await env.services.action.doAction(SALES_ACTION_XMLID, {
                    clearBreadcrumbs: true,
                });
                service.setCurrentMenu(resolved);
                return;
            }
        } catch (e) {
            console.warn("[sale_menu_restructure] fallback a selección nativa:", e);
        }
        return originalSelectMenu(menu);
    };
    return service;
};
