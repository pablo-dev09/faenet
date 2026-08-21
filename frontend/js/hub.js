/* =====================================================
   FaeNet - hub.js
   Hub do Curso: estagios, provas e forum de duvidas.
   ===================================================== */

(function (global) {
    'use strict';

    const Hub = {
        currentCurso: '',
        currentTab: 'estagio',

        async render(container) {
            const me = FaeAuth.currentUser;
            if (!me) return;

            // Pega o curso padrao do usuario.
            this.currentCurso = me.curso || 'Informatica';

            // Cabecalho + seletor de curso
            const header = FaeUtils.el('div', { class: 'page-header' },
                FaeUtils.el('div', {},
                    FaeUtils.el('h1', { class: 'page-header__title' }, 'Hub do Curso'),
                    FaeUtils.el('div', { class: 'page-header__subtitle' }, 'Estagios, provas e forum de duvidas da sua turma.'),
                ),
                FaeUtils.el('div', { class: 'flex gap-1' },
                    FaeUtils.el('select', { class: 'field__input', style: { width: '180px' }, id: 'hub-curso' },
                        ['Informatica', 'Administracao', 'Enfermagem', 'Mecanica', 'Eletrotecnica', 'Outro']
                            .map(c => FaeUtils.el('option', { value: c, selected: c === this.currentCurso }, c)),
                    ),
                    FaeUtils.el('button', { class: 'btn btn--primary', id: 'hub-new' }, '+ Novo'),
                ),
            );
            container.appendChild(header);

            // Tabs
            const tabs = FaeUtils.el('div', { class: 'tabs' });
            const tabDefs = [
                { key: 'estagio', label: 'Estagios' },
                { key: 'prova', label: 'Provas' },
                { key: 'forum_topic', label: 'Forum' },
            ];
            tabDefs.forEach(t => {
                const b = FaeUtils.el('button', { class: 'tab' + (t.key === this.currentTab ? ' is-active' : ''), data: { key: t.key } }, t.label);
                b.addEventListener('click', () => {
                    this.currentTab = t.key;
                    tabs.querySelectorAll('.tab').forEach(x => x.classList.remove('is-active'));
                    b.classList.add('is-active');
                    loadList();
                });
                tabs.appendChild(b);
            });
            container.appendChild(tabs);

            const listArea = FaeUtils.el('div', { class: 'hub-list' });
            container.appendChild(listArea);

            const cursoSelect = header.querySelector('#hub-curso');
            cursoSelect.addEventListener('change', () => {
                this.currentCurso = cursoSelect.value;
                loadList();
            });
            header.querySelector('#hub-new').addEventListener('click', () => this.openCreate());

            const loadList = async () => {
                listArea.innerHTML = '';
                listArea.appendChild(FaeUtils.el('div', { class: 'skeleton', style: { height: '120px' } }));
                try {
                    const items = await FaeAPI.hubList(this.currentTab, { curso: this.currentCurso, limit: 50 });
                    listArea.innerHTML = '';
                    if (!items.length) {
                        listArea.appendChild(FaeUtils.el('div', { class: 'empty' },
                            `Nenhum item em ${this.currentCurso}. Que tal publicar o primeiro?`,
                        ));
                        return;
                    }
                    items.forEach(i => {
                        if (this.currentTab === 'forum_topic') {
                            listArea.appendChild(this.renderForumTopic(i));
                        } else if (this.currentTab === 'estagio') {
                            listArea.appendChild(this.renderEstagio(i));
                        } else if (this.currentTab === 'prova') {
                            listArea.appendChild(this.renderProva(i));
                        }
                    });
                } catch (e) {
                    listArea.innerHTML = '';
                    FaeUtils.error(e.message);
                }
            };
            loadList();
        },

        openCreate() {
            const me = FaeAuth.currentUser;
            const wrap = FaeUtils.el('div', {});
            let tipo = this.currentTab === 'forum_topic' ? 'forum_topic' : this.currentTab;

            const selectTipo = FaeUtils.el('select', { class: 'field__input' },
                FaeUtils.el('option', { value: 'estagio', selected: tipo === 'estagio' }, 'Estagio'),
                FaeUtils.el('option', { value: 'prova', selected: tipo === 'prova' }, 'Prova / Aviso'),
                FaeUtils.el('option', { value: 'forum_topic', selected: tipo === 'forum_topic' }, 'Topico de Forum'),
            );
            selectTipo.addEventListener('change', () => { tipo = selectTipo.value; refreshBody(); });
            wrap.appendChild(FaeUtils.el('div', { class: 'field' },
                FaeUtils.el('span', { class: 'field__label' }, 'Tipo'),
                selectTipo,
            ));
            wrap.appendChild(FaeUtils.el('div', { class: 'field' },
                FaeUtils.el('span', { class: 'field__label' }, 'Curso'),
                FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'curso', value: this.currentCurso, maxlength: 80, required: true }),
            ));

            const body = FaeUtils.el('div', {});
            wrap.appendChild(body);

            function refreshBody() {
                FaeUtils.clear(body);
                body.appendChild(FaeUtils.el('div', { class: 'field' },
                    FaeUtils.el('span', { class: 'field__label' }, 'Titulo'),
                    FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'title', maxlength: 200, required: true }),
                ));
                if (tipo === 'estagio') {
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Empresa'),
                        FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'empresa', maxlength: 120 }),
                    ));
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Prazo (AAAA-MM-DD)'),
                        FaeUtils.el('input', { class: 'field__input', type: 'date', name: 'prazo' }),
                    ));
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Link'),
                        FaeUtils.el('input', { class: 'field__input', type: 'url', name: 'link', placeholder: 'https://...' }),
                    ));
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Tags (separadas por virgula)'),
                        FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'tags' }),
                    ));
                } else if (tipo === 'prova') {
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Disciplina'),
                        FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'disciplina', maxlength: 120 }),
                    ));
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Data (AAAA-MM-DD)'),
                        FaeUtils.el('input', { class: 'field__input', type: 'date', name: 'data' }),
                    ));
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Conteudo'),
                        FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'conteudo' }),
                    ));
                } else if (tipo === 'forum_topic') {
                    body.appendChild(FaeUtils.el('div', { class: 'field' },
                        FaeUtils.el('span', { class: 'field__label' }, 'Tags (opcional)'),
                        FaeUtils.el('input', { class: 'field__input', type: 'text', name: 'tags' }),
                    ));
                }
                body.appendChild(FaeUtils.el('div', { class: 'field' },
                    FaeUtils.el('span', { class: 'field__label' }, 'Descricao'),
                    FaeUtils.el('textarea', { class: 'field__textarea', name: 'content', maxlength: 8000 }),
                ));
            }
            refreshBody();

            const modal = FaeUtils.openModal({
                title: 'Publicar no Hub',
                body: wrap,
                footer: [
                    FaeUtils.el('button', { class: 'btn btn--ghost', onclick: () => modal.close() }, 'Cancelar'),
                    FaeUtils.el('button', { class: 'btn btn--primary', onclick: async () => {
                        const f = wrap;
                        const payload = {
                            item_type: tipo,
                            curso: f.querySelector('input[name="curso"]').value.trim() || this.currentCurso,
                            title: f.querySelector('input[name="title"]')?.value.trim(),
                            content: f.querySelector('textarea[name="content"]')?.value.trim(),
                        };
                        const extra = {};
                        ['empresa', 'prazo', 'link', 'tags', 'disciplina', 'data', 'conteudo'].forEach(k => {
                            const el = f.querySelector(`input[name="${k}"]`);
                            if (el && el.value) extra[k] = el.value.trim();
                        });
                        if (Object.keys(extra).length) payload.extra = extra;
                        if (!payload.title && tipo !== 'forum_topic') {
                            FaeUtils.error('Titulo obrigatorio.'); return;
                        }
                        try {
                            await FaeAPI.hubCreate(payload);
                            FaeUtils.success('Publicado no Hub!');
                            modal.close();
                            window.FaeApp.refresh();
                        } catch (e) { FaeUtils.error(e.message); }
                    } }, 'Publicar'),
                ],
            });
        },

        renderEstagio(i) {
            const card = FaeUtils.el('div', { class: 'hub-item' },
                FaeUtils.el('div', { class: 'hub-item__tag hub-item__tag--estagio' }, 'Estagio'),
                FaeUtils.el('h3', { class: 'hub-item__title' }, i.title || ''),
            );
            const extra = FaeUtils.el('div', { class: 'hub-item__extra' });
            const e = i.extra || {};
            if (e.empresa) extra.appendChild(FaeUtils.el('span', {}, `🏢 ${e.empresa}`));
            if (e.prazo) extra.appendChild(FaeUtils.el('span', {}, `⏰ Prazo: ${e.prazo}`));
            if (e.tags) extra.appendChild(FaeUtils.el('span', {}, `# ${e.tags}`));
            card.appendChild(extra);
            if (i.content) card.appendChild(FaeUtils.el('div', { class: 'hub-item__content' }, i.content));
            const meta = FaeUtils.el('div', { class: 'hub-item__meta' });
            meta.appendChild(FaeUtils.el('span', {}, `📚 ${i.curso}`));
            meta.appendChild(FaeUtils.el('span', {}, `👤 ${i.author ? i.author.username : i.username}`));
            meta.appendChild(FaeUtils.el('span', {}, FaeUtils.timeAgo(i.timestamp)));
            card.appendChild(meta);
            if (e.link) {
                card.appendChild(FaeUtils.el('a', { class: 'btn btn--ghost btn--sm mt-1', href: e.link, target: '_blank', rel: 'noopener' }, '🔗 Abrir vaga'));
            }
            if (i.username === FaeAuth.currentUser.username) {
                const actions = FaeUtils.el('div', { class: 'flex gap-1 mt-2' });
                actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: async () => {
                    if (!await FaeUtils.confirm('Apagar este item?')) return;
                    try { await FaeAPI.hubDelete(i.id); card.remove(); FaeUtils.success('Item removido.'); } catch (e) { FaeUtils.error(e.message); }
                } }, '🗑 Apagar'));
                card.appendChild(actions);
            }
            return card;
        },

        renderProva(i) {
            const card = FaeUtils.el('div', { class: 'hub-item' },
                FaeUtils.el('div', { class: 'hub-item__tag hub-item__tag--prova' }, 'Prova / Aviso'),
                FaeUtils.el('h3', { class: 'hub-item__title' }, i.title || ''),
            );
            const extra = FaeUtils.el('div', { class: 'hub-item__extra' });
            const e = i.extra || {};
            if (e.disciplina) extra.appendChild(FaeUtils.el('span', {}, `📖 ${e.disciplina}`));
            if (e.data) extra.appendChild(FaeUtils.el('span', {}, `📅 ${e.data}`));
            if (e.conteudo) extra.appendChild(FaeUtils.el('span', {}, `📝 ${e.conteudo}`));
            card.appendChild(extra);
            if (i.content) card.appendChild(FaeUtils.el('div', { class: 'hub-item__content' }, i.content));
            const meta = FaeUtils.el('div', { class: 'hub-item__meta' });
            meta.appendChild(FaeUtils.el('span', {}, `📚 ${i.curso}`));
            meta.appendChild(FaeUtils.el('span', {}, `👤 ${i.author ? i.author.username : i.username}`));
            meta.appendChild(FaeUtils.el('span', {}, FaeUtils.timeAgo(i.timestamp)));
            card.appendChild(meta);
            if (i.username === FaeAuth.currentUser.username) {
                const actions = FaeUtils.el('div', { class: 'flex gap-1 mt-2' });
                actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: async () => {
                    if (!await FaeUtils.confirm('Apagar este aviso?')) return;
                    try { await FaeAPI.hubDelete(i.id); card.remove(); FaeUtils.success('Aviso removido.'); } catch (e) { FaeUtils.error(e.message); }
                } }, '🗑 Apagar'));
                card.appendChild(actions);
            }
            return card;
        },

        async renderForumTopic(i) {
            const wrap = FaeUtils.el('div', { class: 'hub-item hub-topic' + (i.solved ? ' is-solved' : '') },
                FaeUtils.el('div', { class: 'hub-item__tag hub-item__tag--forum_topic' }, 'Topico'),
                FaeUtils.el('h3', { class: 'hub-item__title' }, i.title || ''),
            );
            if (i.content) wrap.appendChild(FaeUtils.el('div', { class: 'hub-item__content', html: FaeUtils.formatText(i.content) }));
            const extra = FaeUtils.el('div', { class: 'hub-item__extra' });
            (i.extra && i.extra.tags ? i.extra.tags : '').split(',').filter(Boolean).forEach(t => {
                extra.appendChild(FaeUtils.el('span', {}, `# ${t.trim()}`));
            });
            if (extra.children.length) wrap.appendChild(extra);
            const meta = FaeUtils.el('div', { class: 'hub-item__meta' });
            meta.appendChild(FaeUtils.el('span', {}, `📚 ${i.curso}`));
            meta.appendChild(FaeUtils.el('span', {}, `👤 ${i.author ? i.author.username : i.username}`));
            meta.appendChild(FaeUtils.el('span', {}, FaeUtils.timeAgo(i.timestamp)));
            meta.appendChild(FaeUtils.el('span', {}, `💬 ${i.answers_count} resposta${i.answers_count === 1 ? '' : 's'}`));
            wrap.appendChild(meta);

            const actions = FaeUtils.el('div', { class: 'flex gap-1 mt-2' });
            actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: () => toggleAnswers() }, 'Ver respostas'));
            if (i.username === FaeAuth.currentUser.username) {
                actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: async () => {
                    try { await FaeAPI.hubSolve(i.id, !i.solved); FaeUtils.success(i.solved ? 'Reaberto.' : 'Marcado como resolvido.'); window.FaeApp.refresh(); } catch (e) { FaeUtils.error(e.message); }
                } }, i.solved ? '↺ Reabrir' : '✓ Marcar resolvido'));
                actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: async () => {
                    if (!await FaeUtils.confirm('Apagar este topico?')) return;
                    try { await FaeAPI.hubDelete(i.id); wrap.remove(); FaeUtils.success('Topico removido.'); } catch (e) { FaeUtils.error(e.message); }
                } }, '🗑 Apagar'));
            }
            wrap.appendChild(actions);

            const answersArea = FaeUtils.el('div', { class: 'hub-topic__answers', hidden: true });
            wrap.appendChild(answersArea);

            const toggleAnswers = async () => {
                if (!answersArea.hidden) { answersArea.hidden = true; return; }
                answersArea.hidden = false;
                answersArea.innerHTML = '';
                answersArea.appendChild(FaeUtils.el('div', { class: 'skeleton', style: { height: '60px' } }));
                try {
                    const answers = await FaeAPI.hubAnswers(i.id);
                    answersArea.innerHTML = '';
                    answers.forEach(a => answersArea.appendChild(this.renderForumAnswer(a, i)));
                    // Form de resposta
                    const formWrap = FaeUtils.el('div', { class: 'mt-2' });
                    const ta = FaeUtils.el('textarea', { class: 'field__textarea', placeholder: 'Sua resposta...' });
                    const btn = FaeUtils.el('button', { class: 'btn btn--primary btn--sm mt-1', onclick: async () => {
                        const text = ta.value.trim();
                        if (!text) return;
                        try {
                            const a = await FaeAPI.hubReply(i.id, text);
                            answersArea.appendChild(this.renderForumAnswer(a, i));
                            ta.value = '';
                        } catch (e) { FaeUtils.error(e.message); }
                    } }, 'Responder');
                    formWrap.appendChild(ta);
                    formWrap.appendChild(btn);
                    answersArea.appendChild(formWrap);
                } catch (e) { FaeUtils.error(e.message); }
            };
            return wrap;
        },

        renderForumAnswer(a, topic) {
            const card = FaeUtils.el('div', { class: 'hub-answer' },
                FaeUtils.el('div', { style: { fontSize: '13px' } },
                    FaeUtils.el('strong', {}, a.author ? a.author.name : a.username),
                    FaeUtils.el('span', { class: 'muted text-xs' }, ` · @${a.username} · ${FaeUtils.timeAgo(a.timestamp)}`),
                ),
                FaeUtils.el('div', { class: 'mt-1', html: FaeUtils.formatText(a.content) }),
            );
            if (a.username === FaeAuth.currentUser.username || (topic && topic.username === FaeAuth.currentUser.username)) {
                const actions = FaeUtils.el('div', { class: 'flex gap-1 mt-1' });
                actions.appendChild(FaeUtils.el('button', { class: 'btn btn--ghost btn--sm', onclick: async () => {
                    if (!await FaeUtils.confirm('Apagar resposta?')) return;
                    try { await FaeAPI.hubDelete(a.id); card.remove(); } catch (e) { FaeUtils.error(e.message); }
                } }, '🗑 Apagar'));
                card.appendChild(actions);
            }
            return card;
        },
    };

    global.FaeHub = Hub;
})(window);
