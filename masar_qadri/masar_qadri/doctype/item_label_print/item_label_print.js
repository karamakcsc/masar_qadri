// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Label Print", {
	fetch_items: function(frm) {
        frappe.call({
            doc: frm.doc,
            method: "fetch_items",
            freeze: true,
            freeze_message: "Fetching Items Please Wait..",
            callback: function(r) {
                frm.refresh_field("items");
            }
        })
	},
});
