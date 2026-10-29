# Odoo URL Replacement (odoo_url_replacement)

**Technical Name:** `odoo_url_replacement`  
**Compatibility:** Odoo 18.0 Community & Enterprise  
**Author:** Arif N Ramadhan &bull; [Niits Inovasi Teknologi](https://www.niits.id)  
**License:** [OPL-1 (Odoo Proprietary License v1.0)](https://www.odoo.com/documentation/18.0/legal/licenses.html)  
**Price:** Free  

---

## Overview

In Odoo 18, all backend URLs are prefixed by `/odoo` (e.g. `https://yourdomain.com/odoo/action-250`).

**Odoo URL Replacement** allows administrators to replace the default `/odoo` segment with their own custom brand name (such as `https://yourdomain.com/brand/action-250`) for a fully white-labeled ERP experience.

---

## Key Features

- **Custom Brand Slug:** Set any custom alphanumeric brand slug (`2` to `32` characters).
- **Zero Server Restart:** Settings take effect immediately after saving in General Settings via registry cache clearing.
- **Smart 302 Redirection:** Incoming requests to `/odoo`, `/odoo/<path>`, and legacy `/web` URLs automatically redirect to the branded URL while preserving query strings and hashes.
- **Login Flow Integration:** Successful login redirects users straight to `/<brand>`.
- **Safe Defaults:** Reverts to 100% native Odoo behavior when disabled or if configuration is unassigned.
- **Strict Validation:** Prevents collisions with core routes and reserved keywords (`web`, `website`, `scoped_app`, `mail`, `report`, etc.).
- **Clean Uninstallation:** Restores standard Odoo routing and clears database parameters automatically.

---

## Installation & Setup

1. Place the `odoo_url_replacement` folder into your Odoo addons path.
2. Restart the Odoo server.
3. Activate Developer Mode and go to **Apps &rarr; Update Apps List**.
4. Search for **Odoo URL Replacement** and click **Install**.
5. Navigate to **Settings &rarr; General Settings**.
6. In the **URL Replacement Settings** section:
   - Check **Enable URL Replacement**.
   - Enter your **Brand Text** (e.g. `mycompany`).
   - Click **Save**.

---

## URL Mapping Reference

| Default Odoo 18 URL | With Module (e.g. `brand = mycompany`) | Description |
|---|---|---|
| `/odoo` | `/mycompany` | Backend dashboard |
| `/odoo/action-250` | `/mycompany/action-250` | Specific action / view |
| `/odoo/action-250/12` | `/mycompany/action-250/12` | Specific record form |
| `/web` | `/mycompany` | Legacy web client route (redirected) |
| `/web/login` | `/web/login` | Unchanged (standard authentication) |
| Technical endpoints (`/jsonrpc`, `/websocket`, `/report/*`) | Unchanged | Preserved for stability & compatibility |

---

## Emergency Recovery (SQL)

If you ever need to disable the module directly from the database without accessing the backend UI:

```sql
UPDATE ir_config_parameter
SET value = 'False'
WHERE key = 'odoo_url_replacement.enabled';
```

Then clear the registry cache or restart the Odoo service.

---

## Support & Contact

- **Author:** Arif N Ramadhan
- **Email:** [sqlrif@gmail.com](mailto:sqlrif@gmail.com)
- **Website:** [https://www.niits.id](https://www.niits.id)
- **License:** OPL-1 (Odoo Proprietary License v1.0)
