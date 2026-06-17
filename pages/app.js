// Bio Event Calendar client: API-first locally, static JSON fallback on GitHub Pages.
const api = {
  async load(params) {
    const query = new URLSearchParams(params).toString();
    try {
      const res = await fetch('/api/bio-events?' + query);
      if (res.ok) return await res.json();
    } catch (_) {
      // GitHub Pages has no Python API; fall through to static JSON.
    }
    const staticUrl = new URL('data/bio_events.json', window.location.href);
    const staticRes = await fetch(staticUrl, { cache: 'no-store' });
    if (!staticRes.ok) throw new Error(`Static data load failed: ${staticRes.status}`);
    const data = await staticRes.json();
    return { ...data, events: filterStatic(data.events, params) };
  }
};

function filterStatic(events, params) {
  return events.filter((e) => {
    if (params.date_from && e.event_date < params.date_from) return false;
    if (params.date_to && e.event_date > params.date_to) return false;
    if (params.ticker && e.ticker.toUpperCase() !== params.ticker.toUpperCase()) return false;
    if (params.market && e.market.toUpperCase() !== params.market.toUpperCase()) return false;
    if (params.event_type && e.event_type !== params.event_type) return false;
    if (params.confidence_level && e.confidence_level !== params.confidence_level.toUpperCase()) return false;
    return !params.confidence_level ? ['A', 'B'].includes(e.confidence_level) : true;
  });
}

function values() {
  const params = {};
  for (const id of ['date_from', 'date_to', 'ticker', 'market', 'event_type', 'confidence_level']) {
    const element = document.getElementById(id);
    const value = element.value.trim();
    if (value) params[id] = value;
  }
  return params;
}

async function loadEvents() {
  let data;
  try {
    data = await api.load(values());
  } catch (error) {
    document.getElementById('meta').textContent = `데이터 로딩 실패: ${error.message}`;
    return;
  }
  const meta = document.getElementById('meta');
  meta.textContent = `데이터: ${data.source_mode || 'API'} · 생성/갱신: ${(data.generated_at || new Date().toISOString()).slice(0, 19)}`;
  const root = document.getElementById('events');
  root.innerHTML = data.events.length ? '' : '<div class="card">조회된 이벤트가 없습니다.</div>';
  for (const e of data.events) {
    const el = document.createElement('article');
    el.className = 'card event';
    el.innerHTML = `<div class="date">${e.event_date}</div><div><div><span class="badge">${e.event_type}</span> <span class="badge">신뢰도 ${e.confidence_level}</span></div><h3>${e.summary_ko}</h3><p class="muted">${e.company_name} (${e.ticker}, ${e.market}) · ${e.product_name} · ${e.condition_name} · ${e.clinical_phase}</p><a class="source" href="${e.source_url}" target="_blank" rel="noreferrer">${e.source} 원천 보기</a></div><div class="muted">업데이트<br>${e.last_updated_at.slice(0, 10)}</div>`;
    root.appendChild(el);
  }
}

document.getElementById('load').addEventListener('click', loadEvents);
loadEvents();
