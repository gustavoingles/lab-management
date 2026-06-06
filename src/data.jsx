// ============================================================
// LabManager — dados de demonstração (pt-BR)
// Espelha os enums de inventory/choices.py e o guia de apresentação.
// ============================================================

// ---- Perfis (role switcher) -------------------------------------------------
const PERFIS = {
  solicitante: { codigo: "solicitante", nome: "Solicitante", desc: "Pesquisador / aluno" },
  almoxarife: { codigo: "almoxarife", nome: "Almoxarife", desc: "Estoque físico" },
  gestor: { codigo: "gestor", nome: "Gestor", desc: "Coordenador do laboratório" },
  manutencao: { codigo: "manutencao", nome: "Téc. manutenção", desc: "Ordens de serviço" },
};

const USUARIOS = {
  solicitante: { nome: "Marina Alves", email: "marina@lab.test", iniciais: "MA" },
  almoxarife: { nome: "Renato Lima", email: "renato@lab.test", iniciais: "RL" },
  gestor: { nome: "Cláudia Souza", email: "claudia@lab.test", iniciais: "CS" },
  manutencao: { nome: "Iuri Mendes", email: "iuri@lab.test", iniciais: "IM" },
};

// ---- Tipos de item ----------------------------------------------------------
const TIPOS_ITEM = {
  equipamento: { label: "Equipamento", icon: "cpu", tone: "info" },
  consumivel: { label: "Consumível", icon: "package", tone: "neutral" },
  reagente: { label: "Reagente", icon: "flask-round", tone: "violet" },
  epi: { label: "EPI", icon: "shield", tone: "success" },
  peca: { label: "Peça", icon: "cog", tone: "amber" },
};

// ---- Estados operacionais (equipamento) ------------------------------------
const STATUS_OP = {
  ativo: { label: "Ativo", tone: "success", icon: "circle-check" },
  em_manutencao: { label: "Em manutenção", tone: "amber", icon: "wrench" },
  inativo: { label: "Inativo", tone: "neutral", icon: "circle-pause" },
  descartado: { label: "Descartado", tone: "destructive", icon: "trash-2" },
};

// ---- Status de requisição ---------------------------------------------------
const STATUS_REQ = {
  rascunho: { label: "Rascunho", tone: "neutral" },
  aberta: { label: "Aberta", tone: "info" },
  em_aprovacao: { label: "Em aprovação", tone: "amber" },
  aprovada: { label: "Aprovada", tone: "violet" },
  rejeitada: { label: "Rejeitada", tone: "destructive" },
  atendida: { label: "Atendida", tone: "success" },
  cancelada: { label: "Cancelada", tone: "neutral" },
};

const STATUS_OS = {
  aberta: { label: "Aberta", tone: "info" },
  em_execucao: { label: "Em execução", tone: "amber" },
  aguardando_pecas: { label: "Aguardando peças", tone: "violet" },
  encerrada: { label: "Encerrada", tone: "success" },
  cancelada: { label: "Cancelada", tone: "neutral" },
};

const STATUS_RESERVA = {
  pendente: { label: "Pendente", tone: "amber" },
  confirmada: { label: "Confirmada", tone: "success" },
  cancelada: { label: "Cancelada", tone: "neutral" },
  encerrada: { label: "Encerrada", tone: "neutral" },
};

const STATUS_INV = {
  aberto: { label: "Aberto", tone: "info" },
  em_andamento: { label: "Em andamento", tone: "amber" },
  encerrado: { label: "Encerrado", tone: "success" },
  cancelado: { label: "Cancelado", tone: "neutral" },
};

const TIPO_MOV = {
  entrada: { label: "Entrada", tone: "success", icon: "arrow-down-to-line", sign: "+" },
  saida: { label: "Saída", tone: "destructive", icon: "arrow-up-from-line", sign: "−" },
  transferencia: { label: "Transferência", tone: "info", icon: "arrow-left-right", sign: "" },
  ajuste: { label: "Ajuste", tone: "amber", icon: "sliders-horizontal", sign: "=" },
  baixa: { label: "Baixa", tone: "neutral", icon: "archive-x", sign: "−" },
};

