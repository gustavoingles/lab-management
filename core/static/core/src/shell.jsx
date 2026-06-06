// ============================================================
// LabManager — shell (sidebar + topbar) com menu por perfil
// ============================================================

// Cada item: chave de rota, rótulo, ícone e perfis que enxergam.
const NAV_GROUPS = [
  {
    label: null,
    items: [{ key: "dashboard", label: "Início", icon: "layout-dashboard", roles: ["solicitante", "almoxarife", "gestor", "manutencao"] }],
  },
  {
    label: "Catálogo",
    items: [
      { key: "itens", label: "Itens", icon: "package-search", roles: ["solicitante", "almoxarife", "gestor", "manutencao"] },
      { key: "equipamentos", label: "Equipamentos", icon: "cpu", roles: ["solicitante", "almoxarife", "gestor", "manutencao"] },
      { key: "categorias", label: "Categorias", icon: "tags", roles: ["almoxarife", "gestor"] },
    ],
  },
  {
    label: "Estoque",
    items: [
      { key: "estoque", label: "Estoque", icon: "boxes", roles: ["almoxarife", "gestor"] },
      { key: "movimentacoes", label: "Movimentações", icon: "arrow-left-right", roles: ["almoxarife", "gestor"] },
      { key: "localizacoes", label: "Localizações", icon: "map-pin", roles: ["almoxarife", "gestor"] },
    ],
  },
  {
    label: "Operação",
    items: [
      { key: "requisicoes", label: "Requisições", icon: "clipboard-list", roles: ["solicitante", "almoxarife", "gestor"] },
      { key: "reservas", label: "Reservas", icon: "calendar-clock", roles: ["solicitante", "almoxarife", "gestor"] },
    ],
  },
  {
    label: "Manutenção",
    items: [
      { key: "ordens", label: "Ordens de serviço", icon: "wrench", roles: ["gestor", "manutencao"] },
      { key: "manutencoes", label: "Manutenções", icon: "calendar-check", roles: ["gestor", "manutencao"] },
    ],
  },
  {
    label: "Conformidade",
    items: [
      { key: "inventarios", label: "Inventários", icon: "clipboard-check", roles: ["almoxarife", "gestor"] },
      { key: "baixas", label: "Baixas e descarte", icon: "archive-x", roles: ["almoxarife", "gestor"] },
      { key: "auditoria", label: "Auditoria", icon: "history", roles: ["gestor"] },
    ],
  },
  {
    label: "Administração",
    items: [{ key: "usuarios", label: "Usuários", icon: "users", roles: ["gestor"] }],
  },
];

function navForRole(role) {
  return NAV_GROUPS
    .map((g) => ({ ...g, items: g.items.filter((it) => it.roles.includes(role)) }))
    .filter((g) => g.items.length);
}

function Logo({ compact }) {
  return (
    <div className="flex items-center gap-2.5">
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[image:var(--gradient-hero)] text-primary-foreground shadow-[var(--shadow-card)]">
        <Icon name="flask-conical" className="h-5 w-5" />
      </span>
      {!compact && (
        <div className="leading-tight">
          <div className="font-semibold tracking-tight">LabManager</div>
          <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Controle &amp; Manutenção</div>
        </div>
      )}
    </div>
  );
}

function Sidebar({ route, setRoute, role }) {
  const groups = navForRole(role);
  // mapeia rotas de detalhe ao item de menu pai (para manter ativo)
  const parent = { equipamento_detail: "equipamentos", requisicao_detail: "requisicoes", ordem_detail: "ordens", inventario_detail: "inventarios" };
  const active = parent[route] || route;
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card/50 lg:flex">
      <div className="flex h-16 items-center border-b border-border px-5">
        <Logo />
      </div>
      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-5">
        {groups.map((g, gi) => (
          <div key={gi}>
            {g.label && <p className="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/70">{g.label}</p>}
            <div className="space-y-0.5">
              {g.items.map((it) => {
                const on = active === it.key;
                return (
                  <button key={it.key} onClick={() => setRoute(it.key)}
                    className={`group flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors ${on ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"}`}>
                    <Icon name={it.icon} className="h-4 w-4" />
                    <span>{it.label}</span>
                    {on && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary"></span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}

// Troca de perfil (demonstra o menu por perfil)
function RoleSwitcher({ role, setRole }) {
  const [open, setOpen] = React.useState(false);
  const u = USUARIOS[role], p = PERFIS[role];
  return (
    <div className="relative">
      <button onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2.5 rounded-lg border border-border bg-card px-2 py-1.5 text-left transition-colors hover:bg-accent">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">{u.iniciais}</span>
        <span className="hidden leading-tight sm:block">
          <span className="block text-sm font-medium">{u.nome}</span>
          <span className="block text-xs text-muted-foreground">{p.nome}</span>
        </span>
        <Icon name="chevrons-up-down" className="h-4 w-4 text-muted-foreground" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)}></div>
          <div className="absolute right-0 z-40 mt-2 w-64 overflow-hidden rounded-xl border border-border bg-popover shadow-[var(--shadow-elegant)]">
            <p className="border-b border-border px-3 py-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Visualizar como perfil</p>
            {Object.keys(PERFIS).map((k) => {
              const on = k === role;
              return (
                <button key={k} onClick={() => { setRole(k); setOpen(false); }}
                  className={`flex w-full items-center gap-3 px-3 py-2.5 text-left transition-colors hover:bg-accent ${on ? "bg-accent/60" : ""}`}>
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">{USUARIOS[k].iniciais}</span>
                  <span className="leading-tight">
                    <span className="block text-sm font-medium">{PERFIS[k].nome}</span>
                    <span className="block text-xs text-muted-foreground">{PERFIS[k].desc}</span>
                  </span>
                  {on && <Icon name="check" className="ml-auto h-4 w-4 text-primary" />}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function Topbar({ role, setRole, onLogout, pageTitle }) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-background/80 px-4 backdrop-blur lg:px-8">
      <div className="lg:hidden"><Logo compact /></div>
      <div className="relative hidden flex-1 md:block">
        <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input placeholder="Buscar itens, equipamentos, requisições..."
          className="h-9 w-full max-w-md rounded-md border border-input bg-card pl-9 pr-3 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
      </div>
      <div className="ml-auto flex items-center gap-2">
        <button className="relative flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">
          <Icon name="bell" className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-[oklch(0.6_0.2_25)]"></span>
        </button>
        <div className="mx-1 hidden h-6 w-px bg-border sm:block"></div>
        <RoleSwitcher role={role} setRole={setRole} />
      </div>
    </header>
  );
}

Object.assign(window, { Sidebar, Topbar, navForRole, NAV_GROUPS, Logo });
