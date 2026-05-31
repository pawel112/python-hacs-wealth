# Majątek

Custom integration for Home Assistant installed via HACS.

Creates one Home Assistant device named **Majątek** and a fixed set of monetary sensors updated by HTTP POST.

## Fixed categories

The integration exposes these sensors:

- konto bankowe
- gotówka
- kapitał
- karta kredytowa
- giełda
- IKE
- IKZE
- ZUS
- konta celowe
- inwestycje
- inne
- status

## Security

The endpoint accepts requests only with a token in the HTTP header:

```text
Authorization: Bearer TWOJ_TOKEN
```

The token is configured when adding the integration in Home Assistant.

## Example POST

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer moj_sekretny_token" \
  -d '{
    "currency": "PLN",
    "konto_bankowe": 12345.67,
    "gotowka": 500.00,
    "kapital": 100000.00,
    "karta_kredytowa": -1200.00,
    "gielda": 15500.45,
    "ike": 25000.00,
    "ikze": 13000.00,
    "zus": 42000.00,
    "konta_celowe": 8000.00,
    "inwestycje": 32000.50,
    "inne": 900.00,
    "status": "ok"
  }' \
  http://HOME_ASSISTANT:8123/api/majatek
```

## Payload format

```json
{
  "currency": "PLN",
  "konto_bankowe": 12345.67,
  "gotowka": 500.00,
  "kapital": 100000.00,
  "karta_kredytowa": -1200.00,
  "gielda": 15500.45,
  "ike": 25000.00,
  "ikze": 13000.00,
  "zus": 42000.00,
  "konta_celowe": 8000.00,
  "inwestycje": 32000.50,
  "inne": 900.00,
  "status": "ok"
}
```

## Installation in HACS

1. Push this repository to GitHub.
2. In Home Assistant open HACS -> Integrations -> three dots -> Custom repositories.
3. Add the GitHub repository URL and choose category **Integration**.
4. Install **Majątek**.
5. Restart Home Assistant.
6. Add integration **Majątek** from Devices & Services.
7. During setup enter the default currency and secret token.

## Notes

- The HTTP endpoint is `/api/majatek`.
- All monetary sensors belong to one device: `Majątek`.
- Currency defaults to `PLN` and may be overridden in each POST.
- The endpoint returns `401` for missing or wrong token.
