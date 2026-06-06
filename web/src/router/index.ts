import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { setAuthFailureHandler } from "@/services/api";
import type { Role } from "@/types";

// Prosirujemo meta tipove rute (TypeScript)
declare module "vue-router" {
  interface RouteMeta {
    // 'gost' = layout bez sidebara (login/register), 'aplikacija' = puni layout
    layout?: "gost" | "aplikacija";
    // true ako je ruta javna (ne treba prijavu)
    javno?: boolean;
    // ako je postavljeno, samo te role smiju pristupiti
    uloge?: Role[];
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/auth/LoginView.vue"),
    meta: { layout: "gost", javno: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/auth/RegisterView.vue"),
    meta: { layout: "gost", javno: true },
  },
  {
    path: "/",
    name: "dashboard",
    component: () => import("@/views/DashboardView.vue"),
    meta: { layout: "aplikacija" },
  },
  {
    path: "/trainings",
    name: "trainings",
    component: () => import("@/views/TrainingsView.vue"),
    meta: { layout: "aplikacija" },
  },
  {
    path: "/trainings/:id",
    name: "training-detail",
    component: () => import("@/views/TrainingDetailView.vue"),
    meta: { layout: "aplikacija" },
  },
  {
    path: "/memberships",
    name: "memberships",
    component: () => import("@/views/MembershipsView.vue"),
    meta: { layout: "aplikacija" },
  },
  {
    // Admin-only stranica
    path: "/admin/users",
    name: "admin-users",
    component: () => import("@/views/admin/UsersView.vue"),
    meta: { layout: "aplikacija", uloge: ["admin"] },
  },
  {
    // 404
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/views/NotFoundView.vue"),
    meta: { layout: "aplikacija" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

// --- GLOBALNI GUARD ---
// Trci prije svake navigacije. Provjerava prijavu i role.
router.beforeEach(async (to) => {
  const auth = useAuthStore();

  // Na prvom ucitavanju aplikacije pokusaj povuci korisnika iz spremljenog tokena.
  if (!auth.initialized) {
    await auth.loadUser();
  }

  // Javne rute (login/register): ako je vec prijavljen, salji ga na dashboard.
  if (to.meta.javno) {
    if (auth.isAuthenticated) {
      return { name: "dashboard" };
    }
    return true;
  }

  // Privatne rute: ako nije prijavljen -> login (pamtimo kamo je htio ici).
  if (!auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  // Provjera role: ako ruta trazi odredene role, a korisnik ih nema -> dashboard.
  if (to.meta.uloge && auth.role && !to.meta.uloge.includes(auth.role)) {
    return { name: "dashboard" };
  }

  return true;
});

// Kad interceptor javi da je auth definitivno pao (refresh ne radi),
// odjavi korisnika i posalji na login.
setAuthFailureHandler(() => {
  const auth = useAuthStore();
  auth.logout();
  if (router.currentRoute.value.name !== "login") {
    router.push({
      name: "login",
      query: { redirect: router.currentRoute.value.fullPath },
    });
  }
});

export default router;
