# models/account_move_line.py
from odoo import models, api, _ , fields
from odoo.exceptions import UserError
import json
from odoo.tools import format_date
from odoo.tools.misc import formatLang

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service',
        inverse='_inverse_product_id',
        ondelete='restrict',
        check_company=True,
    )
    extra_flags = fields.Json("Extra Flags", default=dict)
    
    product_template_id = fields.Many2one(
        string="Classes",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        search='_search_product_template_id',
        )
    attachment_name = fields.Char(string="Filename")
    logo_attachment_id = fields.Binary(string="Logo",help="Upload Logo of the required service!!!")
    country_id = fields.Many2one(string="Country", comodel_name='res.country', help="Country for which this logo is available")
    city_selection = fields.Selection(
        selection=[
            ('lahore', 'Lahore'),
            ('karachi', 'Karachi'),
            ('islamabad', 'Islamabad'),
        ],
        default='karachi',
        string="City",
    )
    opposition_number = fields.Json(
        string="Opposition Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    appeal_number = fields.Json(
        string="Appeal Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    suit_number = fields.Json(
        string="Suit Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    filing_date= fields.Date(String="Filing Date")
    rectification_no = fields.Json(
        string="Rectification Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    registration_no =fields.Json(
        string="Registration Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    application_variant_data = fields.Json(
        string="Application Number",
        help="Stores mapping of classes → input value",
        store=True
    )
    selected_variant_ids = fields.Json(
        string='Selected Variants',
    )
    selected_variant_names = fields.Json(string="Variant Names", default=list)
    
    trademark_id = fields.Many2one(
        comodel_name="res.partner.trademark",
        string="Trademark",
        domain="[('partner_id', '=', parent.partner_id)]",
    )

    professional_fees = fields.Float(string="Professional Fees")
    service_fee = fields.Float(string="Service Fee", related="product_id.lst_price", readonly=False, store=True)
    fees_calculation = fields.Text(string="Fees Calculation")
    price_unit = fields.Float(string="Fees", help="Total Fees including Professional and Service Fees")
    per_class_fee = fields.Float(string="Per Class Fee", compute="_compute_per_class_fee", store=True, readonly=True)
    
    label_id = fields.Many2one(
        comodel_name="res.partner.label",
        string="Label",
        domain="[('partner_id', '=', parent.partner_id)]",
        ondelete="set null"
    )


    @api.depends('product_id')
    def _compute_per_class_fee(self):
        for rec in self:
            product_classes = rec.product_id.product_tmpl_id.attribute_line_ids.mapped('attribute_id').ids
            variants = rec.env['product.template.attribute.value'].sudo().search([('attribute_id','in', product_classes)])
            if variants:
                rec.per_class_fee = variants[0].price_extra

    @api.onchange('professional_fees', 'selected_variant_names', 'per_class_fee', 'service_fee')
    def _compute_professional_fees_expression(self):
        for rec in self:
            variants = rec.selected_variant_names

            if not variants:
                variants = []
            elif isinstance(variants, str):
                try:
                    variants = json.loads(variants)
                except Exception:
                    variants = []

            count = len(variants) if variants else 1

            total = rec.professional_fees * count
            per_class_total = rec.per_class_fee * count
            final_total = total + per_class_total

            rec.fees_calculation = (
                f"({"{:,.2f}".format(rec.professional_fees)} * {count}) + "
                f"({"{:,.2f}".format(rec.per_class_fee)} * {count}) = {"{:,.2f}".format(final_total)}"
            )

            rec.price_unit = final_total + (rec.service_fee or 0.0)

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    def update_price_unit(self, vals):
        """ Update price_subtotal of this account.move.line """
        self.ensure_one()  
        price = vals.get("price")
        variants = vals.get("selected_variant_ids",[])
        variants_names = vals.get("selected_variant_names",[])
        # application_number = vals.get("application_numbers", {})

        if price is None:
            raise UserError(_("No price provided"))

        try:
            price = float(price)
        except ValueError:
            raise UserError(_("Invalid price value"))

        self.price_unit = price
        self.selected_variant_ids = variants
        self.selected_variant_names = variants_names
        # self.application_id = application_number  
        # raise UserError(_("Application Number: %s") % str(vals.get('variant_price')))
        return {"status": "success", "new_price_subtotal": self.price_subtotal}
    
    def get_field_label(self, field_name):
        field = self._fields.get(field_name)
        if field:
            return field.string
        return field_name

    def get_field_value(self, field_name):
        """Return a display-ready value for a given field name"""
        field = self._fields.get(field_name)
        if not field:
            return ""

        value = getattr(self, field_name, False)
        if not value:
            return ""

        # Handle Many2one
        if field.type == "many2one":
            if field.name == "trademark_id" and value:
                return value.trademark_name
            if field.name == "product_template_id" and self.selected_variant_names:
                return ", ".join(self.selected_variant_names or [])
            return value.display_name

        # Handle Date / Datetime
        if field.type == "date":
            return format_date(self.env, value)
        if field.type == "datetime":
            return fields.Datetime.to_string(value)

        # Handle Binary (image/logo)
        if field.type == "binary":
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            mimetype = "image/png"  
            if hasattr(self, "logo_attachment_id") and self.attachment_name:
                if self.attachment_name.lower().endswith(".jpg") or self.attachment_name.lower().endswith(".jpeg"):
                    mimetype = "image/jpeg"
                elif self.attachment_name.lower().endswith(".gif"):
                    mimetype = "image/gif"
                elif self.attachment_name.lower().endswith(".svg"):
                    mimetype = "image/svg+xml"
            return f"data:{mimetype};base64,{value}"

        if isinstance(value, dict):
            return value

        if isinstance(value, (list, tuple)):
            return value
        
        if field.type == 'float':
            try:
                return formatLang(self.env, value, digits=2)
            except Exception:
                return "{:,.2f}".format(value)

        return str(value)

