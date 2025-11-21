### Authentication & Authorization

Nyx secures protected endpoints with a Litestar guard that validates Bearer JWTs against a JWKS endpoint (Zitadel by default).

Overview
- Guard: `src.guards.jwt_guard`
- JWKS cache: fetched on demand from `config.zitadel.Settings.jwks_url` and cached for 3600s
- All `profiles` routes are protected (`guards = [jwt_guard]`)

Config
- See docs/configuration.md. Defaults:
  - `ISSUER=http://localhost:8080`
  - `JWKS_URL=http://localhost:8080/oauth/v2/keys`
  - `AUDIENCE=347527518753980419`

Using Zitadel locally
- Quick login to the admin console:
```
http://localhost:8080/ui/console?login_hint=zitadel-admin@zitadel.localhost
```
- Use the password:
```
Password1!
```
- After logging in, create an application (client) and use its Client ID as the `AUDIENCE` for Nyx.
- See the full guide: `docs/zitadel.md`.

Local development options
1) Run a Zitadel instance reachable at your configured `JWKS_URL` and use tokens issued with a `kid` present in the JWKS.
2) Use a statically signed JWT for tests; ensure the JWKS served contains the matching `kid` and public key.

Supplying the token
- Send `Authorization: Bearer <token>` header when calling protected endpoints.

Troubleshooting 401/403
- Verify the token `kid` exists in the JWKS and the `aud` matches `config.zitadel.Settings.audience`.
- Ensure clock skew is reasonable; tokens not yet valid or expired will be rejected.
- Check that your JWKS URL is reachable from the app container/host.

Temporarily bypassing guards (not for commit)
- For quick local exploration, you may remove the guard from `ProfileController` handlers. Do not commit this change.
