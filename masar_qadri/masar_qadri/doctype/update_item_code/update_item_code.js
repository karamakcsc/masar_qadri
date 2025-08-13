// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Update Item Code", {
	update: function(frm) {
        frappe.call({
            doc: frm.doc,
            method: "update_name",
            callback: function(r) {
                console.log("Teeeeeeeeeeeeez");
            }
        })
	},
});
