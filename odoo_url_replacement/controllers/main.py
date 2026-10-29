# -*- coding: utf-8 -*-
# Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
# License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.

import logging

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

_logger = logging.getLogger(__name__)


class BrandedHome(Home):

    @http.route()
    def web_client(self, s_action=None, **kw):
        """
        Redirect /odoo and /web GET requests to branded URL when replacement is enabled.
        Preserves query parameters and avoids loops by checking request.httprequest.path.
        """
        try:
            raw_path = request.httprequest.path
            enabled, brand = request.env['ir.http']._get_url_replacement_config()
            if enabled and brand and request.httprequest.method == 'GET':
                # Check if original request came via /odoo or /web (not through /<brand>)
                if raw_path == '/web' or raw_path == '/odoo' or raw_path.startswith('/odoo/'):
                    if raw_path.startswith('/odoo/'):
                        target_path = f"/{brand}" + raw_path[5:]  # replace leading '/odoo' with '/<brand>'
                    else:
                        target_path = f"/{brand}"

                    query_str = request.httprequest.query_string.decode('utf-8')
                    redirect_url = f"{target_path}?{query_str}" if query_str else target_path
                    return request.redirect(redirect_url, code=302, keep_hash=True)
        except Exception as e:
            _logger.warning("Error in odoo_url_replacement web_client redirect: %s", e)

        return super().web_client(s_action=s_action, **kw)

    def _login_redirect(self, uid, redirect=None):
        """
        Ensure user redirects to /<brand> instead of /odoo after login.
        """
        try:
            enabled, brand = request.env['ir.http']._get_url_replacement_config()
            if enabled and brand:
                if not redirect:
                    redirect = f"/{brand}"
                elif redirect == '/odoo' or redirect == '/web':
                    redirect = f"/{brand}"
                elif redirect.startswith('/odoo/'):
                    redirect = f"/{brand}" + redirect[5:]
        except Exception as e:
            _logger.warning("Error in odoo_url_replacement _login_redirect: %s", e)

        return super()._login_redirect(uid, redirect=redirect)
