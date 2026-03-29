const apiBase = `${window.location.protocol}//${window.location.hostname}:8000/api`;

async function request(path, options = {}) {
  const res = await fetch(`${apiBase}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

function scriptCard(script) {
  const wrapper = document.createElement('div');
  wrapper.className = 'card';

  wrapper.innerHTML = `
    <h3>${script.name}</h3>
    <div class="row">Статус: <strong>${script.running ? 'running' : 'paused'}</strong></div>
    <div class="row">
      <label>Cron:</label>
      <input value="${script.cron}" data-role="cron-input" />
      <button class="refresh" data-role="save-cron">Сохранить cron</button>
    </div>
    <div class="row">
      <button class="start" data-role="start">Запустить</button>
      <button class="pause" data-role="pause">Пауза</button>
      <button class="refresh" data-role="logs">Показать логи</button>
    </div>
    <pre data-role="logs-output">Логи не загружены</pre>
  `;

  const cronInput = wrapper.querySelector('[data-role="cron-input"]');

  wrapper.querySelector('[data-role="save-cron"]').onclick = async () => {
    try {
      await request(`/scripts/${script.name}/cron`, {
        method: 'PUT',
        body: JSON.stringify({ cron: cronInput.value.trim() }),
      });
      await loadScripts();
      alert('Cron успешно обновлён');
    } catch (e) {
      alert(`Не удалось сохранить cron: ${e.message}`);
    }
  };

  wrapper.querySelector('[data-role="start"]').onclick = async () => {
    await request(`/scripts/${script.name}/start`, { method: 'POST' });
    await loadScripts();
  };

  wrapper.querySelector('[data-role="pause"]').onclick = async () => {
    await request(`/scripts/${script.name}/pause`, { method: 'POST' });
    await loadScripts();
  };

  wrapper.querySelector('[data-role="logs"]').onclick = async () => {
    const logs = await request(`/scripts/${script.name}/logs?limit=20`);
    const output = logs.map((log) => `[${log.created_at}] ${log.status}\n${log.output}`).join('\n\n');
    wrapper.querySelector('[data-role="logs-output"]').textContent = output || 'Логи отсутствуют';
  };

  return wrapper;
}

async function loadScripts() {
  const scripts = await request('/scripts');
  const root = document.getElementById('scripts');
  root.innerHTML = '';
  scripts.forEach((script) => root.appendChild(scriptCard(script)));
}

loadScripts().catch((e) => {
  const root = document.getElementById('scripts');
  root.innerHTML = `<div class="card">Ошибка загрузки: ${e.message}</div>`;
});
