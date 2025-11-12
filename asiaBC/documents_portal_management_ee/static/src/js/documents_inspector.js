// /** @odoo-module */

// import { _t } from "@web/core/l10n/translation";
// import { DocumentsInspector } from "@documents/views/inspector/documents_inspector";
// import { patch } from "@web/core/utils/patch";
// import { useService } from "@web/core/utils/hooks";
// import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';
// import { session } from "@web/session";

// patch(DocumentsInspector.prototype, {
//     setup() {
//         super.setup();
//         this.rpc = useService("rpc");
//         this.dialogService = useService("dialog");
//         this.notificationService = useService('notification');
//     },

//     async onSharedUsers(ev){
//         ev.preventDefault();
//         ev.stopPropagation();

//         if (!this.props.documents.length) {
//             return;
//         }

//         if (this.props.documents.length > 1){
//             return this.notificationService.add(
//                 _t("Failed: Please select just one document."), 
//                 { type: "danger" }
//             );
//         }

//         if (this.props.documents[0].data.owner_id[0] != session.uid){
//             return this.notificationService.add(
//                 _t("Failed: Sharing document belonging to others is prohibited."), 
//                 { type: "danger" }
//             );
//         }

//         if (!this.resIds[0]){
//             return;
//         }
//         console.log(this)
//         const record = this.props.documents[0];
//         this.dialogService.add(FormViewDialog, {
//             title: _t('Share a file with another user'),
//             resModel: 'documents.document',
//             resId: this.resIds[0],
//             context: {
//                 form_view_ref: 'documents_portal_management_ee.document_view_form_shared_users',
//             },
//             onRecordSaved: async (result) => await record.model.load(),
//         });
//     }
// });





/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { DocumentsDetailsPanel } from "@documents/components/documents_details_panel/documents_details_panel";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';
import { session } from "@web/session";

patch(DocumentsDetailsPanel.prototype, {
    setup() {
        super.setup(...arguments);
        this.rpc = useService("rpc");
        this.dialogService = useService("dialog");
        this.notificationService = useService('notification');
    },

    async onSharedUsers(ev){
        ev.preventDefault();
        ev.stopPropagation();

        const records = this.props.list.records;

        if (!records.length) {
            return;
        }

        if (records.length > 1){
            return this.notificationService.add(
                _t("Failed: Please select just one document."), 
                { type: "danger" }
            );
        }

        const record = records[0];

        if (record.data.owner_id[0] !== session.uid){
            return this.notificationService.add(
                _t("Failed: Sharing document belonging to others is prohibited."), 
                { type: "danger" }
            );
        }

        if (!record.resId){
            return;
        }

        this.dialogService.add(FormViewDialog, {
            title: _t('Share a file with another user'),
            resModel: 'documents.document',
            resId: record.resId,
            context: {
                form_view_ref: 'documents_portal_management_ee.document_view_form_shared_users',
            },
            onRecordSaved: async () => await this.props.list.load(),
        });
    }
});