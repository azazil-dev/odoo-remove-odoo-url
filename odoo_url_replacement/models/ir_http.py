# -*- coding: utf-8 -*-
# Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
# License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.

import logging
from odoo import models, tools
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @tools.ormcache('self.env.cr.dbname')
    def _get_url_replacement_config(self):
        """
        Returns (enabled, brand_text) cached in registry LRU cache per database.
        Cache is invalidated whenever registry.clear_cache() is called.
        """
        try:
            Param = self.env['ir.config_parameter'].sudo()
            enabled = Param.get_param('odoo_url_replacement.enabled', 'False').strip().lower() in ('1', 'true', 'yes')
            brand = (Param.get_param('odoo_url_replacement.brand_text', '') or '').strip().lower()
            if enabled and brand:
                return True, brand
        except Exception as e:
            _logger.warning("Error fetching odoo_url_replacement configuration: %s", e)
        return False, ''

    @classmethod
    def _match(cls, path_info, key=None):
        """
        Intercept route matching:
        If enabled and path starts with /<brand>, rewrite path to /odoo before matching against routing map.
        """
        try:
            env = request.env if request else None
            if env:
                enabled, brand = env['ir.http']._get_url_replacement_config()
                if enabled and brand:
                    prefix = f"/{brand}"
                    if path_info == prefix:
                        path_info = "/odoo"
                    elif path_info.startswith(f"{prefix}/"):
                        path_info = "/odoo" + path_info[len(prefix):]
        except Exception as e:
            _logger.warning("Error in odoo_url_replacement _match interceptor: %s", e)

        # Call standard matching
        try:
            return super()._match(path_info, key=key)
        except TypeError:
            # Fallback for signatures without 'key'
            return super()._match(path_info)

    def session_info(self):
        result = super().session_info()
        try:
            enabled, brand = self._get_url_replacement_config()
            if enabled and brand:
                result['odoo_url_replacement_enabled'] = True
                result['odoo_url_replacement_brand'] = brand
        except Exception as e:
            _logger.warning("Error adding odoo_url_replacement info to session_info: %s", e)
        return result
