frappe.ui.form.on("Item", {
    onload: function(frm) {
        DescriptionProperty(frm);
    }, 
    refresh: function(frm){ 
        DescriptionProperty(frm);
    }, 
    setup: function(frm){
        DescriptionProperty(frm);
    }
});

function DescriptionProperty(frm) { 
    frappe.call({
        method:"masar_qadri.custom.item.item.description_property", 
        args: {
            self: JSON.stringify(frm.doc)
        }, 
        callback: function(r){
            if (r.message){
            frm.set_df_property('custom_description_code', 'read_only', r.message);
            }
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