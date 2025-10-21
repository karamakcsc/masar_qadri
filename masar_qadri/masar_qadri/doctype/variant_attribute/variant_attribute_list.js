frappe.listview_settings['Variant Attribute'] = {
    onload: function(list) {
        list.page.add_inner_button(
            __('Sync Attributes'),
            function() {
                frappe.call({
                    method: 'masar_qadri.masar_qadri.doctype.variant_attribute.variant_attribute.sync_attributes',
                    freeze: true,
                    freeze_message: __('Syncing Attributes...'),
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__("Attributes Synced Successfully"));
                            list.refresh();
                        }
                    }
                });
            },
            __("Actions")
        );
    }
};