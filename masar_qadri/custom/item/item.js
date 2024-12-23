frappe.ui.form.on("Item", {
    onload: function(frm) {
        set_color_code(frm);
    }
});

function set_color_code(frm) {
    if (frm.doc.variant_of && frm.doc.attributes) {
        frappe.call({
            method: "masar_qadri.custom.item.item.get_color_code",
            args: {
                name: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    console.log(r.message);
                    frm.doc.attributes.forEach(row => {
                        if (row.attribute === "Colour") {
                            frappe.model.set_value(row.doctype, row.name, "custom_color_code", r.message);
                        }
                    });
                    frm.refresh_field("attributes");
                }
            }
        });
    }
}
