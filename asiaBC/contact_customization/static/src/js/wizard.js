/** @odoo-module **/

import { registry } from '@web/core/registry';

function downloadAndClose(env, action) {
    window.open(action.params.url, '_self');
    return { type: 'ir.actions.act_window_close' };
}
registry.category('actions').add('download_and_close_wizard', downloadAndClose);
export default downloadAndClose;
