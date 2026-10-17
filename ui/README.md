# ServiceOps Portal UI

Vanilla-JS single-page app for the ServiceOps Portal API. No build step, no Node.

## Build

```bash
docker build -t serviceops-ui:1 ./ui
```

## Run

Join the same Docker network as the API and Postgres (`serviceops-net`):

```bash
docker run -d --name serviceops-ui \
  --network serviceops-net \
  -p 8080:80 \
  --restart unless-stopped \
  serviceops-ui:1
```

Then open `http://localhost:8080` in your browser.

## Pointing the UI at the API

The browser calls the API at the **host-mapped** API port, not via the Docker network.
Edit the `API_BASE` constant near the top of `app.js`:

```js
const API_BASE = "http://localhost:8000";
```

If the API is on a different host or port, change this and rebuild the image.

## Roles

- `ADMIN` — full access, including the Users page.
- `APPROVER` — can approve/reject requests.
- `OPERATOR` — can delete requests.
- `USER` — create and view their own requests.

## Routes

- `#/login`
- `#/dashboard`
- `#/requests`, `#/requests/new`, `#/requests/{id}`
- `#/users` (admin only)
