const scenarios = {
  corporate: {
    title: 'Corporate · diligence issue extraction',
    short: 'Corporate diligence',
    summary: 'Surface agreement issues across a deal-room corpus for attorney verification and drafting decisions.',
    fact: 'A transaction team needs faster issue spotting across contracts without surrendering relevance, materiality, or negotiating judgment.',
    knowledge: 'Approved matter corpus, clause taxonomy, document lineage, access controls, and a named knowledge owner.',
    authority: 'Deal attorneys determine legal relevance, materiality, escalation, and the final drafting or negotiating position.',
    evaluation: 'Attorney-reviewed issue set; citation completeness; omission and hallucination review; repeatability across representative documents.',
    adoption: 'Matter kickoff pattern, embedded examples, office hours, feedback capture, and practice KM ownership.',
    value: 'Measured cycle time, rework, issue coverage, repeat use, and client-response speed.',
    treatments: {
      prototype: ['Matter prototype', 'Bounded pilot with attorney review on every output.'],
      practice: ['Practice pattern', 'Prove across representative matters and document the legitimate exceptions.'],
      candidate: ['Cross-practice candidate', 'Test reusable components against another practice fact pattern before standardizing.'],
      standard: ['Firm standard', 'Maintain evaluation, knowledge ownership, exception rules, and retirement criteria.']
    }
  },
  litigation: {
    title: 'Litigation · discovery synthesis',
    short: 'Litigation synthesis',
    summary: 'Build chronology and theme support from a large review set while preserving privilege and strategy authority.',
    fact: 'A litigation team needs a defensible synthesis of documents, chronology, actors, and emerging themes under time pressure.',
    knowledge: 'Matter-authorized collection, privilege boundaries, review coding, document citations, and chain-of-custody context.',
    authority: 'Litigators decide responsiveness, privilege, factual significance, theory of the case, and what reaches the client or court.',
    evaluation: 'Citation validity; factual consistency; privilege leakage tests; theme coverage; reviewer agreement on sampled outputs.',
    adoption: 'Reviewer playbook, escalation path, matter-specific training, and continuous feedback from senior litigators.',
    value: 'Measured review effort, chronology build time, rework, factual coverage, and team confidence.',
    treatments: {
      prototype: ['Matter prototype', 'Use only inside a bounded review lane with heightened supervision.'],
      practice: ['Practice pattern', 'Separate reusable synthesis mechanics from matter-specific privilege and strategy rules.'],
      candidate: ['Cross-practice candidate', 'Reuse citation and chronology controls; do not export matter strategy assumptions.'],
      standard: ['Firm standard', 'Standardize the control pattern, not the legal judgment.']
    }
  },
  regulatory: {
    title: 'Regulatory · monitoring to advisory',
    short: 'Regulatory monitoring',
    summary: 'Turn changing regulatory sources into a traceable attorney-ready update with accountable interpretation.',
    fact: 'A regulatory team must detect change, understand client relevance, and produce timely advice across fast-moving sources.',
    knowledge: 'Approved primary sources, jurisdiction taxonomy, effective dates, client context, and source-refresh ownership.',
    authority: 'Regulatory lawyers interpret applicability, uncertainty, materiality, and the advice delivered to clients.',
    evaluation: 'Source freshness; citation coverage; change-detection recall; jurisdiction accuracy; attorney correction patterns.',
    adoption: 'Practice alerts, client-context prompts, review checkpoints, and shared KM stewardship.',
    value: 'Measured monitoring effort, time to attorney-ready draft, corrections, coverage, and client-response speed.',
    treatments: {
      prototype: ['Matter prototype', 'Test source coverage and change detection before drafting assistance.'],
      practice: ['Practice pattern', 'Define jurisdiction limits, source ownership, and attorney review rules.'],
      candidate: ['Cross-practice candidate', 'Reuse monitoring mechanics where source taxonomies and authority rules align.'],
      standard: ['Firm standard', 'Maintain the source registry and revalidate when law, policy, or models change.']
    }
  },
  whitecollar: {
    title: 'White Collar · investigation chronology',
    short: 'Investigation chronology',
    summary: 'Organize evidence and chronology for sensitive investigations with heightened confidentiality and human control.',
    fact: 'An investigation team needs to connect communications, events, actors, and allegations without compromising privilege or investigative strategy.',
    knowledge: 'Matter-specific access, approved evidence set, privilege and export-control boundaries, provenance, and investigation taxonomy.',
    authority: 'Investigation counsel decides scope, credibility, privilege, legal characterization, escalation, and disclosure.',
    evaluation: 'Evidence citation accuracy; entity and date consistency; privilege controls; access tests; omission review on high-consequence facts.',
    adoption: 'Small authorized cohort, scenario-based training, named escalation owner, and deliberate expansion only after evidence.',
    value: 'Measured chronology effort, correction burden, issue coverage, response speed, and defensibility signals.',
    treatments: {
      prototype: ['Matter prototype', 'Heightened controls, narrow access, and no autonomous consequential action.'],
      practice: ['Practice pattern', 'Capture the technical pattern while keeping matter-specific access and strategy local.'],
      candidate: ['Cross-practice candidate', 'Transfer provenance and chronology controls, not investigative assumptions.'],
      standard: ['Firm standard', 'Standardize only the controls that remain defensible across sensitive matters.']
    }
  }
};

