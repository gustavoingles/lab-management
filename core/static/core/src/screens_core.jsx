// ============================================================
// LabManager — telas centrais: Login + Dashboard
// ============================================================

function LoginScreen({ onEnter }) {
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const err = await onEnter(e.target.email.value, e.target.password.value);
    setBusy(false);
    if (err) setError(err);
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Painel de marca */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-[image:var(--gradient-hero)] p-12 text-primary-foreground lg:flex">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)", backgroundSize: "28px 28px" }}></div>
        <div className="relative flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
            <Icon name="flask-conical" className="h-6 w-6" />
          </span>
          <span className="text-lg font-semibold tracking-tight">LabManager</span>
        </div>
        <div className="relative max-w-md">
          <h1 className="text-3xl font-semibold leading-tight tracking-tight">Controle de estoque e manutenção de equipamentos de laboratório</h1>
          <p className="mt-4 text-primary-foreground/80">Rastreabilidade completa de ativos, do cadastro à baixa — itens, reagentes, EPIs, equipamentos, ordens de serviço e inventários, em um só painel.</p>
          <div className="mt-8 flex flex-wrap gap-2">
            {["Catálogo", "Estoque", "Requisições", "Manutenção", "Auditoria"].map((t) => (
              <span key={t} className="rounded-full bg-white/15 px-3 py-1 text-xs font-medium backdrop-blur">{t}</span>
            ))}
          </div>
        </div>
        <p className="relative text-xs text-primary-foreground/70">Universidade de Maceió · Afya — Ciência da Computação · 2026</p>
      </div>

      {/* Formulário */}
      <div className="flex w-full flex-col items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden"><Logo /></div>
          <h2 className="text-2xl font-semibold tracking-tight">Bem-vindo de volta</h2>
          <p className="mt-1 text-sm text-muted-foreground">Entre com sua conta para acessar o painel.</p>
          <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            <Field label="E-mail">
              <Input name="email" type="email" defaultValue="claudia@lab.test" placeholder="voce@laboratorio.com" required />
            </Field>
            <Field label="Senha">
              <Input name="password" type="password" defaultValue="labtest" placeholder="••••••••" required />
            </Field>
            {error && (
              <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
                <Icon name="alert-circle" className="h-4 w-4 shrink-0" />
                {error}
              </div>
            )}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-muted-foreground">
                <input type="checkbox" className="h-4 w-4 rounded border-input accent-[oklch(0.55_0.13_220)]" /> Manter conectado
              </label>
              <a className="text-xs font-medium text-primary hover:underline" href="#">Esqueceu a senha?</a>
            </div>
            <Button type="submit" className="w-full" size="lg" disabled={busy}>
              {busy ? "Entrando…" : "Entrar"}
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Ainda não tem conta? <a className="font-medium text-primary hover:underline" href="#">Cadastre-se</a>
          </p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, tone, hint, hintTone }) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
        </div>
        <span className={`flex h-10 w-10 items-center justify-center rounded-lg ${TONE[tone]}`}>
          <Icon name={icon} className="h-5 w-5" />
        </span>
      </div>
      {hint && <p className={`mt-3 inline-flex items-center gap-1 text-xs ${hintTone === "destructive" ? "text-[oklch(0.55_0.2_25)]" : "text-muted-foreground"}`}>{hint}</p>}
    </Card>
  );
}

