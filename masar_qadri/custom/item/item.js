frappe.ui.form.on("Item", {
    onload: function(frm) {
        set_color_code(frm);
        DescriptionProperty(frm);
    }, 
    refresh: function(frm){ 
        DescriptionProperty(frm);
    }, 
    setup: function(frm){
        DescriptionProperty(frm);
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
                        if (row.attribute === "Color") {
                            frappe.model.set_value(row.doctype, row.name, "custom_color_code", r.message);
                        }
                    });
                    frm.refresh_field("attributes");
                }
            }
        });
    }
}
function DescriptionProperty(frm) { 
    frappe.call({
        method:"masar_qadri.custom.item.item.description_property", 
        args: {
            self: JSON.stringify(frm.doc)
        }, 
        callback: function(r){
            frm.set_df_property('custom_description_code', 'read_only', r.message);
        }
    })
}


frappe.ui.form.on("Item Variant Attribute", {
    attribute: function(frm) {
        DescriptionProperty(frm);
    }, 
    attribute_value: function(frm){ 
        DescriptionProperty(frm);
    }
});