let currentScenario = 'corporate';
let currentStage = 'practice';
let renderToken = 0;

const byId = (id) => document.getElementById(id);
const all = (selector) => Array.from(document.querySelectorAll(selector));

function updateText(id, value) {
  const node = byId(id);
  if (node) node.textContent = value;
}

function renderState({ animate = true } = {}) {
  const token = ++renderToken;
  const scenario = scenarios[currentScenario];
  const [disposition, nextDecision] = scenario.treatments[currentStage];

  const fields = {
    scenarioTitle: scenario.title,
    scenarioSummary: scenario.summary,
    fact: scenario.fact,
    knowledge: scenario.knowledge,
    authority: scenario.authority,
    evaluation: scenario.evaluation,
    adoption: scenario.adoption,
    value: scenario.value,
    recordDisposition: disposition,
    nextDecision
  };
  Object.entries(fields).forEach(([id, value]) => updateText(id, value));
  document.querySelectorAll('[data-field="sphereLabel"]').forEach((node) => { node.textContent = scenario.short; });
  document.querySelectorAll('[data-field="disposition"]').forEach((node) => { node.textContent = disposition; });

  all('.scenario-button').forEach((button) => {
    const selected = button.dataset.scenario === currentScenario;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  all('.treatment-controls button').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.stage === currentStage));
  });

  const sphere = byId('sphereStage');
  if (sphere) {
    sphere.dataset.scenario = currentScenario;
    sphere.setAttribute('aria-label', `Living precedent sphere. ${scenario.short} workflow selected. ${disposition}.`);
  }

  const layers = all('.record-grid section');
  layers.forEach((layer) => layer.classList.remove('resolved'));
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!animate || reducedMotion) {
    layers.forEach((layer) => layer.classList.add('resolved'));
  } else {
    layers.forEach((layer, index) => {
      window.setTimeout(() => {
        if (token === renderToken) layer.classList.add('resolved');
      }, 85 + index * 75);
    });
  }

  const announcement = byId('stateAnnouncement');
  if (announcement) announcement.textContent = `${scenario.title}. ${disposition}. ${nextDecision}`;
}

all('.scenario-button').forEach((button) => {
  button.addEventListener('click', () => {
    currentScenario = button.dataset.scenario;
    renderState();
  });
  button.addEventListener('keydown', (event) => {
    if (!['ArrowDown', 'ArrowUp', 'ArrowRight', 'ArrowLeft'].includes(event.key)) return;
    event.preventDefault();
    const buttons = all('.scenario-button');
    const currentIndex = buttons.indexOf(button);
    const delta = ['ArrowDown', 'ArrowRight'].includes(event.key) ? 1 : -1;
    const next = buttons[(currentIndex + delta + buttons.length) % buttons.length];
    next.focus();
    next.click();
  });
});

all('.treatment-controls button').forEach((button) => {
  button.addEventListener('click', () => {
    currentStage = button.dataset.stage;
    renderState();
  });
});

byId('resetStudio')?.addEventListener('click', () => {
  currentScenario = 'corporate';
  currentStage = 'practice';
  renderState();
  all('.scenario-button')[0]?.focus();
});

const menuButton = byId('menuButton');
const siteMenu = byId('siteMenu');
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!open));
  siteMenu?.classList.toggle('open', !open);
});
siteMenu?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  menuButton?.setAttribute('aria-expanded', 'false');
  siteMenu.classList.remove('open');
}));

const header = document.querySelector('.site-header');
const syncHeader = () => header?.classList.toggle('scrolled', window.scrollY > 30);
window.addEventListener('scroll', syncHeader, { passive: true });
syncHeader();

renderState({ animate: true });