const PRIORIDADE = {
  baixa: { label: "Baixa", tone: "neutral" },
  media: { label: "Média", tone: "info" },
  alta: { label: "Alta", tone: "amber" },
  critica: { label: "Crítica", tone: "destructive" },
};

const TIPO_MAN = {
  preventiva: { label: "Preventiva", tone: "info" },
  corretiva: { label: "Corretiva", tone: "amber" },
  calibracao: { label: "Calibração", tone: "violet" },
  verificacao: { label: "Verificação", tone: "neutral" },
  inspecao: { label: "Inspeção", tone: "neutral" },
};

// ---- Catálogo ---------------------------------------------------------------
const CATEGORIAS = [
  { id: 1, codigo: "REAG", nome: "Reagentes", itens: 3 },
  { id: 2, codigo: "CONS", nome: "Consumíveis", itens: 2 },
  { id: 3, codigo: "EPI", nome: "Proteção individual", itens: 2 },
  { id: 4, codigo: "EQUIP", nome: "Equipamentos", itens: 3 },
  { id: 5, codigo: "PECA", nome: "Peças e sobressalentes", itens: 1 },
];

const UNIDADES = [
  { id: 1, sigla: "mL", nome: "Mililitro" },
  { id: 2, sigla: "L", nome: "Litro" },
  { id: 3, sigla: "un", nome: "Unidade" },
  { id: 4, sigla: "cx", nome: "Caixa" },
  { id: 5, sigla: "par", nome: "Par" },
];

const LOCALIZACOES = [
  { id: 1, nome: "Campus Saúde", tipo: "campus", pai: null },
  { id: 2, nome: "Prédio A — Biológicas", tipo: "predio", pai: "Campus Saúde" },
  { id: 3, nome: "Lab. Bioquímica", tipo: "laboratorio", pai: "Prédio A — Biológicas" },
  { id: 4, nome: "Lab. Microbiologia", tipo: "laboratorio", pai: "Prédio A — Biológicas" },
  { id: 5, nome: "Almoxarifado Central", tipo: "armario", pai: "Prédio A — Biológicas" },
  { id: 6, nome: "Armário B2", tipo: "armario", pai: "Lab. Bioquímica" },
];

const ITENS = [
  { id: 1, codigo: "REAG-001", nome: "Etanol 70%", tipo: "reagente", categoria: "Reagentes", unidade: "mL", controlado: false },
  { id: 2, codigo: "REAG-002", nome: "Ácido Clorídrico PA", tipo: "reagente", categoria: "Reagentes", unidade: "mL", controlado: true },
  { id: 3, codigo: "REAG-003", nome: "Solução de Lugol", tipo: "reagente", categoria: "Reagentes", unidade: "mL", controlado: false },
  { id: 4, codigo: "CONS-001", nome: "Ponteira 1000 µL", tipo: "consumivel", categoria: "Consumíveis", unidade: "un", controlado: false },
  { id: 5, codigo: "CONS-002", nome: "Tubo Falcon 15 mL", tipo: "consumivel", categoria: "Consumíveis", unidade: "un", controlado: false },
  { id: 6, codigo: "EPI-001", nome: "Luva Nitrílica M", tipo: "epi", categoria: "Proteção individual", unidade: "cx", controlado: false },
  { id: 7, codigo: "EPI-002", nome: "Óculos de proteção", tipo: "epi", categoria: "Proteção individual", unidade: "un", controlado: false },
  { id: 8, codigo: "EQ-001", nome: "Microscópio Binocular", tipo: "equipamento", categoria: "Equipamentos", unidade: "un", controlado: false },
  { id: 9, codigo: "EQ-002", nome: "Centrífuga Refrigerada", tipo: "equipamento", categoria: "Equipamentos", unidade: "un", controlado: false },
  { id: 10, codigo: "EQ-003", nome: "Autoclave Vertical", tipo: "equipamento", categoria: "Equipamentos", unidade: "un", controlado: false },
  { id: 11, codigo: "PECA-001", nome: "Rotor para centrífuga", tipo: "peca", categoria: "Peças e sobressalentes", unidade: "un", controlado: false },
];

