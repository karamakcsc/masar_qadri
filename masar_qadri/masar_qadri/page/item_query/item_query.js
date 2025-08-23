frappe.pages['item-query'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Item Query',
        single_column: true
    });

    // Main container
    let $container = $(`
        <div class="item-query-form">
            <div class="row"></div>
        </div>
    `).appendTo(page.body);

    // Define fields
    const fields = [
        {
            fieldname: 'item_code',
            label: 'Item Code',
            fieldtype: 'Link',
            options: 'Item',
            onchange: function() {
                let item_code = controls['item_code'].get_value();
                if (!item_code) return;

                frappe.db.get_doc('Item', item_code).then(doc => {
                    controls['item_name'].set_value(doc.item_name);
                    controls['item_description'].set_value(doc.description || '');
                    controls['item_group'].set_value(doc.item_group);

                    // Image preview
                    if (doc.image) {
                        show_item_image(doc.image, doc.item_name);
                    } else {
                        clear_item_image();
                    }

                    // First barcode if any
                    if (doc.barcodes && doc.barcodes.length) {
                        controls['item_barcode'].set_value(doc.barcodes[0]['barcode'] || '');
                    }
                });
            }
        },
        {
            fieldname: 'item_barcode',
            label: 'Item Barcode',
            fieldtype: 'Data',
            onchange: function() {
                let barcode = controls['item_barcode'].get_value();
                if (!barcode) return;

                frappe.call({
                    method: "masar_qadri.masar_qadri.page.item_query.api.get_item_from_barcode",
                    args: { barcode },
                    callback: function(r) {
                        if (!r.message) {
                            frappe.msgprint(__('No item found with this barcode'));
                            controls['item_code'].set_value('');
                            controls['item_name'].set_value('');
                            controls['item_description'].set_value('');
                            controls['item_group'].set_value('');
                            clear_item_image();
                            return;
                        }

                        let item_code = r.message;
                        controls['item_code'].set_value(item_code);

                        // Fetch item details
                        frappe.db.get_doc('Item', item_code).then(doc => {
                            controls['item_name'].set_value(doc.item_name);
                            controls['item_description'].set_value(doc.description || '');
                            controls['item_group'].set_value(doc.item_group);

                            if (doc.image) {
                                show_item_image(doc.image, doc.item_name);
                            } else {
                                clear_item_image();
                            }
                        });
                    }
                });
            }
        },
        {
            fieldname: 'item_name',
            label: 'Item Name',
            fieldtype: 'Data',
            read_only: 1
        },
        {
            fieldname: 'item_description',
            label: 'Item Description',
            fieldtype: 'Small Text',
            read_only: 1
        },
        {
            fieldname: 'item_group',
            label: 'Item Group',
            fieldtype: 'Link',
            options: 'Item Group',
            read_only: 1
        },
        // Use HTML instead of Image control
        {
            fieldname: 'item_image_html',
            label: 'Item Image',
            fieldtype: 'HTML'
        },
        {
            fieldname: 'warehouse',
            label: 'Warehouse',
            fieldtype: 'Link',
            options: 'Warehouse'
        },
        {
            fieldname: 'date',
            label: 'Date',
            fieldtype: 'Date',
            reqd: 1,
            read_only: 1
        }
    ];

    // Render controls
    let controls = {};
    fields.forEach((f) => {
        let $col = $('<div class="col-md-4 mb-3"></div>').appendTo($container.find('.row'));
        controls[f.fieldname] = frappe.ui.form.make_control({
            df: f,
            parent: $col,
            render_input: true
        });
    });

    // Helper: set/clear image
    function show_item_image(image_value, alt_text) {
        // Works with either file URL or file name from File doctype
        let file_url = frappe.utils.get_file_link(image_value);
        // Avoid issues with spaces and special chars
        file_url = encodeURI(file_url);

        const html = `
            <div class="item-image-wrap" style="max-width:100%;">
                <img src="${file_url}" alt="${frappe.utils.escape_html(alt_text || 'Item Image')}"
                     style="max-width:60%;height:auto;object-fit:contain;border:1px solid #e5e7eb;border-radius:8px;padding:4px;display:block;" />
            </div>
        `;
        controls['item_image_html'].$wrapper.html(html);

        // Graceful fallback if the image fails to load (404, 500, or private)
        controls['item_image_html'].$wrapper.find('img').on('error', function() {
            controls['item_image_html'].$wrapper.html(
                `<div class="text-muted small">Image not available (file may be missing or private)</div>`
            );
        });
    }
    function clear_item_image() {
        controls['item_image_html'].$wrapper.html(
            `<div class="text-muted small"></div>`
        );
    }

    // Default date
    controls['date'].set_value(frappe.datetime.get_today());
    clear_item_image();

    // Stock container
    let $stock_container = $('<div class="mt-4"></div>').appendTo($container);

    // Buttons
    let $btn_row = $('<div class="mt-3"></div>').appendTo($container);
    let $btn_get = $('<button class="btn btn-primary mr-2">Get Stock</button>').appendTo($btn_row);
    let $btn_refresh = $('<button class="btn btn-secondary">Refresh</button>').appendTo($btn_row);

    function get_item_code_for_stock(callback) {
        let item_code = controls['item_code'].get_value();
        let barcode = controls['item_barcode'].get_value();

        if (item_code) {
            callback(item_code);
        } else if (barcode) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Item Barcode",
                    filters: { barcode: barcode },
                    fields: ["parent"],
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length) {
                        callback(r.message[0].parent);
                    } else {
                        frappe.msgprint(__('No item found with this barcode'));
                    }
                }
            });
        } else {
            frappe.msgprint(__('Please enter an Item Code or scan/enter an Item Barcode'));
        }
    }

    function fetch_stock() {
        get_item_code_for_stock(function(item_code) {
            if (!item_code) return;

            let warehouse = controls['warehouse'].get_value();
            $stock_container.empty();

            if (warehouse) {
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Bin",
                        filters: { item_code, warehouse },
                        fieldname: ["actual_qty"]
                    },
                    callback: function(r) {
                        let qty = r.message ? r.message.actual_qty : 0;
                        let html = `
                            <table class="table table-bordered mt-3">
                                <thead>
                                    <tr>
                                        <th>Warehouse</th>
                                        <th>Available Qty</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>${warehouse}</td>
                                        <td>${qty || 0}</td>
                                    </tr>
                                </tbody>
                            </table>
                        `;
                        $stock_container.append(html);
                    }
                });
            } else {
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Bin",
                        filters: { item_code },
                        fields: ["warehouse", "actual_qty"],
                        limit_page_length: 500
                    },
                    callback: function(r) {
                        if (r.message && r.message.length) {
                            let rows = r.message.map(d =>
                                `<tr><td>${d.warehouse}</td><td>${d.actual_qty}</td></tr>`
                            ).join("");
                            let html = `
                                <table class="table table-bordered mt-3">
                                    <thead>
                                        <tr>
                                            <th>Warehouse</th>
                                            <th>Available Qty</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${rows}
                                    </tbody>
                                </table>
                            `;
                            $stock_container.append(html);
                        } else {
                            $stock_container.append(`<p>No stock found for this item in any warehouse</p>`);
                        }
                    }
                });
            }
        });
    }

    $btn_get.on('click', fetch_stock);
    $btn_refresh.on('click', function() { location.reload(); });

    setTimeout(() => {
        if (controls['item_barcode'].$input) {
            controls['item_barcode'].$input.focus();
        }
    }, 500);
};
