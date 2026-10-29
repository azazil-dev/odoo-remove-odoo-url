# -*- coding: utf-8 -*-
# Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
# License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.

{
    'name': "Odoo URL Replacement",
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': "Replace /odoo backend URL with your own custom brand slug for white-labeling",
    'description': """
Odoo URL Replacement (Remove Odoo URL)
=====================================
Replace the `/odoo` segment in backend URLs with your custom brand name.
For example, `https://yourdomain.com/odoo/action-250` becomes `https://yourdomain.com/brand/action-250`.

Key Features:
- Seamless white-labeling for Odoo 19 backend.
- Easy toggle and brand slug configuration in General Settings.
- Automatic redirects from `/odoo` and `/web` to branded URLs.
- Zero server restart needed; changes apply immediately on save.
- Completely safe default: reverts to 100% native Odoo behavior when disabled.
- Works cleanly on both Odoo 19 Community Edition and Enterprise.
    """,
    'author': "Arif N Ramadhan",
    'website': "https://www.niits.id",
    'maintainer': "Arif N Ramadhan",
    'support': "sqlrif@gmail.com",
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'base_setup',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_url_replacement/static/src/js/router_brand_patch.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/setting.png',
        'static/description/before.png',
        'static/description/after.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
