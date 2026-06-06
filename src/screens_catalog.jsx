// ============================================================
// LabManager — Catálogo, Estoque e Movimentações
// ============================================================

function ItensScreen({ pode }) {
  const [tipo, setTipo] = React.useState("");
  const [q, setQ] = React.useState("");
  const itens = ITENS.filter((i) => (!tipo || i.tipo === tipo) && (!q || (i.nome + i.codigo).toLowerCase().includes(q.toLowerCase())));
  return (
    <div>
      <PageHeader title="Itens" subtitle="Catálogo de tudo que o laboratório possui — equipamentos, reagentes, consumíveis, EPIs e peças.">
        <Button variant="outline" icon="tags">Categorias</Button>
        {pode && <Button icon="plus">Novo item</Button>}
      </PageHeader>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <SearchBox value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar por nome ou código..." />
        <div className="flex flex-wrap gap-1.5">
          <FilterChip active={tipo === ""} onClick={() => setTipo("")}>Todos</FilterChip>
          {Object.entries(TIPOS_ITEM).map(([k, v]) => (
            <FilterChip key={k} active={tipo === k} onClick={() => setTipo(k)} icon={v.icon}>{v.label}</FilterChip>
          ))}
        </div>
      </div>

      <DataTable columns={[
        { label: "Código" }, { label: "Nome" }, { label: "Tipo" }, { label: "Categoria" },
        { label: "Unidade" }, { label: "Controlado" }, ...(pode ? [{ label: "", align: "right" }] : []),
      ]}>
        {itens.map((i) => {
          const t = TIPOS_ITEM[i.tipo];
          return (
            <Row key={i.id}>
              <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{i.codigo}</td>
              <td className="px-4 py-3 font-medium">{i.nome}</td>
              <td className="px-4 py-3"><Badge tone={t.tone} dot>{t.label}</Badge></td>
              <td className="px-4 py-3 text-muted-foreground">{i.categoria}</td>
              <td className="px-4 py-3 text-muted-foreground">{i.unidade}</td>
              <td className="px-4 py-3">{i.controlado ? <Badge tone="amber" dot>Controlado</Badge> : <span className="text-muted-foreground">—</span>}</td>
              {pode && <td className="px-4 py-3 text-right"><RowActions /></td>}
            </Row>
          );
        })}
      </DataTable>
      <p className="mt-3 text-xs text-muted-foreground">{itens.length} {itens.length === 1 ? "item" : "itens"}</p>
    </div>
  );
}

function FilterChip({ active, onClick, children, icon }) {
  return (
    <button onClick={onClick}
      className={`inline-flex h-8 items-center gap-1.5 rounded-md border px-3 text-xs font-medium transition-colors ${active ? "border-primary bg-primary/10 text-primary" : "border-input bg-card text-muted-foreground hover:bg-accent hover:text-foreground"}`}>
      {icon && <Icon name={icon} className="h-3.5 w-3.5" />}{children}
    </button>
  );
}

function RowActions() {
  return (
    <div className="flex items-center justify-end gap-1">
      <button className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><Icon name="pencil" className="h-3.5 w-3.5" /></button>
      <button className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive"><Icon name="trash-2" className="h-3.5 w-3.5" /></button>
    </div>
  );
}

