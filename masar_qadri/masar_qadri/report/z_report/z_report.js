frappe.query_reports["Z Report"] = {
	filters: [
		{
			fieldname: "pos_profile",
			label: __("POS Profile"),
			fieldtype: "Link",
			options: "POS Profile",
			reqd: 1,
			width: "80",
			get_query: function () {
				return {
					filters: {
						disabled: 0
					}
				};
			},
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			width: "80",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			width: "80",
		},
	],

	onload: function (report) {
		frappe.call({
			method: "masar_qadri.api.get_user_pos_profiles",
			callback: function (r) {
				const allowed_profiles = (r && r.message) ? r.message : [];

				if (allowed_profiles.length) {
					report.get_filter('pos_profile').get_query = function() {
						return {
							filters: [
								['POS Profile', 'name', 'in', allowed_profiles]
							]
						};
					};

					if (allowed_profiles.length === 1) {
						report.set_filter_value('pos_profile', allowed_profiles[0]);
						report.get_filter('pos_profile').df.read_only = 1;
					} else {
						frappe.msgprint(__("Please select a POS Profile."));
					}
				} else {
					frappe.msgprint(__("No POS Profile linked to your user."));
				}
			},
			error: function(err) {
				console.error("Error calling get_user_pos_profiles:", err);
				frappe.msgprint(__("Failed to load POS profiles. Please check console for details."));
			}
		});
	},
};
