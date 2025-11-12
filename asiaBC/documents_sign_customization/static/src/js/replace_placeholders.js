/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { SignablePDFIframe } from "@sign/components/sign_request/signable_PDF_iframe";
import { Document } from "@sign/components/sign_request/document_signable";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(SignablePDFIframe.prototype, {
    enableCustom(signItem) {
    try {
        if (!signItem || !signItem.el || !signItem.data) return;
        if (this.readonly || signItem.data.responsible !== this.currentRole) return;

        const signItemElement = signItem.el;
        const signItemData = signItem.data;
        const signItemType = this.signItemTypesById[signItemData.type_id];

        if (!signItemType || !signItemElement) return;

        const { name, item_type: type, auto_value: autoValue } = signItemType;

        const placeholderMap = this.signInfo.get('placeholderDirectorMap') || {};
        const mapping = placeholderMap[name]; // Use 'name' as the key for mapping

        if (["text", "textarea"].includes(type) && !signItemElement.raw_value) {
            const valueToFill = (mapping && mapping.raw_value) || autoValue;
            if (valueToFill) {
                signItemElement.raw_value = valueToFill;
                if (signItemElement.parentElement) {
                    signItemElement.parentElement.classList.add("o_filled");
                }
            }
        }

        if (name === _t("Date") && !signItemElement.raw_value) {
            const dateValue = this.signInfo.get('todayFormattedDate');
            if (dateValue) {
                signItemElement.raw_value = dateValue;
                if (signItemElement.parentElement) {
                    signItemElement.parentElement.classList.add("o_filled");
                }
            }
        }

        if (["signature", "initial"].includes(type)) {
            signItemElement.addEventListener("click", (e) => {
                this.handleSignatureDialogClick(e.currentTarget, signItemType);
            });
        }

        if (this.env.isSmall && ["text", "textarea"].includes(type)) {
            const inputBottomSheet = new MobileInputBottomSheet({
                type,
                element: signItemElement,
                value: signItemElement.raw_value,
                label: `${signItemType.tip || ''}: ${signItemType.placeholder || ''}`,
                placeholder: signItemElement.placeholder,
                onTextChange: (value) => {
                    signItemElement.raw_value = value;
                },
                onValidate: (value) => {
                    signItemElement.raw_value = value;
                    signItemElement.dispatchEvent(new Event("input", { bubbles: true }));
                    inputBottomSheet.hide();
                    this.navigator.goToNextSignItem();
                },
                buttonText: _t("next"),
            });

            signItemElement.addEventListener("focus", () => {
                inputBottomSheet.updateInputText(signItemElement.raw_value);
                inputBottomSheet.show();
            });
        }

        if (type === "selection") {
            if (signItemElement.raw_value) {
                this.handleInput();
            }

            const optionDiv = signItemElement.querySelector(".o_sign_select_options_display");
            if (optionDiv) {
                optionDiv.addEventListener("click", (e) => {
                    if (e.target.classList.contains("o_sign_item_option")) {
                        const option = e.target;
                        const selectedValue = option.dataset.id;
                        signItemElement.raw_value = selectedValue;
                        option.classList.add("o_sign_selected_option");
                        option.classList.remove("o_sign_not_selected_option");

                        const notSelected = optionDiv.querySelectorAll(`.o_sign_item_option:not([data-id='${selectedValue}'])`);
                        [...notSelected].forEach((el) => {
                            el.classList.remove("o_sign_selected_option");
                            el.classList.add("o_sign_not_selected_option");
                        });

                        this.handleInput();
                    }
                });
            }
        }

        signItemElement.addEventListener("input", this.handleInput.bind(this));

    } catch (error) {
        console.warn("Error in enableCustom for placeholder:", signItem?.data?.type_id, error);
    }
}

});