const EQUIPAMENTOS = [
  { id: 1, serie: "MIC-2021-0098", tombamento: "TB-44210", item: "Microscópio Binocular", status: "ativo", local: "Lab. Bioquímica", aquisicao: "2021-03-12", proxManut: "2026-08-10", os: 0 },
  { id: 2, serie: "CEN-2019-0312", tombamento: "TB-39817", item: "Centrífuga Refrigerada", status: "em_manutencao", local: "Lab. Microbiologia", aquisicao: "2019-07-30", proxManut: "2026-06-15", os: 1 },
  { id: 3, serie: "AUT-2022-0011", tombamento: "TB-50120", item: "Autoclave Vertical", status: "ativo", local: "Lab. Microbiologia", aquisicao: "2022-11-05", proxManut: "2026-07-01", os: 0 },
  { id: 4, serie: "MIC-2017-0044", tombamento: "TB-28890", item: "Microscópio Binocular", status: "inativo", local: "Almoxarifado Central", aquisicao: "2017-02-18", proxManut: "—", os: 0 },
];

const ESTOQUE = [
  { id: 1, item: "Etanol 70%", codigo: "REAG-001", local: "Lab. Bioquímica", unidade: "mL", total: 5000, reservado: 500, minimo: 1000, alerta: 1500 },
  { id: 2, item: "Ácido Clorídrico PA", codigo: "REAG-002", local: "Almoxarifado Central", unidade: "mL", total: 2000, reservado: 0, minimo: 500, alerta: 800 },
  { id: 3, item: "Ponteira 1000 µL", codigo: "CONS-001", local: "Almoxarifado Central", unidade: "un", total: 120, reservado: 100, minimo: 50, alerta: 80 },
  { id: 4, item: "Tubo Falcon 15 mL", codigo: "CONS-002", local: "Lab. Microbiologia", unidade: "un", total: 40, reservado: 10, minimo: 25, alerta: 30 },
  { id: 5, item: "Luva Nitrílica M", codigo: "EPI-001", local: "Lab. Microbiologia", unidade: "cx", total: 8, reservado: 0, minimo: 5, alerta: 6 },
  { id: 6, item: "Solução de Lugol", codigo: "REAG-003", local: "Armário B2", unidade: "mL", total: 250, reservado: 0, minimo: 100, alerta: 150 },
];
ESTOQUE.forEach((e) => { e.livre = e.total - e.reservado; e.abaixoAlerta = e.livre <= e.alerta; });

const MOVIMENTACOES = [
  { id: 1, data: "04/06 14:22", tipo: "saida", item: "Ponteira 1000 µL", qtd: "80 un", origem: "Almoxarifado Central", destino: "—", usuario: "Renato Lima", ref: "REQ #1039" },
  { id: 2, data: "04/06 11:08", tipo: "entrada", item: "Etanol 70%", qtd: "2000 mL", origem: "—", destino: "Lab. Bioquímica", usuario: "Renato Lima", ref: "NF 8841" },
  { id: 3, data: "03/06 16:45", tipo: "transferencia", item: "Tubo Falcon 15 mL", qtd: "20 un", origem: "Almoxarifado Central", destino: "Lab. Microbiologia", usuario: "Renato Lima", ref: "—" },
  { id: 4, data: "03/06 09:30", tipo: "ajuste", item: "Luva Nitrílica M", qtd: "8 cx", origem: "—", destino: "Lab. Microbiologia", usuario: "Cláudia Souza", ref: "INV-2026-03" },
  { id: 5, data: "02/06 15:12", tipo: "entrada", item: "Ácido Clorídrico PA", qtd: "2000 mL", origem: "—", destino: "Almoxarifado Central", usuario: "Renato Lima", ref: "NF 8830" },
  { id: 6, data: "02/06 10:01", tipo: "baixa", item: "Solução de Lugol", qtd: "50 mL", origem: "Armário B2", destino: "—", usuario: "Cláudia Souza", ref: "Validade" },
];

