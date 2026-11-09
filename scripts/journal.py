"""Build the scholarly catalogue without changing a paper's original review status."""
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

GROUPS = {'project': 'Project papers', 'literature': 'Independent research',
          'background': 'Foundational literature', 'data': 'Data and software',
          'source': 'Construction sources'}


def esc(value):
    return html.escape(str(value), quote=True)


def web_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Journal links must be public HTTPS URLs')
    return value


def load_catalogue(root):
    data = json.loads((Path(root) / 'docs/journal/papers.json').read_text(encoding='utf-8'))
    ids = set()
    for item in data['papers']:
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', item['id']) or item['id'] in ids:
            raise ValueError('Invalid or duplicate journal entry ID')
        ids.add(item['id'])
        if item['group'] not in GROUPS or not item['authors'] or not item['review_status']:
            raise ValueError('Missing scholarly attribution or review status')
        if item.get('accepted_by_journal'):
            raise ValueError('Launch catalogue has no independently accepted Journal articles')
        for name in ('url', 'pdf_url', 'code_url', 'record_url', 'viewer_url', 'license_url'):
            if item.get(name):
                web_url(item[name])
    return data


def bibtex(item):
    # Keep titles intact, including braces and Unicode author names.
    clean = lambda text: str(text).replace('\\', r'\textbackslash{}').replace('{', r'\{').replace('}', r'\}')
    kind = 'article' if item.get('publication_type') == 'journal-article' else 'misc'
    names = []
    for name in item['authors']:
        if name == 'Alejandro Zarzuelo Urdiales':
            names.append('Zarzuelo Urdiales, Alejandro')
        elif name in ('Tencent Hunyuan', '@BuilderOfAgents / tronford') or 'individually credited contributors' in name:
            names.append('{' + clean(name) + '}')
        else:
            names.append(clean(name))
    fields = {'title': item['title'],
              'url': item['url'],
              'note': item['review_status']}
    if re.match(r'^\d{4}', item['date']):
        fields['year'] = item['date'][:4]
    if item.get('doi'):
        fields['doi'] = item['doi']
    if kind == 'article':
        fields['journal'] = item['venue']
        for source, target in [('volume','volume'),('issue','number'),('pages','pages'),('article_number','eid')]:
            if item.get(source):
                fields[target] = item[source]
    return '@' + kind + '{' + item['id'] + ',\n  author = {' + ' and '.join(names) + '},\n' + ',\n'.join(
        '  ' + key + ' = {' + clean(value) + '}' for key, value in fields.items()) + '\n}\n'


def card(item):
    search = ' '.join([item['title'], *item['authors'], item['kind'], item.get('venue', '')]).lower()
    stamp = f'<time datetime="{esc(item["date"])}">{esc(item["date"])}</time>' if re.fullmatch(r'\d{4}-\d{2}-\d{2}',item['date']) else '<span>'+esc(item['date'])+'</span>'
    return f'''<article class="j-card" data-journal-card data-group="{item['group']}" data-search="{esc(search)}">
      <div class="j-card-meta"><span class="j-badge">{esc(item['kind'])}</span>{stamp}</div>
      <h3><a href="articles/{item['id']}/">{esc(item['title'])}</a></h3>
      <p class="j-authors">{esc(', '.join(item['authors']))}</p>
      <p>{esc(item['summary'])}</p>
      <p class="j-origin">{esc(item.get('venue', 'Author manuscript'))}</p>
      <a class="j-read" href="articles/{item['id']}/">Read paper details <span aria-hidden="true">↗</span></a>
    </article>'''


