# -*- coding: utf-8 -*-
# Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
# License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.

from odoo import SUPERUSER_ID, api


def uninstall_hook(env_or_cr, registry=None):
    if isinstance(env_or_cr, api.Environment):
        env = env_or_cr
    else:
        env = api.Environment(env_or_cr, SUPERUSER_ID, {})
    # Remove config parameters cleanly
    params = env['ir.config_parameter'].sudo().search([
        ('key', 'in', ['remove_odoo_url.enabled', 'remove_odoo_url.brand_text'])
    ])
    if params:
        params.unlink()
    env.registry.clear_cache()

