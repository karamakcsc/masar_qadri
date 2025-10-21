frappe.pages['item-details'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Item Details',
        single_column: true
    });

    // Container
    let $container = $(`<div class="item-details-form"><div class="row"></div></div>`).appendTo(page.body);

    // Filter fields
    const fields = [
        {
            fieldname: 'item_group',
            label: 'Item Group',
            fieldtype: 'Link',
            options: 'Item Group'
        },
        {
            fieldname: 'article',
            label: 'Article',
            fieldtype: 'Data'
        },
        {
            fieldname: 'size',
            label: 'Size',
            fieldtype: 'Data'
        },
        {
            fieldname: 'color',
            label: 'Color',
            fieldtype: 'Data'
        },
        {
            fieldname: 'season',
            label: 'Season',
            fieldtype: 'Data'
        },
        {
            fieldname: 'warehouse',
            label: 'Warehouse',
            fieldtype: 'Link',
            options: 'Warehouse',
            get_query: function() {
                return {
                    filters: { 
                        warehouse_type: ['!=', 'Transit'],
                        is_group: 0
                    }
                };
            }
        }
    ];

    // Render Controls
    let controls = {};
    fields.forEach((f) => {
        let $col = $('<div class="col-md-4 mb-3"></div>').appendTo($container.find('.row'));
        controls[f.fieldname] = frappe.ui.form.make_control({
            df: f,
            parent: $col,
            render_input: true
        });
    });

    // Results Container
    let $result_container = $('<div class="mt-4"></div>').appendTo($container);

    // Buttons
    let $btn_row = $('<div class="mt-3"></div>').appendTo($container);
    let $btn_get = $('<button class="btn btn-primary mr-2">Get Items</button>').appendTo($btn_row);
    let $btn_clear = $('<button class="btn btn-secondary">Clear</button>').appendTo($btn_row);

    // Validate Filters
    function validate_filters() {
        const item_group = controls['item_group'].get_value();
        const article = controls['article'].get_value();

        if (!item_group && !article) {
            frappe.msgprint(__('Please select either Item Group or Article before applying other filters.'));
            return false;
        }
        return true;
    }

    // Fetch Items
    function fetch_items() {
        if (!validate_filters()) return;

        const args = {
            item_group: controls['item_group'].get_value(),
            article: controls['article'].get_value(),
            size: controls['size'].get_value(),
            color: controls['color'].get_value(),
            season: controls['season'].get_value(),
            warehouse: controls['warehouse'].get_value()
        };

        $result_container.empty().html(`<p class="text-muted">Loading...</p>`);

        frappe.call({
            method: "masar_qadri.masar_qadri.page.item_details.api.get_items_with_filters",
            args: args,
            callback: function(r) {
                const items = r.message || [];
                render_results(items);
            }
        });
    }

    // Render Results Table
    function render_results(items) {
        $result_container.empty();

        if (!items.length) {
            $result_container.html(`<p>No items found.</p>`);
            return;
        }

        let html = `
            <table class="table table-bordered mt-3">
                <thead class="thead-light">
                    <tr>
                        <th>Item Code</th>
                        <th>Item Name</th>
                        <th>Item Group</th>
                        <th>Brand</th>
                        <th>Article</th>
                        <th>Season</th>
                        <th>Color</th>
                        <th>Size</th>
                        <th>Style</th>
                        <th>Warehouse</th>
                        <th>Qty</th>
                    </tr>
                </thead>
                <tbody>
        `;

        items.forEach(item => {
            if (item.stock && item.stock.length) {
                item.stock.forEach(s => {
                    html += `
                        <tr>
                            <td>${item.name || '-'}</td>
                            <td>${item.item_name || '-'}</td>
                            <td>${item.item_group || '-'}</td>
                            <td>${item.brand || '-'}</td>
                            <td>${item.article || '-'}</td>
                            <td>${item.season || '-'}</td>
                            <td>${item.color || '-'}</td>
                            <td>${item.size || '-'}</td>
                            <td>${item.style || '-'}</td>
                            <td>${s.warehouse || '-'}</td>
                            <td>${s.actual_qty || 0}</td>
                        </tr>
                    `;
                });
            } else {
                html += `
                    <tr>
                        <td>${item.name || '-'}</td>
                        <td>${item.item_name || '-'}</td>
                        <td>${item.item_group || '-'}</td>
                        <td>${item.brand || '-'}</td>
                        <td>${item.article || '-'}</td>
                        <td>${item.season || '-'}</td>
                        <td>${item.color || '-'}</td>
                        <td>${item.size || '-'}</td>
                        <td>${item.style || '-'}</td>
                        <td>-</td>
                        <td>0</td>
                    </tr>
                `;
            }
        });

        html += `</tbody></table>`;
        $result_container.html(html);
    }

    // Clear Form
    $btn_clear.on('click', function() {
        Object.keys(controls).forEach(k => controls[k].set_value(''));
        $result_container.empty();
    });

    $btn_get.on('click', fetch_items);
};