// ============================================================
// LabManager — Requisições, Reservas, OS, Inventário, Auditoria
// ============================================================

function RequisicoesScreen({ setRoute, setSel, role }) {
  const minhas = role === "solicitante";
  const lista = minhas ? REQUISICOES.filter((r) => r.solicitante === USUARIOS.solicitante.nome) : REQUISICOES;
  return (
    <div>
      <PageHeader title="Requisições" subtitle={minhas ? "Suas solicitações de material ao almoxarifado." : "Solicitações de material — aprovação reserva o estoque automaticamente."}>
        <Button icon="plus">Nova requisição</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Nº" }, { label: "Finalidade" }, { label: "Solicitante" }, { label: "Itens", align: "right" }, { label: "Status" }, { label: "Criada" }, { label: "", align: "right" }]}>
        {lista.map((r) => (
          <Row key={r.id} onClick={() => { setSel(r.id); setRoute("requisicao_detail"); }}>
            <td className="px-4 py-3 font-mono text-xs font-medium">#{r.id}</td>
            <td className="px-4 py-3 font-medium">{r.finalidade}</td>
            <td className="px-4 py-3 text-muted-foreground">{r.solicitante}</td>
            <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">{r.itens.length || "—"}</td>
            <td className="px-4 py-3"><StatusBadge map={STATUS_REQ} value={r.status} /></td>
            <td className="px-4 py-3 text-xs text-muted-foreground">{r.criada}</td>
            <td className="px-4 py-3 text-right"><Icon name="chevron-right" className="h-4 w-4 text-muted-foreground" /></td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

const REQ_STEPS = [
  { key: "aberta", label: "Aberta", icon: "file-plus" },
  { key: "aprovada", label: "Aprovada", icon: "check-check" },
  { key: "atendida", label: "Atendida", icon: "package-check" },
];

function RequisicaoDetail({ id, setRoute, role }) {
  const base = REQUISICOES.find((r) => r.id === id) || REQUISICOES[0];
  const [req, setReq] = React.useState(() => JSON.parse(JSON.stringify(base)));
  const [toast, setToast] = React.useState(null);
  const podeAprovar = role === "gestor";
  const podeAtender = role === "almoxarife" || role === "gestor";

  React.useEffect(() => { if (window.lucide) window.lucide.createIcons(); });

  function flash(msg) { setToast(msg); setTimeout(() => setToast(null), 2600); }

  function aprovar() {
    setReq((r) => ({
      ...r, status: "aprovada",
      itens: r.itens.map((it) => ({ ...it, aprovado: it.solicitado, reserva: it.localOpcoes[0] })),
    }));
    flash("Requisição aprovada — estoque reservado nas localizações com saldo livre.");
  }
  function rejeitar() { setReq((r) => ({ ...r, status: "rejeitada" })); flash("Requisição rejeitada."); }
  function atender(itemId) {
    setReq((r) => {
      const itens = r.itens.map((it) => it.id === itemId ? { ...it, atendido: it.aprovado } : it);
      const todos = itens.every((it) => it.atendido != null);
      return { ...r, itens, status: todos ? "atendida" : r.status };
    });
    flash("Item atendido — baixa física registrada na localização reservada.");
  }

  const stepIdx = { aberta: 0, em_aprovacao: 0, aprovada: 1, atendida: 2 }[req.status] ?? 0;
  const encerrada = req.status === "rejeitada" || req.status === "cancelada";

  return (
    <div className="relative">
      <PageHeader breadcrumb={["Requisições", `#${req.id}`]} title={`Requisição #${req.id}`}
        subtitle={`${req.solicitante} · criada em ${req.criada}`}>
        <StatusBadge map={STATUS_REQ} value={req.status} />
      </PageHeader>

      {/* Stepper */}
      {!encerrada && (
        <Card className="mb-6">
          <div className="flex items-center">
            {REQ_STEPS.map((s, i) => {
              const done = i < stepIdx, cur = i === stepIdx;
              return (
                <React.Fragment key={s.key}>
                  <div className="flex items-center gap-3">
                    <span className={`flex h-9 w-9 items-center justify-center rounded-full ${done ? "bg-primary text-primary-foreground" : cur ? "bg-primary/15 text-primary ring-2 ring-primary/30" : "bg-muted text-muted-foreground"}`}>
                      <Icon name={done ? "check" : s.icon} className="h-4 w-4" />
                    </span>
                    <span className={`text-sm ${cur || done ? "font-semibold" : "text-muted-foreground"}`}>{s.label}</span>
                  </div>
                  {i < REQ_STEPS.length - 1 && <div className={`mx-3 h-0.5 flex-1 rounded ${i < stepIdx ? "bg-primary" : "bg-border"}`}></div>}
                </React.Fragment>
              );
            })}
          </div>
        </Card>
      )}

      {/* Resumo horizontal */}
      <Card className="mb-6">
        <div className="grid gap-5 sm:grid-cols-4">
          <div><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Solicitante</p><p className="mt-1 text-sm font-medium">{req.solicitante}</p></div>
          <div><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Criada em</p><p className="mt-1 text-sm font-medium">{req.criada}</p></div>
          <div><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Itens</p><p className="mt-1 text-sm font-medium">{req.itens.length}</p></div>
          <div><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Status</p><p className="mt-1"><StatusBadge map={STATUS_REQ} value={req.status} /></p></div>
        </div>
        <div className="mt-5 border-t border-border pt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Finalidade</p>
          <p className="mt-1 text-sm">{req.finalidade}{req.justificativa && <span className="text-muted-foreground"> — {req.justificativa}</span>}</p>
        </div>
      </Card>

      {/* Ações do gestor */}
      {podeAprovar && (req.status === "aberta" || req.status === "em_aprovacao") && (
        <div className="mb-6 flex flex-wrap items-center gap-3 rounded-xl border border-primary/30 bg-primary/[0.04] p-4">
          <div className="flex items-center gap-2 text-sm font-medium"><Icon name="gavel" className="h-4 w-4 text-primary" />Aguardando sua decisão</div>
          <div className="ml-auto flex gap-2">
            <Button variant="destructive" size="sm" icon="x" onClick={rejeitar}>Rejeitar</Button>
            <Button size="sm" icon="check-check" onClick={aprovar}>Aprovar e reservar estoque</Button>
          </div>
        </div>
      )}
      {req.status === "aprovada" && podeAtender && (
        <div className="mb-6 flex items-center gap-2 rounded-xl border border-[oklch(0.55_0.15_290_/_0.3)] bg-[oklch(0.55_0.15_290_/_0.05)] p-4 text-sm">
          <Icon name="package-check" className="h-4 w-4 text-[oklch(0.45_0.16_290)]" />
          Estoque reservado. Atenda cada linha na localização reservada para dar baixa física.
        </div>
      )}

      {/* Itens */}
      <Card pad={false}>
        <h3 className="border-b border-border px-5 py-4 font-semibold">Itens da requisição</h3>
        <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/40 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <th className="px-5 py-2.5">Item</th><th className="px-5 py-2.5 text-right">Solicitado</th>
                  <th className="px-5 py-2.5 text-right">Aprovado</th><th className="px-5 py-2.5">Reserva</th>
                  <th className="px-5 py-2.5 text-right">Atendido</th><th className="px-5 py-2.5"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {req.itens.map((it) => (
                  <tr key={it.id}>
                    <td className="px-5 py-3 font-medium">{it.item}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{it.solicitado} <span className="text-xs text-muted-foreground">{it.unidade}</span></td>
                    <td className="px-5 py-3 text-right tabular-nums">{it.aprovado ?? "—"}</td>
                    <td className="px-5 py-3">{it.reserva ? <Badge tone="amber" dot>{it.reserva}</Badge> : <span className="text-muted-foreground">—</span>}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{it.atendido != null ? <span className="font-medium text-[oklch(0.42_0.12_158)]">{it.atendido}</span> : "—"}</td>
                    <td className="px-5 py-3 text-right">
                      {req.status === "aprovada" && podeAtender && it.atendido == null
                        ? <Button size="sm" variant="outline" icon="check" onClick={() => atender(it.id)}>Atender</Button>
                        : it.atendido != null ? <Icon name="circle-check" className="ml-auto h-4 w-4 text-[oklch(0.6_0.13_155)]" /> : null}
                    </td>
                  </tr>
                ))}
                {req.itens.length === 0 && <tr><td colSpan="6" className="px-5 py-8 text-center text-muted-foreground">Sem itens nesta requisição.</td></tr>}
              </tbody>
            </table>
            </div>
      </Card>

      {toast && (
        <div className="fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 items-center gap-2.5 rounded-lg border border-border bg-popover px-4 py-3 text-sm shadow-[var(--shadow-elegant)]">
          <Icon name="circle-check" className="h-4 w-4 text-[oklch(0.6_0.13_155)]" />{toast}
        </div>
      )}
    </div>
  );
}

function ReservasScreen({ role }) {
  return (
    <div>
      <PageHeader title="Reservas de equipamento" subtitle="Agendamento de uso. Horários sobrepostos para o mesmo equipamento são bloqueados.">
        <Button icon="plus">Nova reserva</Button>
      </PageHeader>

      <div className="mb-5 flex items-start gap-3 rounded-xl border border-[oklch(0.78_0.14_75_/_0.3)] bg-[oklch(0.78_0.14_75_/_0.07)] px-4 py-3 text-sm">
        <Icon name="triangle-alert" className="mt-0.5 h-4 w-4 text-[oklch(0.5_0.12_60)]" />
        <p><strong>Conflito de horário:</strong> a nova reserva do Microscópio MIC-2021-0098 às 06/06 14:00–16:00 sobrepõe uma reserva existente. Escolha outro horário ou equipamento.</p>
      </div>

      <DataTable columns={[{ label: "Equipamento" }, { label: "Solicitante" }, { label: "Início" }, { label: "Fim" }, { label: "Finalidade" }, { label: "Status" }, ...(role === "gestor" ? [{ label: "", align: "right" }] : [])]}>
        {RESERVAS.map((r) => (
          <Row key={r.id}>
            <td className="px-4 py-3"><div className="font-medium">{r.equipamento}</div><div className="font-mono text-[11px] text-muted-foreground">{r.serie}</div></td>
            <td className="px-4 py-3 text-muted-foreground">{r.solicitante}</td>
            <td className="px-4 py-3 tabular-nums">{r.inicio}</td>
            <td className="px-4 py-3 tabular-nums">{r.fim}</td>
            <td className="px-4 py-3 text-muted-foreground">{r.finalidade}</td>
            <td className="px-4 py-3"><StatusBadge map={STATUS_RESERVA} value={r.status} /></td>
            {role === "gestor" && <td className="px-4 py-3 text-right">{r.status === "pendente" ? <Button size="sm" variant="outline" icon="check">Confirmar</Button> : null}</td>}
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function OrdensScreen({ setRoute, setSel }) {
  return (
    <div>
      <PageHeader title="Ordens de serviço" subtitle="Fluxo: abrir → iniciar → encerrar. Cada OS guarda histórico de manutenções por equipamento.">
        <Button icon="plus">Nova OS</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Nº" }, { label: "Equipamento" }, { label: "Problema" }, { label: "Prioridade" }, { label: "Status" }, { label: "Aberta" }, { label: "", align: "right" }]}>
        {ORDENS.map((o) => (
          <Row key={o.id} onClick={() => { setSel(o.id); setRoute("ordem_detail"); }}>
            <td className="px-4 py-3 font-mono text-xs font-medium">#{o.id}</td>
            <td className="px-4 py-3"><div className="font-medium">{o.equipamento}</div><div className="font-mono text-[11px] text-muted-foreground">{o.serie}</div></td>
            <td className="px-4 py-3 max-w-xs truncate text-muted-foreground">{o.problema}</td>
            <td className="px-4 py-3"><StatusBadge map={PRIORIDADE} value={o.prioridade} dot /></td>
            <td className="px-4 py-3"><StatusBadge map={STATUS_OS} value={o.status} /></td>
            <td className="px-4 py-3 text-xs text-muted-foreground">{o.abertura}</td>
            <td className="px-4 py-3 text-right"><Icon name="chevron-right" className="h-4 w-4 text-muted-foreground" /></td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function OrdemDetail({ id, setRoute, role }) {
  const o = ORDENS.find((x) => x.id === id) || ORDENS[0];
  const podeMan = role === "gestor" || role === "manutencao";
  return (
    <div>
      <PageHeader breadcrumb={["Ordens de serviço", `#${o.id}`]} title={`Ordem de serviço #${o.id}`}
        subtitle={`${o.equipamento} · ${o.serie}`}>
        {o.status === "aberta" && podeMan && <Button variant="outline" icon="play">Iniciar</Button>}
        {o.status === "em_execucao" && podeMan && <Button variant="outline" icon="check">Encerrar</Button>}
        {podeMan && <Button icon="plus">Registrar manutenção</Button>}
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge map={STATUS_OS} value={o.status} />
              <StatusBadge map={PRIORIDADE} value={o.prioridade} dot />
              <span className="text-xs text-muted-foreground">Aberta em {o.abertura}</span>
            </div>
            <div className="mt-4 space-y-3 text-sm">
              <div><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Problema relatado</p><p className="mt-1">{o.problema}</p></div>
            </div>
          </Card>
          <Card pad={false}>
            <h3 className="border-b border-border px-5 py-4 font-semibold">Manutenções da OS</h3>
            {o.id === 205 ? (
              <table className="w-full text-sm"><tbody className="divide-y divide-border">
                {MANUTENCOES_OS.map((m) => (
                  <tr key={m.id}>
                    <td className="px-5 py-3"><StatusBadge map={TIPO_MAN} value={m.tipo} dot /></td>
                    <td className="px-5 py-3 text-muted-foreground">{m.obs}</td>
                    <td className="px-5 py-3 text-right text-xs text-muted-foreground">Realizada: {m.realizada}</td>
                  </tr>
                ))}
              </tbody></table>
            ) : <EmptyState icon="calendar-check" title="Nenhuma manutenção registrada" >Use "Registrar manutenção" para adicionar preventiva ou corretiva.</EmptyState>}
          </Card>
        </div>
        <div className="space-y-6">
          <Card>
            <h3 className="font-semibold">Detalhes</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <InfoRow label="Equipamento" value={o.equipamento} />
              <InfoRow label="Série" value={<span className="font-mono text-xs">{o.serie}</span>} />
              <InfoRow label="Responsável" value={o.responsavel} />
              <InfoRow label="Prioridade" value={<StatusBadge map={PRIORIDADE} value={o.prioridade} dot />} />
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
}

function ManutencoesScreen() {
  return (
    <div>
      <PageHeader title="Manutenções" subtitle="Visão global de manutenções preventivas, corretivas e calibrações." />
      <DataTable columns={[{ label: "Equipamento" }, { label: "Tipo" }, { label: "Realizada" }, { label: "Próx. vencimento" }, { label: "OS" }]}>
        {MANUTENCOES.map((m) => (
          <Row key={m.id} highlight={m.vencida}>
            <td className="px-4 py-3 font-medium">{m.equipamento}</td>
            <td className="px-4 py-3"><StatusBadge map={TIPO_MAN} value={m.tipo} dot /></td>
            <td className="px-4 py-3 text-muted-foreground">{m.realizada}</td>
            <td className="px-4 py-3">{m.vencida ? <span className="inline-flex items-center gap-1.5 font-medium text-[oklch(0.55_0.2_25)]"><Icon name="alarm-clock" className="h-3.5 w-3.5" />{m.proximo} (vencida)</span> : <span className="text-muted-foreground">{m.proximo}</span>}</td>
            <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{m.os ? `#${m.os}` : "—"}</td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function InventariosScreen({ setRoute, setSel }) {
  return (
    <div>
      <PageHeader title="Inventários" subtitle="Contagens físicas periódicas comparadas ao saldo do sistema.">
        <Button icon="plus">Novo inventário</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Inventário" }, { label: "Localização" }, { label: "Status" }, { label: "Linhas", align: "right" }, { label: "Divergências", align: "right" }, { label: "Responsável" }, { label: "", align: "right" }]}>
        {INVENTARIOS.map((iv) => (
          <Row key={iv.id} onClick={() => { setSel(iv.id); setRoute("inventario_detail"); }}>
            <td className="px-4 py-3 font-mono text-xs font-medium">{iv.id}</td>
            <td className="px-4 py-3 font-medium">{iv.local}</td>
            <td className="px-4 py-3"><StatusBadge map={STATUS_INV} value={iv.status} /></td>
            <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">{iv.linhas}</td>
            <td className="px-4 py-3 text-right">{iv.divergencias > 0 ? <Badge tone="amber">{iv.divergencias}</Badge> : <Badge tone="success">0</Badge>}</td>
            <td className="px-4 py-3 text-muted-foreground">{iv.responsavel}</td>
            <td className="px-4 py-3 text-right"><Icon name="chevron-right" className="h-4 w-4 text-muted-foreground" /></td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function InventarioDetail({ id, setRoute }) {
  const iv = INVENTARIOS.find((x) => x.id === id) || INVENTARIOS[0];
  return (
    <div>
      <PageHeader breadcrumb={["Inventários", iv.id]} title={iv.id} subtitle={`${iv.local} · responsável ${iv.responsavel}`}>
        <StatusBadge map={STATUS_INV} value={iv.status} />
        <Button variant="outline" icon="download">Exportar</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Item" }, { label: "Localização" }, { label: "Sistema", align: "right" }, { label: "Contado", align: "right" }, { label: "Diferença", align: "right" }]}>
        {INVENTARIO_LINHAS.map((l) => (
          <Row key={l.id} highlight={l.diff !== 0}>
            <td className="px-4 py-3 font-medium">{l.item}</td>
            <td className="px-4 py-3 text-muted-foreground">{l.local}</td>
            <td className="px-4 py-3 text-right tabular-nums">{l.sistema}</td>
            <td className="px-4 py-3 text-right tabular-nums">{l.contado}</td>
            <td className="px-4 py-3 text-right">
              {l.diff === 0 ? <span className="text-muted-foreground">0</span>
                : <span className={`font-semibold tabular-nums ${l.diff > 0 ? "text-[oklch(0.42_0.12_158)]" : "text-[oklch(0.55_0.2_25)]"}`}>{l.diff > 0 ? "+" : ""}{l.diff}</span>}
            </td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function BaixasScreen() {
  const tipos = { descarte: "Descarte", baixa: "Baixa", perda: "Perda", obsolescencia: "Obsolescência", avaria_irrecuperavel: "Avaria irrecuperável" };
  const dados = [
    { id: 1, alvo: "Solução de Lugol (50 mL)", tipo: "descarte", motivo: "Validade expirada", data: "02/06/2026", por: "Cláudia Souza" },
    { id: 2, alvo: "Microscópio MIC-2017-0044", tipo: "obsolescencia", motivo: "Equipamento obsoleto, sem peças", data: "20/05/2026", por: "Cláudia Souza" },
  ];
  return (
    <div>
      <PageHeader title="Baixas e descarte" subtitle="Registro de descartes e baixas conforme normas, com motivo e responsável.">
        <Button icon="plus">Nova baixa</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Item / Equipamento" }, { label: "Tipo" }, { label: "Motivo" }, { label: "Data" }, { label: "Responsável" }]}>
        {dados.map((d) => (
          <Row key={d.id}>
            <td className="px-4 py-3 font-medium">{d.alvo}</td>
            <td className="px-4 py-3"><Badge tone="destructive" dot>{tipos[d.tipo]}</Badge></td>
            <td className="px-4 py-3 text-muted-foreground">{d.motivo}</td>
            <td className="px-4 py-3 text-xs text-muted-foreground">{d.data}</td>
            <td className="px-4 py-3 text-muted-foreground">{d.por}</td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function AuditoriaScreen() {
  return (
    <div>
      <PageHeader title="Auditoria" subtitle="Trilha automática de ações — quem fez o quê e quando." />
      <Card pad={false}>
        <div className="px-5">
          {AUDITORIA.map((a, i) => (
            <div key={a.id} className="flex gap-4 py-4">
              <div className="flex flex-col items-center">
                <span className={`flex h-9 w-9 items-center justify-center rounded-full ${TONE[a.tone]}`}><Icon name={a.icon} className="h-4 w-4" /></span>
                {i < AUDITORIA.length - 1 && <span className="mt-1 w-px flex-1 bg-border"></span>}
              </div>
              <div className="flex-1 pb-1">
                <p className="text-sm"><span className="font-medium">{a.quem}</span> <span className="text-muted-foreground">{a.acao}</span> <span className="font-medium">{a.alvo}</span></p>
                <p className="mt-0.5 text-xs text-muted-foreground">{a.perfil} · {a.quando}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function UsuariosScreen() {
  const users = [
    { nome: "Cláudia Souza", email: "claudia@lab.test", perfil: "Gestor", tone: "violet", ativo: true },
    { nome: "Renato Lima", email: "renato@lab.test", perfil: "Almoxarife", tone: "info", ativo: true },
    { nome: "Marina Alves", email: "marina@lab.test", perfil: "Solicitante", tone: "neutral", ativo: true },
    { nome: "Iuri Mendes", email: "iuri@lab.test", perfil: "Téc. manutenção", tone: "amber", ativo: true },
    { nome: "João Pereira", email: "joao@lab.test", perfil: "Solicitante", tone: "neutral", ativo: true },
    { nome: "Ana Costa", email: "ana@lab.test", perfil: "Solicitante", tone: "neutral", ativo: false },
  ];
  return (
    <div>
      <PageHeader title="Usuários" subtitle="Gestão de contas e perfis. Apenas Admin promove outro usuário a Admin.">
        <Button variant="outline" icon="user-cog">Solicitações de perfil</Button>
        <Button icon="user-plus">Novo usuário</Button>
      </PageHeader>
      <DataTable columns={[{ label: "Usuário" }, { label: "E-mail" }, { label: "Perfil" }, { label: "Situação" }, { label: "", align: "right" }]}>
        {users.map((u, i) => (
          <Row key={i}>
            <td className="px-4 py-3"><span className="inline-flex items-center gap-2.5"><span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">{u.nome.split(" ").map((n) => n[0]).join("").slice(0, 2)}</span><span className="font-medium">{u.nome}</span></span></td>
            <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{u.email}</td>
            <td className="px-4 py-3"><Badge tone={u.tone} dot>{u.perfil}</Badge></td>
            <td className="px-4 py-3">{u.ativo ? <Badge tone="success" dot>Ativo</Badge> : <Badge tone="neutral" dot>Inativo</Badge>}</td>
            <td className="px-4 py-3 text-right"><button className="text-xs font-medium text-primary hover:underline">Editar</button></td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

Object.assign(window, { RequisicoesScreen, RequisicaoDetail, ReservasScreen, OrdensScreen, OrdemDetail, ManutencoesScreen, InventariosScreen, InventarioDetail, BaixasScreen, AuditoriaScreen, UsuariosScreen });
