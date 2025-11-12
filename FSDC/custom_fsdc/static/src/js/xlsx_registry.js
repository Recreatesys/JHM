/** @odoo-module **/
import { registry } from "@web/core/registry";
import { BlockUI } from "@web/core/ui/block_ui";
import { download } from "@web/core/network/download";


registry.category("ir.actions.report handlers").add("qwerty_xlsx", async function (action) {
    if (action.report_type === 'xlsx') {
        BlockUI;
	var def = $.Deferred();
    await download({
        
            url: '/xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
            complete: () => unblockUI,    
            error: (error) => self.call('crash_manager', 'rpc_error', error),
        });
    }
});
