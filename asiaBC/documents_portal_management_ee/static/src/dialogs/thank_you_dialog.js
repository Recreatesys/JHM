/** @odoo-module **/
import { ThankYouDialog } from "@sign/dialogs/dialogs";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ThankYouDialog.prototype, {
   setup() {
        super.setup();
        this.message = _t("Please note that the document is not sending out, please save the document by clicking the below button");
    }
});
