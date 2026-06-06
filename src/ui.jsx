// ============================================================
// LabManager — primitivos de UI compartilhados
// Tailwind + tokens oklch (espelham static/css/input.css)
// ============================================================

// Ícone Lucide. Reexecuta createIcons após render.
function Icon({ name, className = "h-4 w-4", strokeWidth = 2 }) {
  return <i data-lucide={name} className={className} style={{ strokeWidth }}></i>;
}

// Paleta de tons para badges/realces (chroma/lightness coerentes)
const TONE = {
  neutral: "bg-muted text-muted-foreground ring-1 ring-inset ring-border",
  info: "bg-[oklch(0.55_0.13_230_/_0.12)] text-[oklch(0.42_0.13_245)] ring-1 ring-inset ring-[oklch(0.55_0.13_230_/_0.22)]",
  success: "bg-[oklch(0.6_0.13_155_/_0.13)] text-[oklch(0.42_0.12_158)] ring-1 ring-inset ring-[oklch(0.6_0.13_155_/_0.22)]",
  amber: "bg-[oklch(0.78_0.14_75_/_0.16)] text-[oklch(0.5_0.12_60)] ring-1 ring-inset ring-[oklch(0.78_0.14_75_/_0.28)]",
  violet: "bg-[oklch(0.55_0.15_290_/_0.12)] text-[oklch(0.45_0.16_290)] ring-1 ring-inset ring-[oklch(0.55_0.15_290_/_0.22)]",
  destructive: "bg-[oklch(0.6_0.2_25_/_0.12)] text-[oklch(0.5_0.2_25)] ring-1 ring-inset ring-[oklch(0.6_0.2_25_/_0.22)]",
};
const DOT = {
  neutral: "bg-muted-foreground/60", info: "bg-[oklch(0.55_0.13_230)]",
  success: "bg-[oklch(0.6_0.13_155)]", amber: "bg-[oklch(0.78_0.14_60)]",
  violet: "bg-[oklch(0.55_0.15_290)]", destructive: "bg-[oklch(0.6_0.2_25)]",
};

function Badge({ tone = "neutral", children, dot = false, className = "" }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${TONE[tone]} ${className}`}>
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${DOT[tone]}`}></span>}
      {children}
    </span>
  );
}

// Badge a partir de um dicionário de status (label + tone)
function StatusBadge({ map, value, dot = true }) {
  const s = map[value] || { label: value, tone: "neutral" };
  return <Badge tone={s.tone} dot={dot}>{s.label}</Badge>;
}

function Button({ variant = "primary", size = "md", children, className = "", icon, onClick, type = "button" }) {
  const base = "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50";
  const sizes = { sm: "h-8 px-3 text-xs", md: "h-9 px-4 text-sm", lg: "h-10 px-5 text-sm" };
  const variants = {
    primary: "bg-[image:var(--gradient-hero)] text-primary-foreground shadow-[var(--shadow-card)] hover:opacity-90",
    solid: "bg-primary text-primary-foreground hover:bg-primary/90",
    outline: "border border-input bg-card hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground text-muted-foreground hover:text-foreground",
    destructive: "border border-destructive/40 text-destructive hover:bg-destructive/10",
  };
  return (
    <button type={type} onClick={onClick} className={`${base} ${sizes[size]} ${variants[variant]} ${className}`}>
      {icon && <Icon name={icon} className={size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4"} />}
      {children}
    </button>
  );
}

function Card({ children, className = "", pad = true }) {
  return (
    <div className={`rounded-xl border border-border bg-card shadow-[var(--shadow-card)] ${pad ? "p-5" : ""} ${className}`}>
      {children}
    </div>
  );
}

// Cabeçalho de página padrão
function PageHeader({ title, subtitle, children, breadcrumb }) {
  return (
    <div className="mb-6">
      {breadcrumb && (
        <div className="mb-2 flex items-center gap-1.5 text-xs text-muted-foreground">
          {breadcrumb.map((b, i) => (
            <React.Fragment key={i}>
              {i > 0 && <Icon name="chevron-right" className="h-3 w-3" />}
              <span className={i === breadcrumb.length - 1 ? "text-foreground" : ""}>{b}</span>
            </React.Fragment>
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
          {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
        </div>
        {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
      </div>
    </div>
  );
}

// Banner informativo (substitui app/intros/*)
function Hint({ children, icon = "info" }) {
  return (
    <div className="mb-5 flex items-start gap-3 rounded-lg border border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
      <Icon name={icon} className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
      <p className="leading-relaxed">{children}</p>
    </div>
  );
}

function EmptyState({ icon = "inbox", title, children }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-muted text-muted-foreground">
        <Icon name={icon} className="h-6 w-6" />
      </div>
      <p className="mt-4 font-medium">{title}</p>
      {children && <p className="mt-1 max-w-sm text-sm text-muted-foreground">{children}</p>}
    </div>
  );
}

// Tabela estilizada — wrapper + header
function DataTable({ columns, children }) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[var(--shadow-card)]">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/40 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {columns.map((c, i) => (
                <th key={i} className={`px-4 py-3 font-medium ${c.align === "right" ? "text-right" : ""} ${c.className || ""}`}>{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">{children}</tbody>
        </table>
      </div>
    </div>
  );
}

// Linha de tabela clicável
function Row({ children, onClick, highlight = false }) {
  return (
    <tr
      onClick={onClick}
      className={`transition-colors ${onClick ? "cursor-pointer" : ""} ${highlight ? "bg-[oklch(0.6_0.2_25_/_0.04)] hover:bg-[oklch(0.6_0.2_25_/_0.07)]" : "hover:bg-muted/40"}`}
    >
      {children}
    </tr>
  );
}

// Barra de proporção (estoque: livre vs reservado)
function StockBar({ livre, reservado, total, alerta }) {
  const max = Math.max(total, 1);
  const pLivre = (livre / max) * 100;
  const pRes = (reservado / max) * 100;
  const baixo = livre <= alerta;
  return (
    <div className="w-36">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-muted">
        <div className={baixo ? "bg-[oklch(0.6_0.2_25)]" : "bg-[oklch(0.6_0.13_155)]"} style={{ width: pLivre + "%" }}></div>
        <div className="bg-[oklch(0.78_0.14_75)]" style={{ width: pRes + "%" }}></div>
      </div>
    </div>
  );
}

// Campo de formulário (label + controle)
function Field({ label, children, hint, className = "" }) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && <label className="text-sm font-medium">{label}</label>}
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
const inputCls = "flex h-9 w-full rounded-md border border-input bg-card px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

function Input(props) { return <input {...props} className={`${inputCls} ${props.className || ""}`} />; }
function Select({ children, ...props }) {
  return (
    <div className="relative">
      <select {...props} className={`${inputCls} appearance-none pr-8 ${props.className || ""}`}>{children}</select>
      <Icon name="chevron-down" className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
    </div>
  );
}

// Busca
function SearchBox({ value, onChange, placeholder = "Buscar..." }) {
  return (
    <div className="relative">
      <Icon name="search" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <input value={value} onChange={onChange} placeholder={placeholder}
        className={`${inputCls} w-64 max-w-full pl-9`} />
    </div>
  );
}

Object.assign(window, { Icon, Badge, StatusBadge, Button, Card, PageHeader, Hint, EmptyState, DataTable, Row, StockBar, Field, Input, Select, SearchBox, inputCls });
