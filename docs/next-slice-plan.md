# National Surface Expansion + Core Slice Plan

> **For Hermes:** Extend the existing isolated stack with additional branded national-facing routes and matching real API endpoints, then verify with tests and live screenshots.

**What will be done**
- Add reusable site chrome/navigation for the existing Next.js app.
- Create additional branded routes for verification, field operations, and official exports.
- Extend the FastAPI service with real JSON endpoints backing those new routes.
- Add tests for the new API endpoints.
- Rebuild the Docker stack and verify routes/screenshots live.

**Why this approach**
- Only one front-facing app exists today, so the cleanest way to propagate the design system is to add real routes in the existing app instead of inventing empty parallel repos.
- This keeps design and product progress aligned: branding rollout also becomes real functional expansion.
- No unnecessary new dependencies.

**Files likely touched**
- `apps/admin-portal/app/page.tsx`
- `apps/admin-portal/app/globals.css`
- `apps/admin-portal/app/layout.tsx`
- `apps/admin-portal/app/verify/page.tsx`
- `apps/admin-portal/app/field/page.tsx`
- `apps/admin-portal/app/exports/page.tsx`
- `apps/admin-portal/components/*`
- `services/api/app/data.py`
- `services/api/app/main.py`
- `services/api/tests/test_app.py`

**Expected outcome**
- Multiple real branded national-platform surfaces exist and render live.
- API exposes real starter endpoints for territories, verification, field work, and exports.
- The isolated stack becomes more product-like, not just prettier.

**Risks and mitigation**
- Risk: route sprawl without shared styling. Mitigation: add reusable shared chrome.
- Risk: visual regression. Mitigation: rebuild and capture screenshots for each route.
- Risk: fake functionality. Mitigation: back every new route with a live API response.

**Verification**
- Run API tests.
- Rebuild admin/API containers.
- Curl each route and endpoint.
- Capture screenshots for the branded routes.
