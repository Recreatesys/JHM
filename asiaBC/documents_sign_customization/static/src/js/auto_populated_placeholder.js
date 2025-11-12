/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SignRequest } from "@sign/backend_components/sign_request/sign_request_action";

patch(SignRequest.prototype, {
    setup() {
        super.setup();
        this.signInfo.set({
            ...this.signInfo.get(),
            placeholderDirectorMap: this.props.action.context.placeholder_director_map || {},
        });
    },
});
