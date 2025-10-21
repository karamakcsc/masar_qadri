// Copyright (c) 2025, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Summary"] = {
	"filters": [
		{
			"fieldname": "sales_invoice",
			"label": __("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "pos_profile",
			"label": __("POS Profile"),
			"fieldtype": "Link",
			"options": "POS Profile",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},

	]
};
