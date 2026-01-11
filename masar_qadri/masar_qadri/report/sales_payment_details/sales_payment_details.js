// Copyright (c) 2026, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Payment Details"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "80",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Link",
			options: "Sales Invoice",
		},
		{
			fieldname: "is_pos",
			label: __("Show only POS"),
			fieldtype: "Check",
		},
		{
			fieldname: "payment_detail",
			label: __("Show Payment Details"),
			fieldtype: "Check",
			default: 1,
		},
	]
};
