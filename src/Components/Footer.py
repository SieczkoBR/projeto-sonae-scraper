import textwrap

def render_footer():
    from datetime import datetime
    year = datetime.now().year

    footer_html = textwrap.dedent("""
    <style>
      .mc-footer {
        margin-top: 24px;
        padding: 18px;
        border-radius: 10px;
        background: linear-gradient(90deg, #0f172a 0%, #0b1220 100%);
        color: #d1d5db;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      }
      .mc-footer__inner {
        display: flex;
        gap: 20px;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
      }
      .mc-footer__left { display: flex; gap: 12px; align-items: center; }
      .mc-footer__brand { display: flex; flex-direction: column; line-height: 1; }
      .mc-footer__title { font-weight: 700; color: #fff; font-size: 14px; }
      .mc-footer__subtitle { font-size: 12px; color: #9ca3af; }
      .mc-footer__links { display: flex; gap: 12px; align-items: center; }
      .mc-footer__link { color: #9ca3af; text-decoration: none; font-size: 13px; padding: 6px 10px; border-radius: 6px; transition: background 0.15s, color 0.15s; }
      .mc-footer__link:hover { background: rgba(255,255,255,0.03); color: #fff; }
      .mc-footer__meta { font-size: 12px; color: #9ca3af; }
      @media (max-width: 700px) { .mc-footer__inner { flex-direction: column; align-items: flex-start; } }
    </style>

    <div class="mc-footer" role="contentinfo">
      <div class="mc-footer__inner">
        <div class="mc-footer__left">
          <div style="width:44px;height:44px;background:linear-gradient(135deg,#06b6d4,#7c3aed);border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:18px">MS</div>
          <div class="mc-footer__brand">
            <div class="mc-footer__title">Dashboard MC Sonae</div>
            <div class="mc-footer__subtitle">ETL • BI • Insights por IA</div>
          </div>
        </div>

        <div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">
          <div class="mc-footer__links" aria-label="links do projeto">
            <a class="mc-footer__link" href="https://github.com/SieczkoBR/projeto-sonae-scraper/tree/main" target="_blank" rel="noopener">Código fonte</a>
            <a class="mc-footer__link" href="https://mit-license.org/" target="_blank" rel="noopener">Licença (MIT)</a>
            <a class="mc-footer__link" href="Documentação/GUIA_COMPLETO.md" target="_blank" rel="noopener">Guia</a>
          </div>
          <div class="mc-footer__meta">
            © """ + str(year) + """ Grupo Projetos 2 — Gabriel Peixoto, Rafael Holder, André Sieczko
          </div>
        </div>
      </div>
    </div>
    """)
    return footer_html.strip()