// Requisições — a #1042 é o fluxo interativo demonstrado
const REQUISICOES = [
  {
    id: 1042, status: "aberta", solicitante: "Marina Alves", criada: "05/06/2026",
    finalidade: "Aula prática de Bioquímica — Turma B",
    justificativa: "Material para 24 alunos na bancada de extração.",
    itens: [
      { id: 1, item: "Etanol 70%", unidade: "mL", solicitado: 500, aprovado: null, reserva: null, atendido: null, localOpcoes: ["Lab. Bioquímica", "Armário B2"] },
      { id: 2, item: "Ponteira 1000 µL", unidade: "un", solicitado: 50, aprovado: null, reserva: null, atendido: null, localOpcoes: ["Almoxarifado Central"] },
      { id: 3, item: "Tubo Falcon 15 mL", unidade: "un", solicitado: 20, aprovado: null, reserva: null, atendido: null, localOpcoes: ["Lab. Microbiologia"] },
    ],
  },
  {
    id: 1041, status: "aprovada", solicitante: "Marina Alves", criada: "04/06/2026",
    finalidade: "Cultura microbiológica", justificativa: "Reposição semanal.",
    itens: [
      { id: 1, item: "Luva Nitrílica M", unidade: "cx", solicitado: 2, aprovado: 2, reserva: "Lab. Microbiologia", atendido: null, localOpcoes: ["Lab. Microbiologia"] },
    ],
  },
  { id: 1039, status: "atendida", solicitante: "João Pereira", criada: "03/06/2026", finalidade: "Preparo de meio de cultura", justificativa: "", itens: [] },
  { id: 1038, status: "rejeitada", solicitante: "Marina Alves", criada: "01/06/2026", finalidade: "Teste de bancada", justificativa: "", itens: [] },
  { id: 1035, status: "atendida", solicitante: "Ana Costa", criada: "28/05/2026", finalidade: "Análise de amostras", justificativa: "", itens: [] },
];

const RESERVAS = [
  { id: 1, equipamento: "Microscópio Binocular", serie: "MIC-2021-0098", solicitante: "Marina Alves", inicio: "06/06 14:00", fim: "06/06 16:00", status: "pendente", finalidade: "Análise de lâminas" },
  { id: 2, equipamento: "Autoclave Vertical", serie: "AUT-2022-0011", solicitante: "João Pereira", inicio: "06/06 09:00", fim: "06/06 10:30", status: "confirmada", finalidade: "Esterilização de vidraria" },
  { id: 3, equipamento: "Microscópio Binocular", serie: "MIC-2021-0098", solicitante: "Ana Costa", inicio: "07/06 10:00", fim: "07/06 12:00", status: "confirmada", finalidade: "Contagem celular" },
  { id: 4, equipamento: "Autoclave Vertical", serie: "AUT-2022-0011", solicitante: "Marina Alves", inicio: "05/06 16:00", fim: "05/06 17:00", status: "encerrada", finalidade: "Descontaminação" },
];

const ORDENS = [
  { id: 205, equipamento: "Centrífuga Refrigerada", serie: "CEN-2019-0312", status: "em_execucao", prioridade: "alta", abertura: "03/06/2026", problema: "Ruído anormal e vibração acima do esperado no rotor.", responsavel: "Iuri Mendes" },
  { id: 204, equipamento: "Autoclave Vertical", serie: "AUT-2022-0011", status: "aberta", prioridade: "media", abertura: "04/06/2026", problema: "Calibração de pressão pendente (vencida).", responsavel: "—" },
  { id: 201, equipamento: "Microscópio Binocular", serie: "MIC-2021-0098", status: "encerrada", prioridade: "baixa", abertura: "20/05/2026", problema: "Troca de lâmpada de iluminação.", responsavel: "Iuri Mendes" },
  { id: 198, equipamento: "Centrífuga Refrigerada", serie: "CEN-2019-0312", status: "encerrada", prioridade: "critica", abertura: "02/05/2026", problema: "Falha no sistema de refrigeração.", responsavel: "Iuri Mendes" },
];

const MANUTENCOES_OS = [
  { id: 1, tipo: "corretiva", realizada: "—", proximo: "—", obs: "Diagnóstico em andamento — aguardando rotor (PECA-001)." },
];

