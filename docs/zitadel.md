### Using Zitadel with Nyx (Local Dev)

This guide shows a minimal, working local setup of Zitadel and how to use it with Nyx.

What you’ll do
- Run Zitadel locally (Docker Compose)
- Log in to the admin console
- Create an OAuth application for API access
- Configure Nyx to validate JWTs against Zitadel’s JWKS
- Call a protected endpoint with a Bearer token

Prerequisites
- Docker and Docker Compose installed
- Nyx cloned locally

1) Start Zitadel locally
- This repository includes a Docker Compose file at `zitadel.yaml` suitable for local development.
```
docker compose -f zitadel.yaml up -d
```
- Wait until the `zitadel` service reports healthy.

2) Open the Zitadel admin console
- Visit the console with a pre-filled login hint (default local admin):
```
http://localhost:8080/ui/console?login_hint=zitadel-admin@zitadel.localhost
```
- Log in with the password:
```
Password1!
```

Notes
- If you changed the default admin in `zitadel.yaml`, use those credentials instead.
- The console is proxied by the Zitadel container on port 8080.

3) Create an OAuth client (Machine-to-Machine or Web flow)
- In the console, create a new Project (e.g., "Nyx").
- Under the project, create an Application:
  - For server-to-server use, choose "Machine" (Client Credentials).
  - For user-involved flows, choose an OIDC app (e.g., Authorization Code) and configure redirect URIs.
- After creation, note these values:
  - Client ID (this will be your token `aud` and our app’s `AUDIENCE`)
  - Issuer URL (typically `http://localhost:8080` locally)
  - JWKS URL (typically `http://localhost:8080/oauth/v2/keys`)

4) Configure Nyx to use Zitadel
- Create or update your `.envs/.zitadel` file:
```
ISSUER=http://localhost:8080
JWKS_URL=http://localhost:8080/oauth/v2/keys
AUDIENCE=<your-zitadel-client-id>
JWKS_REFRESH_INTERVAL=21600
```
- Important: The `AUDIENCE` must match the Client ID of the application you created in Zitadel. The current codebase default for audience is `client-id` (see `config/zitadel.py`); override it here if your client ID is different.

5) Obtain a token
- For Machine-to-Machine: create a service user or use the application’s client credentials according to Zitadel docs to obtain a JWT. Ensure the token’s header contains a `kid` that exists in the JWKS served at `JWKS_URL`.
- For user flows: perform the chosen OIDC flow to obtain an ID token or access token.

6) Call a protected endpoint in Nyx
- Include the token in the `Authorization` header:
```
curl -H "Authorization: Bearer <your-jwt>" \
     http://localhost:8000/profiles
```
- If the guard rejects the token, see Troubleshooting below.

Troubleshooting
- 401/403 responses:
  - Ensure the token’s `kid` is present in the JWKS at `JWKS_URL`.
  - Verify `aud` matches the `AUDIENCE` value configured for Nyx (your Zitadel client ID).
  - Check token validity/clock skew (`iat`, `nbf`, `exp`).
  - Confirm `ISSUER` matches the token’s issuer.
- Zitadel not reachable:
  - Confirm containers are healthy: `docker compose -f zitadel.yaml ps`.
  - Ensure ports 8080 (API/console) and 3000 (login UI) aren’t blocked.

References
- Zitadel Quickstart and docs: https://zitadel.com/docs
- JWKS endpoint (local default): `http://localhost:8080/oauth/v2/keys`
- Admin console (local default): `http://localhost:8080/ui/console`
