/** @odoo-module **/
/*
 * Copyright (C) 2026 Arif N Ramadhan (https://www.niits.id)
 * License OPL-1 (Odoo Proprietary License v1.0). See LICENSE file.
 */

import { browser } from "@web/core/browser/browser";
import { router } from "@web/core/browser/router";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const brand = session.odoo_url_replacement_enabled ? session.odoo_url_replacement_brand : null;

if (brand) {
    const brandPrefix = `/${brand}`;

    patch(router, {
        stateToUrl(state) {
            let url = super.stateToUrl(state);
            // If the generated URL starts with /odoo, rewrite it to /<brand>
            if (url === "/odoo") {
                url = brandPrefix;
            } else if (url.startsWith("/odoo/")) {
                url = brandPrefix + url.slice(5);
            } else if (url.startsWith("/odoo?")) {
                url = brandPrefix + url.slice(5);
            }
            return url;
        },

        urlToState(urlObj) {
            let pathname = urlObj.pathname;
            // Translate incoming /<brand> pathname to /odoo so Odoo core router parses state seamlessly
            if (pathname === brandPrefix) {
                urlObj.pathname = "/odoo";
            } else if (pathname.startsWith(`${brandPrefix}/`)) {
                urlObj.pathname = "/odoo" + pathname.slice(brandPrefix.length);
            }
            return super.urlToState(urlObj);
        },
    });

    // Fallback on boot: if browser location still displays /odoo, silently replace with branded URL
    if (browser.location.pathname === "/odoo" || browser.location.pathname.startsWith("/odoo/")) {
        const newPath = brandPrefix + (browser.location.pathname === "/odoo" ? "" : browser.location.pathname.slice(5));
        const newUrl = newPath + browser.location.search + browser.location.hash;
        browser.history.replaceState(browser.history.state, "", newUrl);
    }
}
