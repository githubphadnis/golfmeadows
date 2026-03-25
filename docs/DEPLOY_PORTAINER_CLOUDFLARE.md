# Deploy Golf Meadows Website using Portainer + Cloudflare

This setup avoids local development and hosts the site in your Docker environment managed by Portainer.

## Architecture

- FastAPI app container (`golfmeadows-web`) listens on port `8080`
- Cloudflare Tunnel container (`cloudflared`) publishes the site to your domain
- DNS proxied by Cloudflare

## 1) Prepare env file

Create a `.env` file (same folder as `docker-compose.yml`) with:

```env
ADDA_BASE_URL=https://indiaapi.adda.io
ADDA_LOGIN_PATH=/api/auth/login
ADDA_WORK_ORDER_UPDATE_PATH=/api/lattice/update-work-order
ADDA_APT_ID=YOUR_APT_ID

# Choose one auth method:
ADDA_BEARER_TOKEN=
# OR
ADDA_EMAIL=
ADDA_PASSWORD=
```

## 2) Build and run in Portainer

Use this repository in a Portainer stack deployment. Portainer reads `docker-compose.yml` and builds the app image.

If deploying from Git in Portainer:

- Repository URL: `https://github.com/githubphadnis/golfmeadows.git`
- Branch: `cursor/meeting-minutes-bot-evaluation-aa9f` (until merged to main)
- Compose path: `docker-compose.yml`

## 3) Verify app internally

After stack starts, verify:

- `http://<docker-host-ip>:8080/?theme=classic`
- `http://<docker-host-ip>:8080/?theme=bold`
- `http://<docker-host-ip>:8080/?theme=calm`

## 4) Publish via Cloudflare Tunnel

If you already have Cloudflare Tunnel running, point hostnames to this service.

Example `cloudflared` ingress:

```yaml
ingress:
  - hostname: golfmedows.org
    service: http://golfmeadows-web:8080
  - hostname: www.golfmedows.org
    service: http://golfmeadows-web:8080
  - service: http_status:404
```

If cloudflared runs outside this compose network, use the Docker host IP:

```yaml
service: http://<docker-host-ip>:8080
```

## 5) ADDA payload alignment

The endpoint path and expected JSON may vary by ADDA onboarding scope.
If submission fails with validation errors, update:

- `ADDA_WORK_ORDER_UPDATE_PATH` in `.env`
- `_build_work_order_payload()` in `web/app.py`

## 6) Common issues

- `500 ADDA_APT_ID is required` -> set `ADDA_APT_ID` in `.env`
- `ADDA login failed` -> verify email/password and allowed API access
- `404/405 from ADDA` -> verify correct work-order endpoint path from ADDA team
