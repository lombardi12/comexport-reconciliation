/**
 * Comexport Customs Reconciliation Intelligence - Frontend Controller
 * Powered by Google Gemini 3.8 Flash & Google Cloud Document AI
 */

let currentScenarioId = "byd_ev_shipment";
let currentScenarioPayload = null;

document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  await loadScenarios();
  setupEventListeners();
});

function setupEventListeners() {
  const reconcileBtn = document.getElementById("btn-reconcile");
  if (reconcileBtn) {
    reconcileBtn.addEventListener("click", () => {
      runReconciliation();
    });
  }
}

async function loadScenarios() {
  try {
    const response = await fetch("/api/scenarios");
    const scenarios = await response.json();
    const container = document.getElementById("scenarios-container");
    container.innerHTML = "";

    scenarios.forEach((sc, idx) => {
      const btn = document.createElement("button");
      btn.id = `btn-scenario-${sc.id}`;
      btn.className = `px-3.5 py-2 rounded-xl text-xs font-medium border transition-all text-left flex items-center gap-2 ${
        sc.id === currentScenarioId
          ? "bg-blue-600/20 text-blue-300 border-blue-500/50 shadow-md shadow-blue-500/10"
          : "bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
      }`;

      let channelBadge = "";
      if (sc.expected_channel === "VERDE") {
        channelBadge = `<span class="h-2 w-2 rounded-full bg-emerald-400"></span>`;
      } else if (sc.expected_channel === "VERMELHO") {
        channelBadge = `<span class="h-2 w-2 rounded-full bg-rose-500"></span>`;
      } else {
        channelBadge = `<span class="h-2 w-2 rounded-full bg-amber-400"></span>`;
      }

      btn.innerHTML = `
        ${channelBadge}
        <div>
          <span class="font-bold">${sc.title}</span>
          <p class="text-[10px] text-slate-500">${sc.category}</p>
        </div>
      `;

      btn.addEventListener("click", () => selectScenario(sc.id));
      container.appendChild(btn);
    });

    // Carrega o primeiro cenário por padrão
    await selectScenario(currentScenarioId);
  } catch (err) {
    console.error("Erro ao carregar cenários:", err);
  }
}

