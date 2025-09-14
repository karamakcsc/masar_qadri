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
        // if (!frappe.user.has_role("Purchase Manager")) {
        //     console.log("Hiding rate column for non-Purchase Manager users");
        //     const grid = frm.get_field('items').grid; 

        //     grid.update_docfield_property('rate', 'in_list_view', 0);

        //     grid.refresh();
        // }

    }
});