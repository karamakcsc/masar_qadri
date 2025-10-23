frappe.ui.form.on("Stock Entry", {
    custom_target_location: function(frm) {
        set_values_based_on_target_location(frm);
        set_transaction_type_ro(frm);
        set_default_from_warehouse(frm);
    },
    refresh: function(frm) {
        set_target_location(frm, false);
        set_default_warehouse_rec(frm);
        set_transaction_type_ro(frm);
    },
    stock_entry_type: function(frm) {
        set_default_warehouse_rec(frm);
        set_transaction_type_ro(frm);
        set_default_from_warehouse(frm);
    },
    from_warehouse: function(frm) {
        set_transaction_type_ro(frm);
    },
    onload: function(frm) {
        set_target_location(frm, true);
    },
    before_submit: function(frm) {
        set_transfer_status(frm);
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

function set_target_location(frm, clear_items=false) {
    if (frm.doc.outgoing_stock_entry && frm.doc.custom_target_location && frm.doc.docstatus == 0) {
        frm.doc.to_warehouse = frm.doc.custom_target_location;
        frm.refresh_field("to_warehouse");

        let s_wh = "";
        if (frm.doc.items && frm.doc.items.length > 0) {
            s_wh = frm.doc.items[0].s_warehouse;
        }

        if (s_wh) {
            frm.doc.from_warehouse = s_wh;
            frm.refresh_field("from_warehouse");
        }
        
        if (!frappe.user.has_role("Stock Manager")) {
            if (clear_items) {
                frm.clear_table("items");
                frm.refresh_field("items");
            }
        }
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
    if (frm.doc.docstatus == 0 && frm.doc.purpose == "Material Transfer" && frm.doc.from_warehouse == "MRK-MWH01 - QH") {
        frm.set_df_property("custom_transaction_type", "read_only", 1);
        frm.doc.custom_transaction_type = "";
        frm.refresh_field("custom_transaction_type");
    }
}

async function set_default_from_warehouse(frm) {
    if (frm.doc.docstatus !== 0) return;

    if (frm.doc.purpose === "Material Transfer" && !frm.doc.outgoing_stock_entry) {
        const current_user = frappe.session.user;

        const warehouses = await frappe.db.get_list("Warehouse", {
            filters: { custom_user: current_user },
            fields: ["name"]
        });

        if (warehouses && warehouses.length > 0) {
            const default_wh = warehouses[0].name;

            frm.set_value("from_warehouse", default_wh);

            if (frm.doc.items && frm.doc.items.length > 0) {
                frm.doc.items.forEach(row => {
                    frappe.model.set_value(row.doctype, row.name, "s_warehouse", default_wh);
                });
            }

        } else {
            console.log("No warehouse linked to user:", current_user);
        }
    }
}

function set_transfer_status(frm) {
    if (frm.doc.add_to_transit && !frm.doc.outgoing_stock_entry) {
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "custom_transfer_status", "Pending");
    }
    if (!frm.doc.add_to_transit && frm.doc.outgoing_stock_entry) {
        frappe.model.set_value(frm.doc.doctype, frm.doc.name, "custom_transfer_status", "Complete");
    }
    frm.refresh_field("custom_transfer_status");
}
