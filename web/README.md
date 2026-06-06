# Gym Management — Frontend

Vue 3 SPA za Gym Management sustav. Komunicira s FastAPI backendom (`../api`).

## Tehnologije

| Sloj             | Tehnologija                       |
| ---------------- | --------------------------------- |
| UI framework     | Vue 3 (Composition API, `<script setup>`) |
| Build tool       | Vite 6                            |
| Jezik            | TypeScript (strict)               |
| Routing          | Vue Router 4 (s guardovima)       |
| State management | Pinia                             |
| HTTP             | Axios (s interceptorom za JWT refresh) |

## Pokretanje (lokalno)

Preduvjet: backend mora biti pokrenut na `http://localhost:8000`
(vidi upute u `../api`).

```bash
cd web
npm install
cp .env.example .env   # Windows: Copy-Item .env.example .env
npm run dev
```

App radi na <http://localhost:5173>.

U developmentu se koristi **Vite proxy**: svi pozivi na `/api/*` preusmjeravaju
se na `http://localhost:8000`, pa nema CORS problema lokalno.

### Dev kredencijali (iz backend seed-a)

| Korisničko ime | Lozinka  | Uloga   |
| -------------- | -------- | ------- |
| `admin`        | `admin123` | Admin   |
| `trainer1`     | `pass123`  | Trener  |
| `member1`      | `pass123`  | Član (aktivna članarina) |
| `member2`      | `pass123`  | Član    |

## Struktura

```
web/
├── src/
│   ├── main.ts                  # Bootstrap: Pinia + Router + mount
│   ├── App.vue                  # Layout switcher (route.meta.layout)
│   ├── router/                  # Rute + globalni guard (auth, role)
│   ├── stores/                  # Pinia: auth.ts, toast.ts
│   ├── services/                # API pozivi po domeni + axios instanca
│   │   ├── api.ts               # Axios + interceptor (JWT auto-refresh)
│   │   ├── auth.service.ts
│   │   ├── training.service.ts
│   │   ├── reservation.service.ts
│   │   ├── membership.service.ts
│   │   └── user.service.ts
│   ├── types/                   # TypeScript interfejsi (1:1 s Pydantic shemama)
│   ├── utils/                   # format.ts (datumi, statusi na hrvatskom)
│   ├── layouts/                 # LayoutGost.vue, LayoutAplikacija.vue
│   ├── components/              # Modal, Toast, status/loading/error/empty
│   └── views/                   # Stranice (Login, Trainings, Memberships, ...)
└── ...config fajlovi
```

## Arhitektura

```
View (.vue)  →  Service (services/)  →  Axios (api.ts)  →  Backend API
                                          ↑
                          interceptor lijepi Bearer token,
                          na 401 osvjezi token i ponovi zahtjev
```

- **Auth flow:** login dohvati access + refresh token, sprema ih u
  `localStorage`, pa povlaci korisnika preko `/auth/me`.
- **Auto-refresh:** access token traje 15 min. Kad istekne (401), interceptor
  jednom pozove `/auth/refresh`; ako i to padne → odjava i redirect na login.
- **Route guardovi:** privatne rute traze prijavu; `/admin/*` traze admin rolu.
  Direktan upis URL-a admin stranice bez prava → redirect na dashboard.

## Deploy na Railway

Frontend i backend se deployaju kao **dva odvojena servisa** iz istog repoa.

### 1. Backend servis (ako vec nije)
- Root directory: `api`
- Env varijable: `DATABASE_URL`, `JWT_SECRET`, i **`CORS_ORIGINS`**
  (postavi na URL frontenda, npr. `https://gym-web-production.up.railway.app`)

> ⚠️ Backend mora imati CORS middleware. Vidi `_BACKEND_PATCH_main.py` i
> `_BACKEND_PATCH_config.py` u ovom folderu — zamijeni njima postojece
> `api/app/main.py` i `api/app/core/config.py`.

### 2. Frontend servis
- Root directory: `web`
- Railway automatski detektira `nixpacks.toml` (build → `npm run build`,
  start → `npm run preview`)
- Env varijabla: **`VITE_API_URL`** = puni URL backenda
  (npr. `https://gym-api-production.up.railway.app`)

> `VITE_API_URL` se ugraduje u build, pa nakon promjene treba redeploy.

### Redoslijed
1. Deploy backend → kopiraj njegov javni URL
2. U frontend servis upiši `VITE_API_URL` = taj URL → deploy
3. Kopiraj frontend URL → u backend `CORS_ORIGINS` → redeploy backend

## Build provjera (lokalno)

```bash
npm run build     # vue-tsc type-check + vite build → dist/
npm run preview   # servira dist/ lokalno
```
