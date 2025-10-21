// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Update Item Attribute", {
	fetch_attributes(frm) {
		if (!frm.doc.item) {
			frappe.msgprint("Please select an Item first");
			return;
		}

		frappe.call({
			doc: frm.doc,
			method: "get_item_attribute",
			callback: function(r) {
				if (!r.message) return;

				const attributes = r.message;

				frm.clear_table("current_attributes");
				frm.clear_table("update_attributes");

				attributes.forEach(attr => {
					let current = frm.add_child("current_attributes");
					current.attribute = attr.attribute;
					current.current_attribute_value = attr.attribute_value;

					let update = frm.add_child("update_attributes");
					update.attribute = attr.attribute;
					update.current_attribute_value = attr.attribute_value;
				});

				frm.refresh_field("current_attributes");
				frm.refresh_field("update_attributes");
			}
		});
	},
});
