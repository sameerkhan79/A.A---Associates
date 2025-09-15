/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { CheckBox } from "@web/core/checkbox/checkbox";

export class InvoiceLineListRendererWithFieldCheckbox extends ListRenderer {
    static components = { ...ListRenderer.components, CheckBox };
    static recordRowTemplate = "account_move_inherit.ListRenderer.RecordRowWithCheckbox";
    setup() {
        super.setup()

    }
    onFieldCheckboxToggle(record, fieldName, ev) {
        const checked = ev.target.checked;
        const recId = record.resId || record.id;
        console.log('Toggle for', recId, fieldName, checked);

        const newFlags = Object.assign({}, record.data.extra_flags || {});

        if (!newFlags[recId]) {
            newFlags[recId] = [];
        }

        if (checked) {
            if (!newFlags[recId].includes(fieldName)) {
                newFlags[recId].push(fieldName);
            }
        } else {
            newFlags[recId] = newFlags[recId].filter(f => f !== fieldName);
        }

        const priority = {
            product_id: 1,                 // Service
            product_template_id: 2,        // Classes
            trademark_id: 3,               // Trademark
            application_variant_data: 4,   // Application Number
            opposition_number: 5,
            registration_no: 6,
            suit_number: 7,
            appeal_number: 8,
            rectification_no: 9,
            filing_date: 10,
            country_id: 11,
            city_selection: 12,
            logo_attachment_id: 13,
            professional_fees: 9990,
            service_fee: 9991,
            per_class_fee: 9992,
            fees_calculation: 9993,
            price_unit: 9999,  
        };


        newFlags[recId] = newFlags[recId].sort((a, b) => {
            const pa = priority[a] || 100;  
            const pb = priority[b] || 100;
            if (pa !== pb) {
                return pa - pb;  
            }
            return a.localeCompare(b); 
        });

        record.update({ extra_flags: newFlags });
    }


}

export class InvoiceLineOne2ManyWithFieldCheckbox extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: InvoiceLineListRendererWithFieldCheckbox,
    };
}

registry.category("fields").add("invoiceLine_list_renderer_with_checkbox", {
    ...x2ManyField,
    component: InvoiceLineOne2ManyWithFieldCheckbox,
});