function EquipamentosScreen({ setRoute, setSel, pode }) {
  return (
    <div>
      <PageHeader title="Equipamentos" subtitle="Ativos rastreáveis por número de série e tombamento, com ciclo de vida operacional.">
        {pode && <Button icon="plus">Novo equipamento</Button>}
      </PageHeader>
      <DataTable columns={[{ label: "Série / Tombamento" }, { label: "Equipamento" }, { label: "Localização" }, { label: "Estado" }, { label: "Próx. manutenção" }, { label: "", align: "right" }]}>
        {EQUIPAMENTOS.map((e) => (
          <Row key={e.id} onClick={() => { setSel(e.id); setRoute("equipamento_detail"); }}>
            <td className="px-4 py-3">
              <div className="font-mono text-xs font-medium">{e.serie}</div>
              <div className="font-mono text-[11px] text-muted-foreground">{e.tombamento}</div>
            </td>
            <td className="px-4 py-3 font-medium">{e.item}</td>
            <td className="px-4 py-3 text-muted-foreground">{e.local}</td>
            <td className="px-4 py-3"><StatusBadge map={STATUS_OP} value={e.status} /></td>
            <td className="px-4 py-3 text-muted-foreground">{e.proxManut}</td>
            <td className="px-4 py-3 text-right"><Icon name="chevron-right" className="h-4 w-4 text-muted-foreground" /></td>
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

const CICLO_VIDA = ["ativo", "em_manutencao", "inativo", "descartado"];

function EquipamentoDetail({ id, setRoute, pode }) {
  const e = EQUIPAMENTOS.find((x) => x.id === id) || EQUIPAMENTOS[0];
  const reservas = RESERVAS.filter((r) => r.serie === e.serie);
  const ordens = ORDENS.filter((o) => o.serie === e.serie);
  const idxAtual = CICLO_VIDA.indexOf(e.status);
  return (
    <div>
      <PageHeader breadcrumb={["Equipamentos", e.serie]} title={e.item}
        subtitle={`Série ${e.serie} · Tombamento ${e.tombamento}`}>
        {pode && <Button variant="outline" icon="wrench" onClick={() => setRoute("ordens")}>Abrir OS</Button>}
        {pode && <Button variant="outline" icon="settings-2">Alterar estado</Button>}
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Ciclo de vida */}
          <Card>
            <h3 className="font-semibold">Ciclo de vida operacional</h3>
            <div className="mt-5 flex items-center">
              {CICLO_VIDA.map((s, i) => {
                const past = i <= idxAtual;
                const cur = i === idxAtual;
                const t = STATUS_OP[s];
                return (
                  <React.Fragment key={s}>
                    <div className="flex flex-col items-center gap-2">
                      <span className={`flex h-10 w-10 items-center justify-center rounded-full ${cur ? TONE[t.tone] : past ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}>
                        <Icon name={t.icon} className="h-4 w-4" />
                      </span>
                      <span className={`text-xs ${cur ? "font-semibold" : "text-muted-foreground"}`}>{t.label}</span>
                    </div>
                    {i < CICLO_VIDA.length - 1 && <div className={`mx-1 h-0.5 flex-1 ${i < idxAtual ? "bg-primary/40" : "bg-border"}`}></div>}
                  </React.Fragment>
                );
              })}
            </div>
            {e.status === "em_manutencao" && (
              <div className="mt-5 flex items-start gap-3 rounded-lg border border-[oklch(0.78_0.14_75_/_0.3)] bg-[oklch(0.78_0.14_75_/_0.08)] px-4 py-3 text-sm">
                <Icon name="wrench" className="mt-0.5 h-4 w-4 text-[oklch(0.5_0.12_60)]" />
                <p>Equipamento <strong>em manutenção</strong> — OS #205 em execução. Indisponível para reservas.</p>
              </div>
            )}
          </Card>

          {/* Ordens de serviço */}
          <Card pad={false}>
            <h3 className="border-b border-border px-5 py-4 font-semibold">Histórico de ordens de serviço</h3>
            {ordens.length ? (
              <table className="w-full text-sm">
                <tbody className="divide-y divide-border">
                  {ordens.map((o) => (
                    <tr key={o.id} className="cursor-pointer hover:bg-muted/40" onClick={() => setRoute("ordens")}>
                      <td className="px-5 py-3 font-mono text-xs text-muted-foreground">OS #{o.id}</td>
                      <td className="px-5 py-3">{o.problema}</td>
                      <td className="px-5 py-3"><StatusBadge map={STATUS_OS} value={o.status} /></td>
                      <td className="px-5 py-3 text-right text-xs text-muted-foreground">{o.abertura}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <EmptyState icon="wrench" title="Sem ordens de serviço" />}
          </Card>
        </div>

        {/* Ficha técnica */}
        <div className="space-y-6">
          <Card>
            <h3 className="font-semibold">Ficha técnica</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <InfoRow label="Estado" value={<StatusBadge map={STATUS_OP} value={e.status} />} />
              <InfoRow label="Localização" value={e.local} />
              <InfoRow label="Nº de série" value={<span className="font-mono text-xs">{e.serie}</span>} />
              <InfoRow label="Tombamento" value={<span className="font-mono text-xs">{e.tombamento}</span>} />
              <InfoRow label="Aquisição" value={e.aquisicao.split("-").reverse().join("/")} />
              <InfoRow label="Próx. manutenção" value={e.proxManut} />
            </dl>
          </Card>
          <Card pad={false}>
            <h3 className="border-b border-border px-5 py-4 font-semibold">Reservas</h3>
            {reservas.length ? (
              <div className="divide-y divide-border">
                {reservas.map((r) => (
                  <div key={r.id} className="px-5 py-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{r.inicio} → {r.fim}</p>
                      <StatusBadge map={STATUS_RESERVA} value={r.status} />
                    </div>
                    <p className="mt-0.5 text-xs text-muted-foreground">{r.solicitante} · {r.finalidade}</p>
                  </div>
                ))}
              </div>
            ) : <div className="px-5 py-6 text-center text-sm text-muted-foreground">Sem reservas</div>}
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

function EstoqueScreen({ pode }) {
  const alertas = ESTOQUE.filter((e) => e.abaixoAlerta);
  return (
    <div>
      <PageHeader title="Estoque" subtitle="Saldos por item e localização. Reservado fica bloqueado para requisições aprovadas; Livre é o que pode ser usado.">
        {pode && <Button icon="arrow-left-right">Nova movimentação</Button>}
      </PageHeader>

      {alertas.length > 0 && (
        <div className="mb-5 rounded-xl border border-[oklch(0.6_0.2_25_/_0.3)] bg-[oklch(0.6_0.2_25_/_0.06)] p-4">
          <div className="flex items-center gap-2 font-medium text-[oklch(0.5_0.2_25)]">
            <Icon name="triangle-alert" className="h-4 w-4" /> {alertas.length} {alertas.length === 1 ? "item abaixo" : "itens abaixo"} do nível de alerta
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{alertas.map((a) => a.item).join(", ")} — considere repor o estoque.</p>
        </div>
      )}

      <DataTable columns={[
        { label: "Item" }, { label: "Localização" }, { label: "Total", align: "right" },
        { label: "Reservado", align: "right" }, { label: "Livre", align: "right" }, { label: "Nível" }, ...(pode ? [{ label: "", align: "right" }] : []),
      ]}>
        {ESTOQUE.map((e) => (
          <Row key={e.id} highlight={e.abaixoAlerta}>
            <td className="px-4 py-3">
              <div className="font-medium">{e.item}</div>
              <div className="font-mono text-[11px] text-muted-foreground">{e.codigo}</div>
            </td>
            <td className="px-4 py-3 text-muted-foreground">{e.local}</td>
            <td className="px-4 py-3 text-right tabular-nums">{e.total} <span className="text-xs text-muted-foreground">{e.unidade}</span></td>
            <td className="px-4 py-3 text-right tabular-nums text-[oklch(0.5_0.12_60)]">{e.reservado || "—"}</td>
            <td className="px-4 py-3 text-right">
              <span className={`font-semibold tabular-nums ${e.abaixoAlerta ? "text-[oklch(0.55_0.2_25)]" : ""}`}>{e.livre}</span>
            </td>
            <td className="px-4 py-3">
              <div className="flex items-center gap-2">
                <StockBar livre={e.livre} reservado={e.reservado} total={e.total} alerta={e.alerta} />
                {e.abaixoAlerta && <Badge tone="destructive">Baixo</Badge>}
              </div>
            </td>
            {pode && <td className="px-4 py-3 text-right"><button className="text-xs font-medium text-primary hover:underline">Níveis</button></td>}
          </Row>
        ))}
      </DataTable>
      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-[oklch(0.6_0.13_155)]"></span> Livre</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-[oklch(0.78_0.14_75)]"></span> Reservado</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-[oklch(0.6_0.2_25)]"></span> Abaixo do alerta</span>
      </div>
    </div>
  );
}

function MovimentacoesScreen({ pode }) {
  return (
    <div>
      <PageHeader title="Movimentações" subtitle="Histórico de entradas, saídas, transferências e ajustes de estoque.">
        {pode && <Button icon="plus">Nova movimentação</Button>}
      </PageHeader>
      <DataTable columns={[{ label: "Data" }, { label: "Tipo" }, { label: "Item" }, { label: "Quantidade", align: "right" }, { label: "Origem → Destino" }, { label: "Responsável" }, { label: "Ref." }]}>
        {MOVIMENTACOES.map((m) => {
          const t = TIPO_MOV[m.tipo];
          return (
            <Row key={m.id}>
              <td className="px-4 py-3 text-xs text-muted-foreground">{m.data}</td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center gap-1.5"><span className={`flex h-6 w-6 items-center justify-center rounded ${TONE[t.tone]}`}><Icon name={t.icon} className="h-3.5 w-3.5" /></span><span className="text-sm font-medium">{t.label}</span></span>
              </td>
              <td className="px-4 py-3">{m.item}</td>
              <td className="px-4 py-3 text-right font-medium tabular-nums">{t.sign && t.sign !== "=" ? t.sign + " " : ""}{m.qtd}</td>
              <td className="px-4 py-3 text-sm text-muted-foreground">{m.origem} <Icon name="arrow-right" className="inline h-3 w-3" /> {m.destino}</td>
              <td className="px-4 py-3 text-sm text-muted-foreground">{m.usuario}</td>
              <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{m.ref}</td>
            </Row>
          );
        })}
      </DataTable>
    </div>
  );
}

function LocalizacoesScreen({ pode }) {
  const tipoTone = { campus: "info", predio: "violet", laboratorio: "success", armario: "amber", posicao: "neutral" };
  return (
    <div>
      <PageHeader title="Localizações" subtitle="Hierarquia física: campus → prédio → laboratório → armário → posição.">
        {pode && <Button icon="plus">Nova localização</Button>}
      </PageHeader>
      <DataTable columns={[{ label: "Nome" }, { label: "Tipo" }, { label: "Pertence a" }, ...(pode ? [{ label: "", align: "right" }] : [])]}>
        {LOCALIZACOES.map((l) => (
          <Row key={l.id}>
            <td className="px-4 py-3 font-medium"><span className="inline-flex items-center gap-2"><Icon name="map-pin" className="h-4 w-4 text-muted-foreground" />{l.nome}</span></td>
            <td className="px-4 py-3"><Badge tone={tipoTone[l.tipo]} dot>{l.tipo}</Badge></td>
            <td className="px-4 py-3 text-muted-foreground">{l.pai || "—"}</td>
            {pode && <td className="px-4 py-3 text-right"><RowActions /></td>}
          </Row>
        ))}
      </DataTable>
    </div>
  );
}

function CategoriasScreen({ pode }) {
  return (
    <div>
      <PageHeader title="Categorias" subtitle="Classificação usada para organizar e filtrar os itens do catálogo.">
        {pode && <Button icon="plus">Nova categoria</Button>}
      </PageHeader>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CATEGORIAS.map((c) => (
          <Card key={c.id} className="transition-shadow hover:shadow-[var(--shadow-elegant)]">
            <div className="flex items-start justify-between">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary"><Icon name="tag" className="h-5 w-5" /></span>
              {pode && <RowActions />}
            </div>
            <p className="mt-3 font-semibold">{c.nome}</p>
            <div className="mt-1 flex items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">{c.codigo}</span>
              <span className="text-muted-foreground">·</span>
              <span className="text-xs text-muted-foreground">{c.itens} itens</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { ItensScreen, EquipamentosScreen, EquipamentoDetail, EstoqueScreen, MovimentacoesScreen, LocalizacoesScreen, CategoriasScreen, FilterChip });
