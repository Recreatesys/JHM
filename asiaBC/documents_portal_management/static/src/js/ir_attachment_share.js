// /** @odoo-module */

// import { FormRenderer } from '@web/views/form/form_renderer';
// import { patch } from "@web/core/utils/patch";
// import { useService } from "@web/core/utils/hooks";
// import { _t } from "@web/core/l10n/translation";

// const { onMounted, onPatched, useEnv } = owl;

// patch(FormRenderer.prototype, {
//     setup(...args) {
//         super.setup(...args);
//         this.action = useService("action");
//         onPatched(this._renderShareButton.bind(this));
//         onMounted(this._renderShareButton.bind(this));
//     },
//     // _renderShareButton(){
//     //     if (this.props.record.resModel === 'ir.attachment'){
//     //         const $sharebutton = $('<div>');
//     //         $sharebutton.addClass("attachment_share_button");
//     //         $sharebutton.append($('<button>').addClass("btn btn-primary").append($('<i class="fa fa-share-alt"/>')));
//     //         $sharebutton.on('click', this._clickShareButton.bind(this));
//     //         const $sheet = $('.o_form_sheet');
//     //         if (this.props.record.resId && this.props.record.data.datas){
//     //             $sheet.append($sharebutton);
//     //         }
//     //     }
//     // },

    
 


 

//     _clickShareButton: function(ev) {
//         ev.stopPropagation();
//         ev.preventDefault();            
//         var self = this;
//         this.action.doAction({
//             type: 'ir.actions.act_window',
//             name: _t('Share Attachments'),
//             res_model: 'ir.attachment.share',
//             views: [[false, 'form']],
//             view_mode: 'form',
//             target: 'new',
//             context: {
//                 active_model : self.props.record.resModel || false,
//                 default_res_id : self.props.record.resId || false,
//                 active_id : self.props.record.resId || false,
//             }
//         })
//     },
// })

// export default FormRenderer;


/** @odoo-module */

import { FormRenderer } from "@web/views/form/form_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const { onMounted, onPatched } = owl;

patch(FormRenderer.prototype, {
    setup(...args) {
        super.setup(...args);
        this.action = useService("action");
        onMounted(() => this._renderShareButton());
        onPatched(() => this._renderShareButton());
    },

    /**
     * Render Share button only for ir.attachment records
     */
    _renderShareButton() {
        try {
            const root = this.el;
            if (!root) return;
            const sheet = root.querySelector(".o_form_sheet");
            if (!sheet) return;

            const oldButton = sheet.querySelector(".attachment_share_button");
            if (oldButton) oldButton.remove();

            if (
                this.props.record.resModel === "ir.attachment" &&
                this.props.record.resId &&
                this.props.record.data.datas
            ) {
                const btnWrapper = document.createElement("div");
                btnWrapper.classList.add("attachment_share_button");
                btnWrapper.style.marginTop = "10px";
                btnWrapper.style.textAlign = "right";
                const btn = document.createElement("button");
                btn.classList.add("btn", "btn-primary");
                btn.innerHTML = `<i class="fa fa-share-alt"></i> ${_t("Share")}`;
                btn.addEventListener("click", this._clickShareButton.bind(this));
                btnWrapper.appendChild(btn);
                sheet.appendChild(btnWrapper);
            }
        } catch (err) {
            console.warn("Error rendering share button:", err);
        }
    },

    /**
     * Action: open share popup form
     */
    _clickShareButton(ev) {
        ev.stopPropagation();
        ev.preventDefault();

        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Share Attachments"),
            res_model: "ir.attachment.share",
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
            context: {
                active_model: this.props.record.resModel || false,
                default_res_id: this.props.record.resId || false,
                active_id: this.props.record.resId || false,
            },
        });
    },
});

export default FormRenderer;