async function selectScenario(scenarioId) {
  currentScenarioId = scenarioId;

  // Atualiza estilos dos botões
  document.querySelectorAll("[id^='btn-scenario-']").forEach((btn) => {
    btn.className = btn.className.replace(
      "bg-blue-600/20 text-blue-300 border-blue-500/50 shadow-md shadow-blue-500/10",
      "bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
    );
  });
  const activeBtn = document.getElementById(`btn-scenario-${scenarioId}`);
  if (activeBtn) {
    activeBtn.className = activeBtn.className.replace(
      "bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200",
      "bg-blue-600/20 text-blue-300 border-blue-500/50 shadow-md shadow-blue-500/10"
    );
  }

  // Busca dados do cenário selecionado
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}`);
    currentScenarioPayload = await res.json();
    populateDocumentsView(currentScenarioPayload);

    // Executa a conciliação automaticamente para fluidez na demo
    await runReconciliation();
  } catch (err) {
    console.error("Erro ao buscar dados do cenário:", err);
  }
}

function populateDocumentsView(data) {
  const inv = data.invoice;
  const pkl = data.packing_list;
  const duimp = data.duimp;

  // Invoice
  document.getElementById("inv-number").textContent = inv.invoice_number;
  document.getElementById("inv-date").textContent = inv.issue_date;
  document.getElementById("inv-supplier").textContent = inv.supplier_name;
  document.getElementById("inv-incoterm-badge").textContent = inv.incoterm;
  document.getElementById("inv-total").textContent = `US$ ${inv.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
  document.getElementById("inv-freight").textContent = `US$ ${inv.freight_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
  document.getElementById("inv-insurance").textContent = `US$ ${inv.insurance_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

  const itemsContainer = document.getElementById("inv-items-list");
  itemsContainer.innerHTML = "";
  inv.items.forEach((item) => {
    const el = document.createElement("div");
    el.className = "p-2 rounded bg-slate-900/40 border border-slate-800/80 flex items-center justify-between";
    el.innerHTML = `
      <div class="truncate mr-2">
        <p class="font-medium text-slate-200 truncate">${item.description}</p>
        <p class="text-[10px] text-slate-500 font-mono">SKU: ${item.sku} • NCM: ${item.ncm}</p>
      </div>
      <div class="text-right whitespace-nowrap">
        <p class="font-mono text-slate-300">${item.quantity} un</p>
        <p class="font-mono text-emerald-400 font-semibold">US$ ${item.total_price.toLocaleString("en-US")}</p>
      </div>
    `;
    itemsContainer.appendChild(el);
  });

  // Packing List
  document.getElementById("pkl-number").textContent = pkl.packing_list_number;
  document.getElementById("pkl-containers").textContent = pkl.container_numbers.join(", ") || "A granel / Ro-Ro";
  document.getElementById("pkl-packages-badge").textContent = `${pkl.total_packages} volumes`;
  document.getElementById("pkl-net-weight").textContent = `${pkl.total_net_weight_kg.toLocaleString("pt-BR")} kg`;
  document.getElementById("pkl-gross-weight").textContent = `${pkl.total_gross_weight_kg.toLocaleString("pt-BR")} kg`;

  // DUIMP
  document.getElementById("duimp-number").textContent = duimp.duimp_number;
  document.getElementById("duimp-ptax").textContent = `R$ ${duimp.ptax_rate.toFixed(4)}`;
  document.getElementById("duimp-urf").textContent = duimp.urog_desembaraco;
  document.getElementById("duimp-modal-badge").textContent = duimp.modal;
  document.getElementById("duimp-val-usd").textContent = `US$ ${duimp.total_customs_value_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
  document.getElementById("duimp-val-brl").textContent = `R$ ${duimp.total_customs_value_brl.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`;

  if (window.lucide) {
    lucide.createIcons();
  }
}

async function runReconciliation() {
  if (!currentScenarioPayload) return;

  const btn = document.getElementById("btn-reconcile");
  const originalBtnHtml = btn.innerHTML;
  btn.innerHTML = `<span class="animate-spin inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span> Analisando com Gemini 3.8 Flash...`;
  btn.disabled = true;

  try {
    const response = await fetch("/api/reconcile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentScenarioPayload),
    });

    const result = await response.json();
    renderReconciliationResult(result);
  } catch (err) {
    console.error("Erro na conciliação:", err);
  } finally {
    btn.innerHTML = originalBtnHtml;
    btn.disabled = false;
    if (window.lucide) {
      lucide.createIcons();
    }
  }
}

function renderReconciliationResult(res) {
  const summary = res.summary;
  const channel = summary.risk_channel;

  const banner = document.getElementById("risk-banner");
  const pill = document.getElementById("risk-status-pill");
  const title = document.getElementById("risk-title");
  const subtitle = document.getElementById("risk-subtitle");
  const iconContainer = document.getElementById("risk-icon-container");

  // Remove classes anteriores
  banner.classList.remove("border-emerald-500/40", "bg-emerald-950/20", "pulse-green");
  banner.classList.remove("border-rose-500/40", "bg-rose-950/20", "pulse-red");
  banner.classList.remove("border-amber-500/40", "bg-amber-950/20");

  if (channel === "VERDE") {
    banner.classList.add("border-emerald-500/40", "bg-emerald-950/20", "pulse-green");
    pill.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40";
    pill.innerHTML = `<span class="h-2 w-2 rounded-full bg-emerald-400"></span> Canal Verde • Aprovado`;
    title.textContent = "Conformidade Aduaneira Aprovada (Canal Verde)";
    title.className = "text-2xl font-black tracking-tight text-emerald-400 mt-2";
    subtitle.textContent = "100% dos dados foram conciliados com sucesso. DUIMP liberada para registro no Siscomex.";
    iconContainer.className = "h-16 w-16 rounded-2xl flex items-center justify-center bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 shadow-lg shadow-emerald-500/20";
    iconContainer.innerHTML = `<i data-lucide="check-circle-2" class="w-8 h-8"></i>`;
  } else if (channel === "VERMELHO") {
    banner.classList.add("border-rose-500/40", "bg-rose-950/20", "pulse-red");
    pill.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/40";
    pill.innerHTML = `<span class="h-2 w-2 rounded-full bg-rose-500 animate-ping"></span> Canal Vermelho • Transmissão Bloqueada`;
    title.textContent = "Inconsistências Críticas Detectadas (Canal Vermelho)";
    title.className = "text-2xl font-black tracking-tight text-rose-400 mt-2";
    subtitle.textContent = "Risco iminente de retenção de carga no porto, multas de ofício e custo de demurrage.";
    iconContainer.className = "h-16 w-16 rounded-2xl flex items-center justify-center bg-rose-500/20 border border-rose-500/40 text-rose-400 shadow-lg shadow-rose-500/20";
    iconContainer.innerHTML = `<i data-lucide="alert-octagon" class="w-8 h-8"></i>`;
  } else {
    banner.classList.add("border-amber-500/40", "bg-amber-950/20");
    pill.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40";
    pill.innerHTML = `<span class="h-2 w-2 rounded-full bg-amber-400"></span> Canal Amarelo • Atenção Requerida`;
    title.textContent = "Atenção Operacional Requerida (Canal Amarelo)";
    title.className = "text-2xl font-black tracking-tight text-amber-400 mt-2";
    subtitle.textContent = "Divergência secundária de tolerância cambial ou frete. Recomenda-se retificação antes do envio.";
    iconContainer.className = "h-16 w-16 rounded-2xl flex items-center justify-center bg-amber-500/20 border border-amber-500/40 text-amber-400 shadow-lg shadow-amber-500/20";
    iconContainer.innerHTML = `<i data-lucide="alert-triangle" class="w-8 h-8"></i>`;
  }

  // KPIs
  document.getElementById("kpi-score").textContent = `${summary.risk_score.toFixed(1)}%`;
  document.getElementById("kpi-critical").textContent = summary.critical_issues;
  document.getElementById("kpi-warnings").textContent = summary.warning_issues;
  document.getElementById("kpi-penalty").textContent = `R$ ${summary.potential_penalty_risk_brl.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`;

  // Parecer Executivo do Gemini 3.8 Flash
  document.getElementById("ai-diagnosis-text").textContent = summary.ai_executive_summary;

  // Avaliação Semântica de NCM
  const semContainer = document.getElementById("semantic-ncm-container");
  semContainer.innerHTML = "";
  if (res.semantic_analysis && res.semantic_analysis.length > 0) {
    res.semantic_analysis.forEach((sem) => {
      const card = document.createElement("div");
      const isOk = sem.semantic_match;
      card.className = `p-3 rounded-xl border ${
        isOk ? "bg-emerald-950/10 border-emerald-500/20" : "bg-rose-950/20 border-rose-500/30"
      } text-xs space-y-1.5`;

      card.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="font-mono font-bold text-slate-200">${sem.item_sku}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono ${
              isOk ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
            }">NCM: ${sem.declared_ncm}</span>
          </div>
          <span class="font-mono text-[11px] font-bold ${isOk ? "text-emerald-400" : "text-rose-400"}">
            Confiança IA: ${sem.confidence_score_pct.toFixed(1)}%
          </span>
        </div>
        <p class="text-slate-300 font-medium">"${sem.international_description}"</p>
        <p class="text-[11px] text-slate-400">${sem.ai_evaluation}</p>
        ${
          sem.recommended_ncm
            ? `<div class="mt-1 pt-1 border-t border-rose-500/20 text-rose-300 font-semibold text-[11px]">Sugestão Gemini: Utilizar NCM ${sem.recommended_ncm}</div>`
            : ""
        }
      `;
      semContainer.appendChild(card);
    });
  } else {
    semContainer.innerHTML = `<p class="text-xs text-slate-500 italic">Nenhum item avaliado.</p>`;
  }

  // Tabela de Divergências
  const discContainer = document.getElementById("discrepancies-container");
  const countBadge = document.getElementById("discrepancy-count-badge");
  discContainer.innerHTML = "";
  countBadge.textContent = `${res.discrepancies.length} item(ns)`;

  if (res.discrepancies.length === 0) {
    discContainer.innerHTML = `
      <div class="p-4 rounded-xl bg-emerald-950/10 border border-emerald-500/20 text-center">
        <i data-lucide="check" class="w-6 h-6 text-emerald-400 mx-auto mb-1"></i>
        <p class="text-xs font-semibold text-emerald-300">Nenhuma divergência documental ou fiscal encontrada.</p>
        <p class="text-[11px] text-slate-400 mt-0.5">Todos os valores, NCMs, pesos e taxas coincidem perfeitamente.</p>
      </div>
    `;
  } else {
    res.discrepancies.forEach((d) => {
      const item = document.createElement("div");
      let borderClass = "border-slate-800 bg-slate-900/60";
      let badgeClass = "bg-slate-700 text-slate-300";

      if (d.severity === "CRITICAL") {
        borderClass = "border-rose-500/30 bg-rose-950/20";
        badgeClass = "bg-rose-500/20 text-rose-300 border border-rose-500/30";
      } else if (d.severity === "WARNING") {
        borderClass = "border-amber-500/30 bg-amber-950/20";
        badgeClass = "bg-amber-500/20 text-amber-300 border border-amber-500/30";
      }

      item.className = `p-3.5 rounded-xl border ${borderClass} text-xs space-y-2`;
      item.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${badgeClass}">${d.severity}</span>
            <span class="font-bold text-slate-200">${d.title}</span>
          </div>
          <span class="text-[10px] font-mono text-slate-500">${d.category}</span>
        </div>
        <p class="text-slate-300 text-[11px]">${d.description}</p>
        <div class="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
          <div><span class="text-slate-500">Esperado (Origem):</span> <strong class="text-slate-200">${d.expected_value}</strong></div>
          <div><span class="text-slate-500">Declarado (DUIMP):</span> <strong class="text-rose-300">${d.actual_value}</strong></div>
        </div>
        <div class="text-[11px] text-cyan-300 font-medium flex items-center gap-1.5 pt-1">
          <i data-lucide="arrow-right-circle" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>Ação Recomendada: ${d.suggested_action}</span>
        </div>
      `;
      discContainer.appendChild(item);
    });
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}
