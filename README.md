# Xavfsiz To'lov Tizimi — Dev Cheat Sheet

## Getting things running

```bash
docker compose up -d              # start everything in background
docker compose ps                 # check what's running / ports
docker compose down                # stop everything
docker compose down -v             # stop + wipe DB volume (fresh start)
docker compose restart backend     # restart just one service
docker compose up -d --build backend   # rebuild after Dockerfile/requirements change
```

## Reading logs (know which container to check)

```bash
docker compose logs backend --tail 30 -f        # Django/DRF app, request/response, view errors
docker compose logs celery_worker --tail 30 -f  # OTP SMS delivery, async payment tasks
docker compose logs celery_beat --tail 30       # scheduled/periodic tasks
docker compose logs nginx --tail 30             # routing errors, config failures
docker compose logs livekit --tail 30           # video session issues
docker compose logs postgres --tail 30          # DB connection issues
```
`-f` tails live — leave it running in a spare terminal while you test in the browser.

## Getting the OTP code (dev mode, no real SMS)

```bash
docker compose logs celery_worker | grep "DEV SMS"
```

## Django shell — inspect/create data directly

```bash
docker compose exec backend python manage.py shell
```
```python
from apps.accounts.models import User
User.objects.all().values("id", "phone", "phone_verified")

from apps.payments.models import PaymentMethod, Transaction
Transaction.objects.filter(user__phone="+998901234567").values("id", "amount", "status")
```

## Migrations

```bash
docker compose exec backend python manage.py makemigrations   # after changing models.py
docker compose exec backend python manage.py migrate           # apply them
docker compose exec backend python manage.py showmigrations    # see what's applied
```

## Admin access

```bash
docker compose exec backend python manage.py createsuperuser
```
Then visit: `http://localhost/admin/`

## Testing API endpoints directly (bypass the frontend)

```bash
# Request OTP
curl -i -X POST http://localhost/api/accounts/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+998901234567"}'

# Verify OTP (grab code from celery_worker logs first)
curl -i -X POST http://localhost/api/accounts/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+998901234567","code":"123456"}'

# Create a transaction (needs a real access token from the verify response)
curl -i -X POST http://localhost/api/payments/transactions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"amount":100000,"payment_method":"<payment_method_uuid>"}'
```

Always hit **`localhost` (port 80, via nginx)** — not `localhost:8000`. Port 8000 is internal-only between containers and isn't published to your Mac.

## Config sanity checks (run these whenever something "just doesn't work")

```bash
docker compose exec nginx nginx -t                       # is nginx config even valid?
docker compose exec backend env | grep SMS_PROVIDER       # dev SMS vs real provider?
docker compose exec celery_worker celery -A config inspect ping   # is celery actually connected?
lsof -nP -iTCP:8000 | grep LISTEN                          # anything squatting on a port?
docker ps --format "table {{.Names}}\t{{.Ports}}"          # port map across all containers
```

## Frontend

```bash
cd frontend && npm run dev          # native, faster HMR — http://localhost:5173
docker compose restart frontend     # or run inside Docker
```
Env var lives in `frontend/.env.local` (`VITE_API_BASE_URL=http://localhost/api`).
**Vite only reads `.env.local` at startup — full restart (Ctrl+C, then `npm run dev`) after any change.**

## Browser-side debugging

- **Network tab** → click the failing request → **Response** tab shows the real backend error (the frontend often just shows a generic "xatolik yuz berdi" message)
- Don't type API URLs directly into the address bar to "test" them — that sends a GET with no auth token, which isn't what the app actually does. Trigger requests by using the actual UI (click the button), then inspect them in Network tab.

## Git

```bash
git remote add origin git@github.com:<you>/<repo>.git   # only once
git push -u origin main                                   # first push
git add -A && git commit -m "message" && git push         # after that
```


# Repo description options

## Short (GitHub "About" field)
Secure payment platform with phone/OTP auth and live video identity verification for high-risk transactions — Django REST Framework, React, LiveKit, Docker.

## Shorter
Secure payments backend + frontend with OTP login and video-based fraud verification (DRF · React · LiveKit · Docker).

## README header version
A secure payment system built with Django REST Framework and React, featuring phone/OTP authentication, tokenized payment methods, an append-only audit log, and LiveKit-powered video verification for high-value or high-risk transactions. Fully containerized with Docker.

## Bilingual (Uzbek + English)
Xavfsiz to'lov tizimi — OTP orqali autentifikatsiya va yuqori xavfli tranzaksiyalar uchun video-KYC (LiveKit) bilan. DRF · React · Docker.
Secure payment system with OTP authentication and LiveKit-based video verification for high-risk transactions.

## Suggested GitHub topics
```
django
drf
react
docker
livekit
fintech
payment-gateway
otp-authentication
webrtc
```