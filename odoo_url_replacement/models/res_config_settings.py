# -*- coding: utf-8 -*-
# Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
# License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.

import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

RESERVED_SLUGS = frozenset({
    'odoo', 'web', 'website', 'my', 'shop', 'mail', 'scoped_app',
    'doc', 'report', 'static', 'base', 'longpolling', 'websocket',
    'jsonrpc', 'xmlrpc', 'survey', 'calendar', 'payment', 'api',
})


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    url_replacement_enabled = fields.Boolean(
        string="Enable URL Replacement",
        config_parameter='odoo_url_replacement.enabled',
        default=False,
    )
    url_replacement_brand_text = fields.Char(
        string="Brand Text",
        config_parameter='odoo_url_replacement.brand_text',
    )

    @api.constrains('url_replacement_enabled', 'url_replacement_brand_text')
    def _check_url_replacement_brand(self):
        for record in self:
            if not record.url_replacement_enabled:
                continue

            brand = (record.url_replacement_brand_text or '').strip().lower()
            if not brand:
                raise ValidationError(_("Brand Text is required when URL Replacement is enabled."))

            # Normalize spaces to hyphens for check
            brand = re.sub(r'\s+', '-', brand)

            if len(brand) < 2 or len(brand) > 32:
                raise ValidationError(
                    _("Brand Text must be between 2 and 32 characters long.")
                )

            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', brand):
                raise ValidationError(
                    _("Brand Text can only contain lowercase letters (a-z), digits (0-9), and hyphens (-). "
                      "It cannot start or end with a hyphen.")
                )

            if brand in RESERVED_SLUGS:
                raise ValidationError(
                    _("The brand '%s' is a reserved system keyword and cannot be used.", brand)
                )

    def set_values(self):
        # Normalize brand text before saving
        if self.url_replacement_brand_text:
            cleaned = self.url_replacement_brand_text.strip().lower()
            cleaned = re.sub(r'\s+', '-', cleaned)
            self.url_replacement_brand_text = cleaned

        super().set_values()
        # Invalidate registry cache so ir_http and routing immediately pick up the changes
        self.env.registry.clear_cache()
