import frappe


def validate(self, method):
    set_supplier_dimension(self)


def set_supplier_dimension(self):
    if self.supplier:
        for item in self.items:
            item.internal_supplier = self.supplier