const MANUTENCOES = [
  { id: 1, equipamento: "Microscópio Binocular", tipo: "corretiva", realizada: "20/05/2026", proximo: "20/11/2026", os: 201 },
  { id: 2, equipamento: "Centrífuga Refrigerada", tipo: "corretiva", realizada: "05/05/2026", proximo: "—", os: 198 },
  { id: 3, equipamento: "Autoclave Vertical", tipo: "calibracao", realizada: "01/02/2026", proximo: "01/06/2026", os: null, vencida: true },
  { id: 4, equipamento: "Microscópio Binocular", tipo: "preventiva", realizada: "10/02/2026", proximo: "10/08/2026", os: null },
];

const INVENTARIOS = [
  { id: "INV-2026-03", local: "Lab. Microbiologia", status: "em_andamento", criado: "03/06/2026", responsavel: "Renato Lima", linhas: 12, divergencias: 2 },
  { id: "INV-2026-02", local: "Almoxarifado Central", status: "encerrado", criado: "01/05/2026", responsavel: "Renato Lima", linhas: 38, divergencias: 5 },
  { id: "INV-2026-01", local: "Lab. Bioquímica", status: "encerrado", criado: "02/04/2026", responsavel: "Cláudia Souza", linhas: 21, divergencias: 0 },
];

const INVENTARIO_LINHAS = [
  { id: 1, item: "Tubo Falcon 15 mL", local: "Lab. Microbiologia", sistema: 40, contado: 38, },
  { id: 2, item: "Luva Nitrílica M", local: "Lab. Microbiologia", sistema: 8, contado: 8 },
  { id: 3, item: "Ponteira 1000 µL", local: "Lab. Microbiologia", sistema: 0, contado: 12 },
  { id: 4, item: "Solução de Lugol", local: "Lab. Microbiologia", sistema: 250, contado: 250 },
];
INVENTARIO_LINHAS.forEach((l) => { l.diff = l.contado - l.sistema; });

const AUDITORIA = [
  { id: 1, quando: "05/06 09:14", quem: "Cláudia Souza", perfil: "Gestor", acao: "aprovou", alvo: "Requisição #1041", icon: "check-circle-2", tone: "success" },
  { id: 2, quando: "04/06 14:22", quem: "Renato Lima", perfil: "Almoxarife", acao: "registrou saída de", alvo: "Ponteira 1000 µL (80 un)", icon: "arrow-up-from-line", tone: "info" },
  { id: 3, quando: "04/06 11:08", quem: "Renato Lima", perfil: "Almoxarife", acao: "registrou entrada de", alvo: "Etanol 70% (2000 mL)", icon: "arrow-down-to-line", tone: "success" },
  { id: 4, quando: "04/06 08:50", quem: "Marina Alves", perfil: "Solicitante", acao: "criou", alvo: "Requisição #1042", icon: "file-plus", tone: "neutral" },
  { id: 5, quando: "03/06 16:45", quem: "Renato Lima", perfil: "Almoxarife", acao: "transferiu", alvo: "Tubo Falcon 15 mL (20 un)", icon: "arrow-left-right", tone: "info" },
  { id: 6, quando: "03/06 10:02", quem: "Iuri Mendes", perfil: "Téc. manutenção", acao: "abriu", alvo: "OS #205 — Centrífuga", icon: "wrench", tone: "amber" },
  { id: 7, quando: "02/06 15:12", quem: "Renato Lima", perfil: "Almoxarife", acao: "registrou entrada de", alvo: "Ácido Clorídrico PA (2000 mL)", icon: "arrow-down-to-line", tone: "success" },
  { id: 8, quando: "01/06 17:30", quem: "Cláudia Souza", perfil: "Gestor", acao: "rejeitou", alvo: "Requisição #1038", icon: "x-circle", tone: "destructive" },
];

Object.assign(window, {
  PERFIS, USUARIOS, TIPOS_ITEM, STATUS_OP, STATUS_REQ, STATUS_OS, STATUS_RESERVA,
  STATUS_INV, TIPO_MOV, PRIORIDADE, TIPO_MAN, CATEGORIAS, UNIDADES, LOCALIZACOES,
  ITENS, EQUIPAMENTOS, ESTOQUE, MOVIMENTACOES, REQUISICOES, RESERVAS, ORDENS,
  MANUTENCOES_OS, MANUTENCOES, INVENTARIOS, INVENTARIO_LINHAS, AUDITORIA,
});