function Dashboard({ setRoute, role }) {
  const u = USUARIOS[role];
  const alertas = ESTOQUE.filter((e) => e.abaixoAlerta);
  const acoes = [
    { key: "requisicoes", icon: "clipboard-plus", titulo: "Nova requisição", desc: "Solicitar materiais ao almoxarifado", roles: ["solicitante", "almoxarife", "gestor"] },
    { key: "reservas", icon: "calendar-plus", titulo: "Reservar equipamento", desc: "Agendar uso de equipamento", roles: ["solicitante", "almoxarife", "gestor"] },
    { key: "movimentacoes", icon: "arrow-left-right", titulo: "Movimentar estoque", desc: "Entrada, saída ou transferência", roles: ["almoxarife", "gestor"] },
    { key: "ordens", icon: "wrench", titulo: "Abrir ordem de serviço", desc: "Registrar manutenção de equipamento", roles: ["gestor", "manutencao"] },
  ].filter((a) => a.roles.includes(role));

  return (
    <div>
      <PageHeader title={`Olá, ${u.nome.split(" ")[0]}`} subtitle="Resumo operacional do laboratório · Lab. Bioquímica e Microbiologia" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Itens ativos" value={String(ITENS.length)} icon="package" tone="info" hint="5 categorias" />
        <StatCard label="Requisições em aberto" value={String(REQUISICOES.filter((r) => r.status === "aberta" || r.status === "aprovada").length)} icon="clipboard-list" tone="violet" hint="aguardando aprovação ou atendimento" />
        <StatCard label="Alertas de estoque" value={String(alertas.length)} icon="triangle-alert" tone="destructive" hint="abaixo do nível de alerta" hintTone="destructive" />
        <StatCard label="OS em andamento" value={String(ORDENS.filter((o) => o.status === "aberta" || o.status === "em_execucao").length)} icon="wrench" tone="amber" hint="em aberto ou execução" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Coluna principal */}
        <div className="space-y-6 lg:col-span-2">
          {/* Estoque em alerta */}
          <Card pad={false}>
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h3 className="font-semibold">Estoque em alerta</h3>
              <button onClick={() => setRoute("estoque")} className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                Ver estoque <Icon name="arrow-right" className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="divide-y divide-border">
              {alertas.length === 0 && (
                <p className="px-5 py-4 text-sm text-muted-foreground">Nenhum item abaixo do nível de alerta.</p>
              )}
              {alertas.map((e) => (
                <div key={e.id} className="flex items-center gap-4 px-5 py-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[oklch(0.6_0.2_25_/_0.1)] text-[oklch(0.55_0.2_25)]">
                    <Icon name="triangle-alert" className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{e.item}</p>
                    <p className="text-xs text-muted-foreground">{e.local}</p>
                  </div>
                  <StockBar livre={e.livre} reservado={e.reservado} total={e.total} alerta={e.alerta} />
                  <div className="w-20 text-right">
                    <span className="text-sm font-semibold text-[oklch(0.55_0.2_25)]">{e.livre}</span>
                    <span className="text-xs text-muted-foreground"> / {e.alerta} {e.unidade}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Atividade recente */}
          <Card pad={false}>
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h3 className="font-semibold">Atividade recente</h3>
              {role === "gestor" && (
                <button onClick={() => setRoute("auditoria")} className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                  Auditoria <Icon name="arrow-right" className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
            <div className="px-5 py-2">
              {AUDITORIA.slice(0, 5).map((a) => (
                <div key={a.id} className="flex items-center gap-3 py-2.5">
                  <span className={`flex h-8 w-8 items-center justify-center rounded-full ${TONE[a.tone]}`}><Icon name={a.icon} className="h-4 w-4" /></span>
                  <p className="flex-1 text-sm">
                    <span className="font-medium">{a.quem}</span> <span className="text-muted-foreground">{a.acao}</span> <span className="font-medium">{a.alvo}</span>
                  </p>
                  <span className="text-xs text-muted-foreground">{a.quando}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Coluna lateral */}
        <div className="space-y-6">
          <Card pad={false}>
            <h3 className="border-b border-border px-5 py-4 font-semibold">Ações rápidas</h3>
            <div className="p-3">
              {acoes.map((a) => (
                <button key={a.key} onClick={() => setRoute(a.key)}
                  className="group flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left transition-colors hover:bg-accent">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary"><Icon name={a.icon} className="h-4 w-4" /></span>
                  <span className="flex-1">
                    <span className="block text-sm font-medium">{a.titulo}</span>
                    <span className="block text-xs text-muted-foreground">{a.desc}</span>
                  </span>
                  <Icon name="chevron-right" className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                </button>
              ))}
            </div>
          </Card>

          <Card pad={false}>
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <h3 className="font-semibold">Manutenções a vencer</h3>
            </div>
            <div className="divide-y divide-border">
              {MANUTENCOES.filter((m) => m.proximo !== "—").map((m) => (
                <div key={m.id} className="flex items-center gap-3 px-5 py-3">
                  <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${m.vencida ? TONE.destructive : TONE.neutral}`}>
                    <Icon name={m.vencida ? "alarm-clock" : "calendar"} className="h-4 w-4" />
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{m.equipamento}</p>
                    <p className="text-xs text-muted-foreground">{TIPO_MAN[m.tipo].label}</p>
                  </div>
                  <span className={`text-xs font-medium ${m.vencida ? "text-[oklch(0.55_0.2_25)]" : "text-muted-foreground"}`}>{m.proximo}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { LoginScreen, Dashboard });
