// ============================================================
// LabManager — app raiz: roteamento + permissões
// ============================================================
const { useState, useEffect } = React;

function useLucide(dep) {
  useEffect(() => {
    if (window.lucide) window.lucide.createIcons();
  });
}

function App() {
  const [logged, setLogged] = useState(false);
  const [role, setRole] = useState("gestor");
  const [route, setRoute] = useState("dashboard");
  const [sel, setSel] = useState(null);

  useLucide([logged, role, route, sel]);

  // Se a rota atual não é permitida ao perfil, volta ao início
  function changeRole(r) {
    setRole(r);
    const allowed = navForRole(r).flatMap((g) => g.items.map((i) => i.key));
    const parents = { equipamento_detail: "equipamentos", requisicao_detail: "requisicoes", ordem_detail: "ordens", inventario_detail: "inventarios", baixas: "baixas", manutencoes: "manutencoes" };
    const baseRoute = parents[route] || route;
    if (!allowed.includes(baseRoute)) setRoute("dashboard");
  }

  if (!logged) return <LoginScreen onEnter={() => setLogged(true)} />;

  const pode = role === "almoxarife" || role === "gestor"; // permissão de escrita no catálogo/estoque

  function render() {
    switch (route) {
      case "dashboard": return <Dashboard setRoute={setRoute} role={role} />;
      case "itens": return <ItensScreen pode={pode} />;
      case "equipamentos": return <EquipamentosScreen setRoute={setRoute} setSel={setSel} pode={pode} />;
      case "equipamento_detail": return <EquipamentoDetail id={sel} setRoute={setRoute} pode={pode} />;
      case "categorias": return <CategoriasScreen pode={pode} />;
      case "estoque": return <EstoqueScreen pode={pode} />;
      case "movimentacoes": return <MovimentacoesScreen pode={pode} />;
      case "localizacoes": return <LocalizacoesScreen pode={pode} />;
      case "requisicoes": return <RequisicoesScreen setRoute={setRoute} setSel={setSel} role={role} />;
      case "requisicao_detail": return <RequisicaoDetail id={sel} setRoute={setRoute} role={role} />;
      case "reservas": return <ReservasScreen role={role} />;
      case "ordens": return <OrdensScreen setRoute={setRoute} setSel={setSel} />;
      case "ordem_detail": return <OrdemDetail id={sel} setRoute={setRoute} role={role} />;
      case "manutencoes": return <ManutencoesScreen />;
      case "inventarios": return <InventariosScreen setRoute={setRoute} setSel={setSel} />;
      case "inventario_detail": return <InventarioDetail id={sel} setRoute={setRoute} />;
      case "baixas": return <BaixasScreen />;
      case "auditoria": return <AuditoriaScreen />;
      case "usuarios": return <UsuariosScreen />;
      default: return <Dashboard setRoute={setRoute} role={role} />;
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar route={route} setRoute={(r) => { setRoute(r); setSel(null); }} role={role} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar role={role} setRole={changeRole} pageTitle={route} />
        <main className="flex-1 p-5 lg:p-8">
          <div className="mx-auto max-w-6xl">{render()}</div>
        </main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
