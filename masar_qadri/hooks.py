app_name = "masar_qadri"
app_title = "Masar Qadri"
app_publisher = "KCSC"
app_description = "Masar Qadri"
app_email = "info@kcsc.com.jo"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "masar_qadri",
# 		"logo": "/assets/masar_qadri/logo.png",
# 		"title": "Masar Qadri",
# 		"route": "/masar_qadri",
# 		"has_permission": "masar_qadri.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/masar_qadri/css/masar_qadri.css"
# app_include_js = "/assets/masar_qadri/js/masar_qadri.js"

# include js, css files in header of web template
# web_include_css = "/assets/masar_qadri/css/masar_qadri.css"
# web_include_js = "/assets/masar_qadri/js/masar_qadri.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "masar_qadri/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "masar_qadri/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "masar_qadri.utils.jinja_methods",
# 	"filters": "masar_qadri.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "masar_qadri.install.before_install"
# after_install = "masar_qadri.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "masar_qadri.uninstall.before_uninstall"
# after_uninstall = "masar_qadri.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "masar_qadri.utils.before_app_install"
# after_app_install = "masar_qadri.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "masar_qadri.utils.before_app_uninstall"
# after_app_uninstall = "masar_qadri.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "masar_qadri.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"validate": "masar_qadri.custom.item.item.validate"
	},
    "Sales Invoice": {
        "before_submit": "masar_qadri.custom.sales_invoice.sales_invoice.before_submit",
        "on_submit": "masar_qadri.notifications.sales_invoice.sales_invoice_notification"
    },
    "Item Attribute": {
        "validate": "masar_qadri.custom.item_attribute.item_attribute.validate"
    },
    "Stock Entry": {
        "on_submit": "masar_qadri.notifications.stock_entry.stock_entry_notification"
    },
    "POS Opening Shift": {
        "on_submit": "masar_qadri.notifications.pos_shift.pos_opening_shift_notification"
    },
    "POS Closing Shift": {
        "on_submit": "masar_qadri.notifications.pos_shift.pos_closing_shift_notification"
    },
}

doctype_js = {
   "Item": "custom/item/item.js",
   "Stock Entry": "custom/stock_entry/stock_entry.js",
   "Purchase Order": "custom/purchase_order/purchase_order.js"
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"masar_qadri.tasks.all"
# 	],
# 	"daily": [
# 		"masar_qadri.tasks.daily"
# 	],
# 	"hourly": [
# 		"masar_qadri.tasks.hourly"
# 	],
# 	"weekly": [
# 		"masar_qadri.tasks.weekly"
# 	],
# 	"monthly": [
# 		"masar_qadri.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "masar_qadri.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.controllers.item_variant.enqueue_multiple_variant_creation": "masar_qadri.override.item.enqueue_multiple_variant_creation", 
    "erpnext.controllers.item_variant.create_variant": "masar_qadri.override.item.create_variant"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "masar_qadri.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["masar_qadri.utils.before_request"]
# after_request = ["masar_qadri.utils.after_request"]

# Job Events
# ----------
# before_job = ["masar_qadri.utils.before_job"]
# after_job = ["masar_qadri.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"masar_qadri.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "name", "in", [
                "Item Attribute Value-custom_description",
                "Item-custom_description_code",
                "Item-custom_item_name_ar",
                "Stock Entry-custom_transaction_type",
                "Sales Invoice Item-custom_sales_person",
                "Sales Invoice Item-custom_section_break_wgrcq",
                "POS Invoice Item-custom_section_break_kipmn",
                "POS Invoice Item-custom_sales_person",
                "Stock Entry Detail-custom_remarks",
                "Stock Entry Detail-custom_section_break_e82qh",
                "Stock Entry-custom_section_break_u4abs",
                "POS Profile-custom_pos_supervisor",
                "POS Profile-custom_section_break_peatv",
                "Stock Entry-custom_target_location",
                "Warehouse-custom_user"
            ]
        ]
    ]},
    {"dt": "Property Setter", "filters": [
        [
            "name", "in", [
                "Purchase Order Item-rate-permlevel",
                "Purchase Order Item-amount-permlevel",
                "Purchase Order Item-base_rate-permlevel",
                "Purchase Order Item-base_amount-permlevel",
                "Stock Entry-main-field_order",
                "Stock Entry Detail-basic_rate-permlevel",
                "Stock Entry-remarks-print_hide",
                "Stock Entry-from_warehouse-mandatory_depends_on",
                "Item-disabled-depends_on",
                "Stock Entry-set_posting_time-depends_on",
                "Stock Entry-inspection_required-depends_on",
                "Stock Entry-apply_putaway_rule-depends_on",
                "Stock Entry-bom_info_section-hidden",
                "Stock Entry-section_break_7qsm-hidden",
                "Customer-mobile_no-unique"
            ]
        ]
    ]}
]
from erpnext.controllers import item_variant
from masar_qadri.override import item 
item_variant.make_variant_item_code = item.make_variant_item_code