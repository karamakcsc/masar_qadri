// Copyright (c) 2026, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Transit Reconciliation"] = {
	"filters": [
		{
			"fieldname": "stock_entry",
			"label": __("Stock Entry"),
			"fieldtype": "Link",
			"options": "Stock Entry",
			"set_query": function() {
				return {
					"filters": {
						"purpose": "Material Transfer",
						"add_to_transit": 1
					}
				};
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
	]
};
