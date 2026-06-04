(function () {
  "use strict";

  const SVG = {
    book: `<svg class="estante-icone" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.966 8.966 0 0 0-6 2.292m0-14.25v14.25"/></svg>`,
    search: `<svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="m21 21-4.35-4.35"/></svg>`,
    plus: `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" d="M12 5v14M5 12h14"/></svg>`,
    upload: `<svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 16v1a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-1m-4-8-4-4m0 0L8 8m4-4v12"/></svg>`,
    x: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M18 6 6 18M6 6l12 12"/></svg>`,
    trash: `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M3 6h18m-2 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`,
    link: `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6m4-3h6v6m-11 5L21 3"/></svg>`,
  };

  const CORES = ["#8B2635", "#1A4A7A", "#2D6A4F", "#5C3A1E", "#4A3060", "#7A4A00", "#1A5C5C", "#6B3A2A", "#3A5C1A", "#5C1A3A", "#8B6914", "#2A4A6B"];
  const ALTURAS = [180, 200, 215, 190, 220, 175, 205];
  const SHELF_CAP = 12;
  const API = window.API || { addBook: '/estante/api/livros', deleteBookPrefix: '/estante/api/deletar/' };

  let books = [];
  let search = "";
  let corSelecionada = CORES[0];
  let pdfSelecionado = null;

  function shadeHex(hex, amt) {
    const n = parseInt(hex.replace('#', ''), 16);
    const r = Math.min(255, Math.max(0, (n >> 16) + amt * 2));
    const g = Math.min(255, Math.max(0, ((n >> 8) & 0xff) + amt * 2));
    const b = Math.min(255, Math.max(0, (n & 0xff) + amt * 2));
    return '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
  }

  function hashNum(id, arr) {
    const text = String(id);
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) >>> 0;
    return arr[h % arr.length];
  }

  function bookColors(book) {
    const base = book.color || hashNum(book.id, CORES);
    return { spine: base, side: shadeHex(base, -20), top: shadeHex(base, 10) };
  }

  function normalizeBook(book) {
    const id = String(book.id);
    return {
      id,
      title: book.title || book.titulo || 'Sem título',
      author: book.author || book.autor || 'Autor desconhecido',
      color: book.color || book.cor || hashNum(id, CORES),
      pdfUrl: book.pdfUrl || '',
      pdfName: book.pdfName || '',
      addedAt: book.addedAt || ''
    };
  }

  function renderLombada(book) {
    const c = bookColors(book);
    const h = hashNum(book.id, ALTURAS);
    const sw = 36;
    const dep = 22;
    const titleSize = Math.min(12, Math.max(9, sw / 3.5));
    const wrap = document.createElement('div');
    wrap.className = 'livro-wrap';
    wrap.style.cssText = `width:${sw + dep}px;height:${h + 12}px;`;
    wrap.title = `${book.title} — ${book.author}`;
    wrap.innerHTML = `
      <div class="livro-3d" style="position:absolute;bottom:0;width:${sw + dep}px;height:${h}px;">
        <div class="livro-spine" style="width:${sw}px;height:${h}px;background:linear-gradient(to right,${c.side} 0%,${c.spine} 30%,${c.spine} 70%,${shadeHex(c.spine, -10)} 100%);box-shadow:inset -3px 0 6px rgba(0,0,0,0.4),inset 3px 0 4px rgba(255,255,255,0.08);">
          <div class="livro-deco-top"></div>
          <div class="livro-deco-top" style="top:14px;opacity:0.25;"></div>
          <div class="livro-deco-bottom"></div>
          <div class="livro-spine-texto">
            <span class="livro-spine-titulo" style="font-size:${titleSize}px;">${book.title}</span>
            <span class="livro-spine-autor">${book.author}</span>
          </div>
        </div>
        <div class="livro-lado" style="width:${dep}px;height:${h}px;background:linear-gradient(to bottom,${c.top} 0%,${c.side} 100%);"></div>
        <div class="livro-topo" style="width:${sw}px;height:${dep * 0.5}px;top:${-dep * 0.4}px;background:${c.top};transform:skewX(-45deg) translateX(${dep * 0.5}px);border-bottom:1px solid rgba(0,0,0,0.2);"></div>
      </div>
      <div class="livro-tooltip">${book.title}</div>`;
    if (book.pdfUrl) wrap.addEventListener('click', () => abrirLeitor(book));
    return wrap;
  }

  function renderEstante() {
    const main = document.getElementById('estante-main');
    if (!main) return;
    main.innerHTML = '';
    const filtered = books.filter(b =>
      b.title.toLowerCase().includes(search.toLowerCase()) ||
      b.author.toLowerCase().includes(search.toLowerCase())
    );
    const sub = document.getElementById('estante-subtitulo');
    if (sub) sub.textContent = `${books.length} ${books.length === 1 ? 'livro' : 'livros'} na coleção`;
    if (filtered.length === 0) {
      main.innerHTML = `<div class="estante-vazia">${search ? 'Nenhum livro encontrado.' : 'Sua estante aguarda o primeiro livro.'}</div>`;
      return;
    }
    const rows = [];
    for (let i = 0; i < filtered.length; i += SHELF_CAP) rows.push(filtered.slice(i, i + SHELF_CAP));
    rows.forEach((rowBooks, rowIndex) => {
      const shelf = document.createElement('div');
      shelf.className = 'prateleira';
      shelf.dataset.label = `Prateleira ${rowIndex + 1}`;
      const livrosDiv = document.createElement('div'); livrosDiv.className = 'prateleira-livros';
      rowBooks.forEach(b => livrosDiv.appendChild(renderLombada(b)));
      shelf.appendChild(livrosDiv);
      const tabua = document.createElement('div'); tabua.className = 'tabua'; shelf.appendChild(tabua);
      const suportes = document.createElement('div'); suportes.className = 'tabua-suportes';
      for (let i = 0; i < 5; i++) { const s = document.createElement('div'); s.className = 'suporte'; suportes.appendChild(s); }
      shelf.appendChild(suportes);
      main.appendChild(shelf);
    });
    if (books.some(b => !b.pdfUrl) && !search) {
      const hint = document.createElement('p'); hint.className = 'estante-hint';
      hint.textContent = 'Alguns livros não têm PDF ainda — faça upload para poder lê-los.';
      main.appendChild(hint);
    }
  }

  function abrirModalAdicionar() {
    corSelecionada = CORES[0];
    pdfSelecionado = null;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay'; overlay.id = 'modal-adicionar';
    overlay.innerHTML = `
      <div class="modal-box">
        <div class="modal-header">
          <div class="modal-header-left">${SVG.book}<h2>Adicionar Livro</h2></div>
          <button class="modal-fechar" id="modal-fechar-btn">${SVG.x}</button>
        </div>
        <div class="drop-zone" id="drop-zone">
          ${SVG.upload}
          <p id="drop-texto">Arraste um PDF ou clique para selecionar</p>
          <input type="file" accept="application/pdf" id="pdf-input" style="display:none">
        </div>
        <div class="campo"><label>Título *</label><input type="text" id="campo-titulo" placeholder="Nome do livro"></div>
        <div class="campo"><label>Autor</label><input type="text" id="campo-autor" placeholder="Nome do autor"></div>
        <div class="campo"><label>Cor da lombada</label><div class="cores-grid" id="cores-grid"></div></div>
        <button class="btn-submit" id="btn-submit" disabled>Adicionar à Estante</button>
      </div>`;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', e => { if (e.target === overlay) fecharModal(); });
    document.getElementById('modal-fechar-btn').addEventListener('click', fecharModal);
    const dropZone = document.getElementById('drop-zone');
    const pdfInput = document.getElementById('pdf-input');
    dropZone.addEventListener('click', () => pdfInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      const f = e.dataTransfer.files[0];
      if (f && f.type === 'application/pdf') selecionarPdf(f);
    });
    pdfInput.addEventListener('change', e => { if (e.target.files[0]) selecionarPdf(e.target.files[0]); });
    const coresGrid = document.getElementById('cores-grid');
    CORES.forEach(cor => {
      const btn = document.createElement('button');
      btn.className = 'cor-btn' + (cor === corSelecionada ? ' ativa' : '');
      btn.style.background = cor;
      btn.addEventListener('click', () => {
        corSelecionada = cor;
        coresGrid.querySelectorAll('.cor-btn').forEach(b => b.classList.remove('ativa'));
        btn.classList.add('ativa');
      });
      coresGrid.appendChild(btn);
    });
    document.getElementById('campo-titulo').addEventListener('input', verificarFormulario);
    document.getElementById('btn-submit').addEventListener('click', submitLivro);
  }

  function selecionarPdf(file) {
    pdfSelecionado = file;
    const p = document.getElementById('drop-texto');
    p.textContent = '📄 ' + file.name;
    p.classList.add('arquivo-ok');
    const t = document.getElementById('campo-titulo');
    if (!t.value) {
      const n = file.name.replace(/\.pdf$/i, '').replace(/[-_]/g, ' ');
      t.value = n.charAt(0).toUpperCase() + n.slice(1);
    }
    verificarFormulario();
  }

  function verificarFormulario() {
    const t = document.getElementById('campo-titulo')?.value.trim();
    const btn = document.getElementById('btn-submit');
    if (btn) btn.disabled = !(t && pdfSelecionado);
  }

  function submitLivro() {
    const titulo = document.getElementById('campo-titulo').value.trim();
    const autor = document.getElementById('campo-autor').value.trim() || 'Autor desconhecido';
    if (!titulo || !pdfSelecionado) return;
    const btn = document.getElementById('btn-submit');
    btn.disabled = true;
    btn.textContent = 'Adicionando...';
    const formData = new FormData();
    formData.append('titulo', titulo);
    formData.append('autor', autor);
    formData.append('color', corSelecionada);
    formData.append('pdf', pdfSelecionado);

    fetch(API.addBook, { method: 'POST', body: formData })
      .then(async response => {
        const data = await response.json();
        if (!response.ok || !data.success) {
          throw new Error(data.error || 'Não foi possível adicionar o livro.');
        }
        return data.book;
      })
      .then(book => {
        books.unshift(normalizeBook(book));
        fecharModal();
        renderEstante();
      })
      .catch(error => {
        alert(error.message);
      })
      .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Adicionar à Estante';
      });
  }

  function fecharModal() {
    const modal = document.getElementById('modal-adicionar');
    if (modal) modal.remove();
  }

  function abrirLeitor(book) {
    const overlay = document.createElement('div');
    overlay.className = 'leitor-overlay';
    overlay.innerHTML = `
      <div class="leitor-topo">
        <div class="leitor-info"><h2>${book.title}</h2><p>${book.author}</p></div>
        <div class="leitor-acoes">
          <a href="${book.pdfUrl}" download="${book.pdfName || book.title}.pdf" class="btn-icone" style="color:#c8923a;">${SVG.link}</a>
          <button class="btn-icone" style="color:#c05040;" id="btn-remover">${SVG.trash}</button>
          <button class="btn-icone" style="color:#a08060;" id="btn-fechar-leitor">${SVG.x}</button>
        </div>
      </div>
      <iframe class="leitor-iframe" src="${book.pdfUrl}" title="${book.title}"></iframe>`;
    document.body.appendChild(overlay);
    document.getElementById('btn-fechar-leitor').addEventListener('click', () => overlay.remove());
    document.getElementById('btn-remover').addEventListener('click', () => {
      if (confirm(`Remover "${book.title}" da estante?`)) {
        fetch(`${API.deleteBookPrefix}${book.id}`, { method: 'POST' })
          .then(async response => {
            const data = await response.json();
            if (!response.ok || !data.success) {
              throw new Error(data.error || 'Falha ao deletar o livro.');
            }
            books = books.filter(b => b.id !== book.id);
            overlay.remove();
            renderEstante();
          })
          .catch(error => alert(error.message));
      }
    });
  }

  function montarHeader(root) {
    const header = document.createElement('header');
    header.className = 'estante-header';
    header.innerHTML = `
      <div class="estante-titulo">${SVG.book}<h1>Minha Estante</h1></div>
      <p class="estante-subtitulo" id="estante-subtitulo">0 livros na coleção</p>
      <div class="estante-controles">
        <div class="estante-busca-wrap">${SVG.search}<input class="estante-busca" type="text" placeholder="Buscar título ou autor..." id="estante-busca"></div>
        <button class="btn-adicionar" id="btn-adicionar">${SVG.plus} Adicionar</button>
      </div>`;
    root.appendChild(header);
    document.getElementById('btn-adicionar').addEventListener('click', abrirModalAdicionar);
    document.getElementById('estante-busca').addEventListener('input', e => { search = e.target.value; renderEstante(); });
  }

  function init() {
    const root = document.getElementById('minha-estante');
    if (!root) return;
    books = (window.INITIAL_LIVROS || []).map(normalizeBook);
    montarHeader(root);
    const main = document.createElement('main');
    main.className = 'estante-main';
    main.id = 'estante-main';
    root.appendChild(main);
    renderEstante();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