def build_journal(root, out, repo, site_url, page, fill):
    root, out = Path(root), Path(out)
    data = load_catalogue(root)
    papers = data['papers']
    urls = []
    submit = repo + '/issues/new?template=journal-submission.yml'
    print_interest = repo + '/issues/new?template=journal-print-interest.yml'

    def emit(path, title, desc, body, depth=1, metadata=''):
        target = out / path / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered = page(path + '/', title + ': Polyhedra in Polyhedra', desc, body, 'journal/',
                        scripts=('journal.js',) if path == 'journal' else (),
                        styles=('journal.css',), depth=depth)
        if metadata:
            rendered = rendered.replace('</head>', metadata + '\n</head>', 1)
        target.write_text(rendered, encoding='utf-8')
        urls.append(path + '/')

    sections = []
    for group, title in GROUPS.items():
        entries = [item for item in papers if item['group'] == group]
        if not entries:
            continue
        descriptions = {
            'project': 'Methods, mathematical guarantees, structural patterns and materials modelling. Each entry retains its current publication status.',
            'literature': 'Independent packing studies with constructions represented in the catalogue. These papers retain their original venues.',
            'background': 'Published research behind the methods and comparisons. These are contextual sources, rather than claimed imports of finite-container coordinates.',
            'data': 'Citable datasets and reproducible software supporting the research.',
            'source': 'Historical catalogues, coordinate releases, refinements and proof repositories. These resources are not presented as journal papers.'}
        sections.append(f'<section class="j-library-group" data-journal-group id="{group}"><div class="j-section-head"><h2>{title}</h2><p>{descriptions[group]}</p></div><div class="j-grid">' + ''.join(card(item) for item in entries) + '</div></section>')
    count_papers = sum(item['group'] in ('project', 'literature', 'background') for item in papers)
    index = f'''<section class="j-hero" aria-labelledby="journal-title">
      <div class="j-hero-copy"><p class="j-eyebrow">Polyhedra in Polyhedra</p><h1 id="journal-title">Journal</h1>
      <p class="j-deck">Geometry worth inspecting.<br>Research built to be reproduced.</p>
      <p class="j-intro">An open-access publishing programme for polyhedral and higher-dimensional polytope packing, exact proofs and reproducible constructions.</p>
      <div class="j-actions"><a class="primary" href="#papers">Explore the papers</a><a class="small" href="{submit}">Submit a manuscript</a></div>
      <div class="j-issue-line"><span class="j-live-dot" aria-hidden="true"></span><span>Volume 1 · Issue 1 · Q4 2026<br><b>The inaugural issue is in progress.</b></span></div>
      <p class="j-small">Submissions are open for the October–December issue. Articles will be published after review and collected into quarterly editions.</p>
      <a href="issues/2026-q4/">About the first issue</a></div>
      <a class="j-cover" href="issues/2026-q4/" aria-label="View the Q4 2026 inaugural issue"><img src="../assets/journal-cover-q4-2026.svg" width="900" height="1200" alt="Q4 2026 journal cover showing sixteen icosahedra inside an icosahedron. Inaugural issue in progress."><span>Volume 1 / Issue 1 / Q4 2026</span></a>
    </section>
    <div class="j-principles"><span>Free to read and submit</span><span>Evidence linked to the research</span><span>Independent review programme</span></div>
    <section class="j-launch-note"><h2>A journal taking shape</h2><p>The founding issue is open for submissions. The collection below brings together existing papers and research resources. Their original venues and review statuses are shown; inclusion here is not acceptance by this Journal. Research articles must complete the <a href="policies/#review">independent review process</a> before joining the issue's accepted contents.</p></section>
    <section id="papers" class="j-library" aria-labelledby="papers-title"><div class="j-section-head"><p class="j-eyebrow">The research collection</p><h2 id="papers-title">Papers, proofs and constructions</h2><p>{count_papers} research papers and {len(papers) - count_papers} data, software and construction resources. Follow each paper to its PDF, citation and supporting evidence.</p></div>
      <form class="j-filters" role="search" onsubmit="return false"><label>Search the collection<input type="search" id="journal-search" placeholder="Title, author or topic" autocomplete="off"></label><label>Collection<select id="journal-group"><option value="all">All research and resources</option>''' + ''.join(f'<option value="{key}">{title}</option>' for key, title in GROUPS.items()) + f'''</select></label></form>
      <p class="j-result-count" id="journal-results" role="status" aria-live="polite">{len(papers)} entries</p>
      {''.join(sections)}<p id="journal-empty" hidden>No entries match this search. Try another title, author or collection.</p>
    </section>
    <section class="j-print"><div><p class="j-eyebrow">From screen to shelf</p><h2>Open access. A print edition in preparation.</h2><p>We plan to print and ship quarterly editions to academics and research libraries around the world. The inaugural Q4 2026 issue is still in progress.</p><p>Print availability, costs and shipping details will be announced before orders open. You can register interest now without placing an order.</p><a class="small" href="{print_interest}">Register print interest</a><a class="j-text-link" href="../assets/journal-cover-q4-2026.svg" download>Download the vector cover</a></div></section>
    <section class="j-editorial"><div><h2>For authors and reviewers</h2><p>Research papers, rigorous bounds, verified constructions and substantial reproducible analyses are welcome. The scope begins in three dimensions.</p><a href="{submit}">Submit a manuscript</a></div><div><h2>Editorial standards</h2><p>Two independent expert reports, disclosed conflicts, linked evidence and a versioned publication record form the founding review policy.</p><a href="policies/">Read the editorial and publication policies</a></div></section>'''
    emit('journal', 'Journal', 'Open-access polyhedral packing research. The inaugural Q4 2026 issue is in progress: papers, exact proofs, reproducible data and a founding review programme.', index)

    issue = f'''<div class="j-breadcrumb"><a href="../../">Journal</a> / Issues / Q4 2026</div><section class="j-hero j-issue-hero"><div><p class="j-eyebrow">Volume 1 · Issue 1 · October–December 2026</p><h1>Q4 2026</h1><p class="j-deck">The inaugural issue<br>is in progress.</p><p class="j-intro">A first quarterly edition on finite packing, exact certificates and the structures they reveal.</p><div class="j-actions"><a class="primary" href="{submit}">Submit to the issue</a><a class="small" href="../../#papers">Explore the research collection</a></div><p>Online articles will appear as they complete review. The issue remains open through 31 December 2026; acceptance depends on the review decision.</p><p>No article has yet been accepted through this Journal's independent review programme. The linked <a href="../../#papers">research collection</a> is a reading library, not a list of accepted issue articles.</p></div><a class="j-cover" href="../../../assets/journal-cover-q4-2026.svg"><img src="../../../assets/journal-cover-q4-2026.svg" width="900" height="1200" alt="Inaugural issue cover, sixteen icosahedra in an icosahedron"></a></section><section class="j-launch-note"><h2>Digital first, quarterly in print</h2><p>Articles will be free to read online. Quarterly print editions are planned for academics and research libraries worldwide. Availability and shipping terms will be announced before orders open.</p><p><a href="{print_interest}">Register print interest</a> · <a href="../../policies/">Editorial policies</a> · <a href="../../../#icoinico_n16">Inspect the construction on the cover</a></p></section>'''
    emit('journal/issues/2026-q4', 'Q4 2026 inaugural issue', 'Volume 1, Issue 1 is in progress. Open submissions for the first quarterly Polyhedra in Polyhedra issue.', issue, depth=3)
    policy = (root / 'web/pages/journal-policies.html').read_text(encoding='utf-8')
    emit('journal/policies', 'Editorial and publication policies', 'Founding editorial policy: independent review, conflicts, open access, fees, reproducibility, corrections and print plans.', fill(policy, {}, '../../'), depth=2)

    bib_dir = out / 'journal/citations'
    bib_dir.mkdir(parents=True, exist_ok=True)
    for item in papers:
        (bib_dir / (item['id'] + '.bib')).write_text(bibtex(item), encoding='utf-8')
        canonical = site_url + 'journal/articles/' + item['id'] + '/'
        links = [] if item['url'] == canonical else [('Original publication' if item['group'] != 'project' else 'Source record', item['url'])]
        for field, label in [('pdf_url', 'Read the PDF'), ('code_url', item.get('code_label','Code and reproducibility')), ('viewer_url', 'Explore the construction'), ('record_url', 'Native construction record')]:
            if item.get(field):
                links.append((label, item[field]))
        actions = ''.join(f'<a class="small" href="{esc("../../../"+url[len(site_url):] if url.startswith(site_url) else url)}">{esc(label)}</a>' for label, url in links)
        detail = f'''<div class="j-breadcrumb"><a href="../../">Journal</a> / <a href="../../#{item['group']}">{GROUPS[item['group']]}</a></div><article class="j-paper"><header><p class="j-eyebrow">{esc(item['kind'])} · {esc(item['date'])}</p><h1>{esc(item['title'])}</h1><p class="j-paper-authors">{esc(', '.join(item['authors']))}</p><p class="j-paper-venue">{esc(item.get('venue', 'Author manuscript'))}</p><div class="j-actions">{actions}<a class="small" href="../../citations/{item['id']}.bib" download>Download citation</a></div></header><section><h2>Overview</h2><p>{esc(item['summary'])}</p></section><section class="j-review"><h2>Publication and review</h2><p>{esc(item['review_status'])}</p><p>This entry links an existing work. It has not been independently accepted or reviewed by Polyhedra in Polyhedra Journal.</p>'''
        if item.get('version_note'):
            detail += '<p>' + esc(item['version_note']) + '</p>'
        if item.get('record_lineage'):
            detail += '<p>' + esc(item['record_lineage']) + '</p>'
        detail += '</section><section><h2>Citation and source</h2><dl class="j-metadata">'
        for label, value in [('Authors', ', '.join(item['authors'])), ('Published / dated', item['date']), ('Venue / archive', item.get('venue', 'Author manuscript')), ('DOI', item.get('doi')), ('Version', item.get('version')), ('Pages', item.get('pages')), ('License', item.get('license')), ('PDF SHA-256', item.get('pdf_sha256'))]:
            if value:
                detail += f'<dt>{label}</dt><dd>{esc(value)}</dd>'
        detail += '</dl><details><summary>Show BibTeX</summary><pre>' + esc(bibtex(item)) + '</pre></details></section>'
        if item.get('related_links'):
            detail += '<section><h2>Related versions and evidence</h2><ul>' + ''.join('<li><a href="' + esc(web_url(link['url'])) + '">' + esc(link['label']) + '</a></li>' for link in item['related_links']) + '</ul></section>'
        detail += '<p class="j-small">Metadata checked ' + esc(data['checked_on']) + '. <a href="' + repo + '/blob/main/docs/journal/papers.json">Inspect the source catalogue</a>. <a href="../../policies/#corrections">Report a correction</a>.</p></article>'
        metadata = []
        if item['group'] in ('project', 'literature', 'background'):
            tags = {'citation_title': item['title'], 'citation_publication_date': item['date'].replace('-', '/'),
                    'citation_doi': item.get('doi'), 'citation_pdf_url': item.get('pdf_url')}
            metadata += [f'<meta name="{name}" content="{esc(value)}">' for name, value in tags.items() if value]
            metadata += [f'<meta name="citation_author" content="{esc(name)}">' for name in item['authors']]
            structured = {'@context': 'https://schema.org', '@type': 'ScholarlyArticle', 'headline': item['title'],
                          'author': [{'@type': 'Person', 'name': author} for author in item['authors']],
                          'datePublished': item['date'], 'description': item['summary'], 'url': item['url']}
            if item.get('doi'):
                structured['identifier'] = item['doi']
            metadata.append('<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
        emit('journal/articles/' + item['id'], item['title'], item['summary'], detail, depth=3, metadata='\n'.join(metadata))
    downloads = root / 'web/journal/downloads'
    if downloads.is_dir():
        shutil.copytree(downloads, out / 'journal/downloads', dirs_exist_ok=True)
    (out / 'journal/catalogue.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return urls
