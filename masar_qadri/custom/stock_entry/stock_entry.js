frappe.ui.form.on("Stock Entry", {
    custom_target_location: function(frm) {
        set_values_based_on_target_location(frm);
        set_transaction_type_ro(frm);
    },
    refresh: function(frm) {
        set_target_location(frm);
        set_default_warehouse_rec(frm);
        set_transaction_type_ro(frm);
    },
    stock_entry_type: function(frm) {
        set_default_warehouse_rec(frm);
        set_transaction_type_ro(frm);
    },
    from_warehouse: function(frm) {
        set_transaction_type_ro(frm);
    }
});


function set_values_based_on_target_location(frm) {
    if (frm.doc.custom_target_location && !frm.doc.outgoing_stock_entry) {
        frm.doc.add_to_transit = 1;
        frm.set_df_property("add_to_transit", "read_only", 1);
        frm.refresh_field("add_to_transit");
        frm.doc.to_warehouse = "Transit - QH";
        frm.refresh_field("to_warehouse");
        frm.doc.items.forEach(item => {
            item.t_warehouse = "Transit - QH";
        });
        frm.refresh_field("items");
    }
}

function set_target_location(frm) {
    if (frm.doc.outgoing_stock_entry && frm.doc.custom_target_location) {
        frm.doc.to_warehouse = frm.doc.custom_target_location;
        frm.refresh_field("to_warehouse");
        frm.doc.items.forEach(item => {
            item.t_warehouse = frm.doc.custom_target_location;
        });
        frm.refresh_field("items");
    }
}

function set_default_warehouse_rec(frm) {
    if (!frm.doc.to_warehouse && frm.doc.docstatus == 0 && frm.doc.stock_entry_type == "Material Receipt") {
        frm.doc.to_warehouse = "MRK-MWH01 - QH";
        frm.refresh_field("to_warehouse");
        frm.doc.items.forEach(item => {
            item.t_warehouse = "MRK-MWH01 - QH";
        });
        frm.refresh_field("items");
    }
}

function set_transaction_type_ro(frm) {
    if (frm.doc.docstatus == 0 && frm.doc.stock_entry_type == "Material Transfer" && frm.doc.from_warehouse == "MRK-MWH01 - QH") {
        console.log("Setting custom_transaction_type to read-only and clearing its value");
        frm.set_df_property("custom_transaction_type", "read_only", 1);
        frm.doc.custom_transaction_type = "";
        frm.refresh_field("custom_transaction_type");
    }
}