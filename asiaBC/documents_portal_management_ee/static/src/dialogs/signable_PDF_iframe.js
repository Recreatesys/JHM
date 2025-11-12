/** @odoo-module **/
import { SignablePDFIframe } from "@sign/components/sign_request/signable_PDF_iframe";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(SignablePDFIframe.prototype, {
    postRender() {
        const res = super.postRender();
        this.no_email = true
        this.props.validateBanner
            .querySelector(".o_validate_button_new")
            .addEventListener("click", () => {
                this.signDocument();
            });
        return res;
    },
    _getRouteAndParams() {
        const route = this.signatureInfo.smsToken
            ? `/sign/sign/${encodeURIComponent(this.props.requestID)}/${encodeURIComponent(
                  this.props.accessToken
              )}/${encodeURIComponent(this.signatureInfo.smsToken)}`
            : `/sign/sign/${encodeURIComponent(this.props.requestID)}/${encodeURIComponent(
                  this.props.accessToken
              )}`;

        const params = {
            signature: this.signatureInfo.signatureValues,
            frame: this.signatureInfo.frameValues,
            new_sign_items: this.signatureInfo.newSignItems,
            no_email:this.no_email
        };
        return [route, params];
    }
});
