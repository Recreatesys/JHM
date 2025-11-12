/** @odoo-module **/

import SearchPanel from "web.searchPanel";
import { patch } from 'web.utils';
const { _t } = require('web.core');
console.log('1111111111111111');
patch(SearchPanel.prototype, 'documents_portal_management.SearchPanel', {
    setup() {
        console.log('2222222222222222');
        this._super();
    }
});