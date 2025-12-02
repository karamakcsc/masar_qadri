// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Item Details Per Supplier"] = {
	"filters": [
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					"filters": {
						"has_variants": 0
					}
				};
			}
		},
		{
			"fieldname": "article",
			"label": __("Article"),
			"fieldtype": "Data",
		}
	]
};
