frappe.ui.form.on("Purchase Order", {
    refresh: function(frm) {
        if (!frm.doc.set_warehouse && frm.doc.docstatus == 0) {
            frm.doc.set_warehouse = "MRK-MWH01 - QH";
            frm.refresh_field("set_warehouse");
            frm.doc.items.forEach(item => {
                item.warehouse = "MRK-MWH01 - QH";
            });
            frm.refresh_field("items");
        }
    },
});