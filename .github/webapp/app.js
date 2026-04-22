const state = {
  jobs: [],
  filteredJobs: [],
  activeMode: "all",
  searchTerm: "",
};

const elements = {
  jobsFileStatus: document.getElementById("jobs-file-status"),
  jobsSearchStatus: document.getElementById("jobs-search-status"),
  activeFilterLabel: document.getElementById("active-filter-label"),
  activeSearchLabel: document.getElementById("active-search-label"),
  metricAll: document.getElementById("metric-all"),
  metricRemote: document.getElementById("metric-remote"),
  metricHybrid: document.getElementById("metric-hybrid"),
  metricOnsite: document.getElementById("metric-onsite"),
  searchInput: document.getElementById("search-input"),
  filterButtons: Array.from(document.querySelectorAll(".filter-btn")),
  companiesList: document.getElementById("companies-list"),
  locationsList: document.getElementById("locations-list"),
  jobsGrid: document.getElementById("jobs-grid"),
  emptyState: document.getElementById("empty-state"),
  resultsCount: document.getElementById("results-count"),
  donutChart: document.getElementById("donut-chart"),
  refreshButton: document.getElementById("refresh-btn"),
  resultsBadge: document.getElementById("results-badge"),
  template: document.getElementById("job-card-template"),
};

const modeLabels = {
  all: "Todas",
  remote: "Remota",
  hybrid: "Hibrida",
  onsite: "Presencial",
  unknown: "Nao classificada",
};

async function bootstrap() {
  bindEvents();
  await loadDashboard();
}

function bindEvents() {
  elements.searchInput.addEventListener("input", (event) => {
    state.searchTerm = event.target.value.trim().toLowerCase();
    renderJobs();
  });

  elements.filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.activeMode = button.dataset.mode;
      elements.filterButtons.forEach((item) => item.classList.toggle("active", item === button));
      updateActiveControls();
      renderJobs();
    });
  });

  elements.refreshButton.addEventListener("click", async () => {
    elements.jobsSearchStatus.textContent = "Atualizando dados...";
    elements.resultsBadge.textContent = "Sincronizando";
    await loadDashboard();
  });
}

async function loadDashboard() {
  const response = await fetch("/api/summary", { cache: "no-store" });
  const payload = await response.json();
  state.jobs = payload.jobs ?? [];

  updateMeta(payload.meta);
  updateSummary(payload.summary);
  updateActiveControls();
  renderJobs();
}

function updateMeta(meta) {
  elements.jobsFileStatus.textContent = meta.exists ? meta.jobs_path : "Arquivo ainda nao existe";
  elements.jobsSearchStatus.textContent = meta.exists
    ? "Dados carregados do JSON atual"
    : "Gere uma coleta para alimentar o painel";
}

function updateSummary(summary) {
  const totals = summary?.totals ?? {};
  elements.metricAll.textContent = totals.all ?? 0;
  elements.metricRemote.textContent = totals.remote ?? 0;
  elements.metricHybrid.textContent = totals.hybrid ?? 0;
  elements.metricOnsite.textContent = totals.onsite ?? 0;

  renderStackList(elements.companiesList, summary?.top_companies ?? []);
  renderStackList(elements.locationsList, summary?.top_locations ?? []);
  renderDonutChart(totals);
}

function renderStackList(container, items) {
  container.replaceChildren();

  if (!items.length) {
    const empty = document.createElement("p");
    empty.textContent = "Sem dados suficientes ainda.";
    container.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "stack-item";

    const label = document.createElement("strong");
    label.textContent = item.label;

    const count = document.createElement("span");
    count.textContent = item.count;

    row.append(label, count);
    container.appendChild(row);
  });
}

function renderDonutChart(totals) {
  const remote = totals.remote ?? 0;
  const hybrid = totals.hybrid ?? 0;
  const onsite = totals.onsite ?? 0;
  const unknown = totals.unknown ?? 0;
  const total = Math.max(remote + hybrid + onsite + unknown, 1);

  const remoteStop = percentage(remote, total);
  const hybridStop = remoteStop + percentage(hybrid, total);
  const onsiteStop = hybridStop + percentage(onsite, total);
  const unknownStop = 100;

  elements.donutChart.style.background = `conic-gradient(
    var(--remote) 0% ${remoteStop}%,
    var(--hybrid) ${remoteStop}% ${hybridStop}%,
    var(--onsite) ${hybridStop}% ${onsiteStop}%,
    var(--unknown) ${onsiteStop}% ${unknownStop}%
  )`;
  elements.donutChart.dataset.center = `${totals.all ?? 0}\n vagas`;
}

function renderJobs() {
  const filtered = state.jobs.filter((job) => {
    const matchesMode = state.activeMode === "all" || job.work_mode === state.activeMode;
    if (!matchesMode) {
      return false;
    }

    if (!state.searchTerm) {
      return true;
    }

    const searchable = `${job.title} ${job.company} ${job.location}`.toLowerCase();
    return searchable.includes(state.searchTerm);
  });

  state.filteredJobs = filtered;
  elements.jobsGrid.replaceChildren();
  elements.resultsCount.textContent = `${filtered.length} vaga(s) visiveis`;
  elements.resultsBadge.textContent = filtered.length ? "Resultados filtrados" : "Sem correspondencias";
  elements.emptyState.classList.toggle("hidden", filtered.length > 0 || state.jobs.length > 0);

  if (!state.jobs.length) {
    return;
  }

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = "<h3>Nenhum resultado com esse filtro.</h3><p>Troque a busca de texto ou a modalidade selecionada.</p>";
    elements.jobsGrid.appendChild(empty);
    return;
  }

  filtered.forEach((job, index) => {
    const node = elements.template.content.firstElementChild.cloneNode(true);
    node.querySelector(".mode-pill").textContent = modeLabels[job.work_mode] ?? modeLabels.unknown;
    node.querySelector(".mode-pill").classList.add(job.work_mode);
    node.querySelector(".job-index").textContent = `#${index + 1}`;
    node.querySelector(".job-title").textContent = job.title || "Sem titulo";
    node.querySelector(".job-company").textContent = job.company || "Empresa nao informada";
    node.querySelector(".job-location").textContent = job.location || "Localizacao nao informada";
    node.querySelector(".job-source").textContent = trimSource(job.source_file);

    const link = node.querySelector(".job-link");
    if (job.url) {
      link.href = job.url;
    } else {
      link.removeAttribute("href");
      link.textContent = "Sem link";
      link.setAttribute("aria-disabled", "true");
    }

    elements.jobsGrid.appendChild(node);
  });
}

function updateActiveControls() {
  elements.activeFilterLabel.textContent = state.activeMode === "all"
    ? "Todas as vagas"
    : modeLabels[state.activeMode] ?? "Filtro customizado";

  elements.activeSearchLabel.textContent = state.searchTerm
    ? `Termo: ${state.searchTerm}`
    : "Sem termo aplicado";
}

function trimSource(source) {
  if (!source) {
    return "sem origem";
  }
  return source.length > 42 ? `${source.slice(0, 39)}...` : source;
}

function percentage(value, total) {
  return Number(((value / total) * 100).toFixed(2));
}

bootstrap().catch((error) => {
  elements.jobsSearchStatus.textContent = "Falha ao carregar dados";
  elements.jobsFileStatus.textContent = error.message;
});
