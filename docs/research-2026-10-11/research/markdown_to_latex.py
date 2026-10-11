"""Convert the review manuscripts to standalone LaTeX, retaining their math.

No external assets are needed by the native compiler. The second manuscript
gets inline pgfplots built from its accompanying data; PNGs remain in Markdown.
"""
import csv, pathlib, re, sys

SYMBOLS={'√':r'$\sqrt{}$','≤':r'$\leq$','≥':r'$\geq$','≈':r'$\approx$','≠':r'$\neq$','×':r'$\times$','∈':r'$\in$','⊆':r'$\subseteq$','⊕':r'$\oplus$','ρ':r'$\rho$','φ':r'$\varphi$','μ':r'$\mu$','Δ':r'$\Delta$','Σ':r'$\Sigma$','π':r'$\pi$','θ':r'$\theta$','δ':r'$\delta$','ε':r'$\varepsilon$','β':r'$\beta$','α':r'$\alpha$','∞':r'$\infty$','∼':r'$\sim$','−':'-','–':'--','—':'---','→':r'$\to$','…':r'\ldots{}','°':r'$^{\circ}$','²':r'$^2$','³':r'$^3$','∎':r'$\square$','ᵀ':r'$^{\mathsf T}$','ℚ':r'$\mathbb Q$','ℝ':r'$\mathbb R$'}

def esc(s):
    s=s.replace('“','``').replace('”',"''").replace('‘','`').replace('’',"'")
    return ''.join(SYMBOLS.get(c,{'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}'}.get(c,c)) for c in s)

def url(s):
    return s.replace('%',r'\%').replace('#',r'\#').replace('&',r'\&').replace('_',r'\_')

def inline(s):
    held=[]
    def keep(x):
        held.append(x); return f'ZZPLACEHOLDER{len(held)-1}ZZ'
    # Math is protected before escaping prose.
    s=re.sub(r'(?<!\\)\$([^$\n]+)\$',lambda m:keep('$'+m.group(1)+'$'),s)
    s=re.sub(r'\\\((.+?)\\\)',lambda m:keep(r'\('+m.group(1)+r'\)'),s)
    s=re.sub(r'`([^`]+)`',lambda m:keep(r'\nolinkurl{'+m.group(1)+'}'),s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:keep(r'\href{'+url(m.group(2))+r'}{'+inline(m.group(1))+'}'),s)
    s=re.sub(r'https?://[^\s<>]+',lambda m:keep(r'\url{'+url(m.group(0))+'}'),s)
    s=re.sub(r'\*\*([^*]+)\*\*',lambda m:keep(r'\textbf{'+inline(m.group(1))+'}'),s)
    s=re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)',lambda m:keep(r'\emph{'+inline(m.group(1))+'}'),s)
    s=esc(s)
    for i,v in reversed(list(enumerate(held))): s=s.replace(f'ZZPLACEHOLDER{i}ZZ',v)
    return s

def convert(path):
    raw=path.read_text(encoding='utf-8'); lines=raw.splitlines(); out=[]; title=''; i=0; listenv=None
    def endlist():
        nonlocal listenv
        if listenv: out.append(r'\end{'+listenv+'}'); listenv=None
    while i<len(lines):
        line=lines[i]; stripped=line.strip()
        if re.match(r'^\*\*Alejandro Zarzuelo(?: Urdiales)?\*\*',stripped):
            i+=1; continue
        if stripped.startswith('```'):
            endlist(); code=[]; i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'): code.append(lines[i]); i+=1
            out.extend([r'\begin{Verbatim}[fontsize=\footnotesize,breaklines=true]',*code,r'\end{Verbatim}']); i+=1; continue
        if stripped in [r'\[','$$']:
            endlist(); math=[]; closing=r'\]' if stripped==r'\[' else '$$'; i+=1
            while i<len(lines) and lines[i].strip()!=closing: math.append(lines[i]); i+=1
            out.extend([r'\begin{center}\begin{adjustbox}{max width=\linewidth}$\displaystyle\begin{aligned}',*math,r'\end{aligned}$\end{adjustbox}\end{center}']); i+=1; continue
        if stripped.startswith('|') and i+1<len(lines) and re.match(r'^\|?\s*:?-+',lines[i+1].strip()):
            endlist(); rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.match(r'^:?-+:?$',x) for x in row): rows.append(row)
                i+=1
            n=max(map(len,rows)); landscape=n>=8
            if landscape: out.append(r'\begin{landscape}')
            widths=''.join('>{\\raggedright\\arraybackslash}p{'+str(round((0.96-0.018*n)/n,3))+'\\linewidth}' for _ in range(n))
            out.extend([r'\begingroup\footnotesize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{'+widths+'}',r'\toprule'])
            for j,row in enumerate(rows):
                out.append(' & '.join(inline(x) for x in row+['']*(n-len(row)))+r' \\')
                if j==0: out.extend([r'\midrule',r'\endhead'])
            out.extend([r'\bottomrule',r'\end{longtable}',r'\endgroup'])
            if landscape: out.append(r'\end{landscape}')
            continue
        h=re.match(r'^(#{1,6})\s+(.+)',stripped)
        if h:
            endlist(); level=len(h.group(1)); val=h.group(2)
            if level==1 and not title: title=val
            else:
                cmd={1:'section',2:'section',3:'subsection',4:'subsubsection',5:'paragraph',6:'paragraph'}[level]
                if level==3 and re.match(r'^9\.\d+',val): out.append(r'\Needspace{10\baselineskip}')
                val=re.sub(r'^\d+(?:\.\d+)*(?:\.)?\s+','',val)
                if val.startswith('Appendix A.'):
                    out.append(r'\appendix'); val=val.removeprefix('Appendix A.').strip()
                star='*' if val in ['Abstract','References and source map','References and source notes','Figure captions'] else ''
                out.append('\\'+cmd+star+'{'+inline(val)+'}')
            i+=1; continue
        img=re.match(r'^!\[([^\]]*)\]\(([^)]+)\)',stripped)
        if img:
            endlist(); asset=img.group(2)
            if asset.startswith('analysis/'):
                caption=re.sub(r'^Figure \d+:\s*','',img.group(1))
                out.append(r'\IfFileExists{'+asset+r'}{\begin{figure}[p]\centering\includegraphics[width=\linewidth,height=0.78\textheight,keepaspectratio]{'+asset+r'}\caption{'+inline(caption)+r'}\end{figure}}{\paragraph{Supplementary figure.} '+inline(caption)+r' See the companion figure in the analysis directory.}')
            else:
                out.append(r'\paragraph{Supplementary figure.} '+inline(img.group(1))+' See the corresponding PNG in the companion Markdown manuscript and analysis directory.')
            i+=1; continue
        match=re.match(r'^(?:[-*]|\d+\.)\s+(.+)',stripped)
        if match:
            env='enumerate' if re.match(r'^\d+\.',stripped) else 'itemize'
            if listenv!=env: endlist(); listenv=env; out.append(r'\begin{'+env+'}')
            out.append(r'\item '+inline(match.group(1))); i+=1; continue
        if not stripped:
            # Blank lines separate prose but need not split every list item.
            if i+1<len(lines) and not re.match(r'^\s*(?:[-*]|\d+\.)\s+',lines[i+1]): endlist()
            out.append(''); i+=1; continue
        if stripped=='---': endlist(); i+=1; continue
        if stripped.startswith('>'): stripped=stripped.lstrip('> ')
        endlist()
        if re.match(r'^\*\*H\d+\.',stripped): out.append(r'\Needspace{5\baselineskip}')
        out.append(inline(stripped)); i+=1
    endlist()
    head=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=24mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,amsmath,amssymb,mathtools,booktabs,longtable,array}
\usepackage{fvextra}
\usepackage{adjustbox}
\usepackage{graphicx,pdflscape}
\usepackage{needspace}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{xurl}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{0.35em}
\setlength{\parindent}{1em}
\newcommand{\R}{\mathbb R}
\newcommand{\Q}{\mathbb Q}
\DeclareMathOperator{\vol}{vol}
\DeclareMathOperator{\dist}{dist}
\DeclareMathOperator{\SO}{SO}
\title{'''+inline(title)+r'''}
\author{Alejandro Zarzuelo Urdiales}
\date{11 October 2026}
\begin{document}
\maketitle
'''
    body='\n'.join(out)
    if path.name.startswith('paper-2'):
        head=head.replace(r'\usepackage{xcolor}',r'\usepackage{xcolor}'+'\n'+r'\usepackage{pgfplots}'+'\n'+r'\pgfplotsset{compat=1.18}')
        body+='\n'+r'\IfFileExists{analysis/figure-1-scale-curves.png}{}{'+plots(path.parent/'analysis')+'}'
    result=path.with_suffix('.tex'); result.write_text(head+body+'\n'+r'\end{document}'+'\n',encoding='utf-8'); print(result)

def plots(analysis):
    rows=list(csv.DictReader((analysis/'record-metrics.csv').open(encoding='utf-8')))
    families=list(dict.fromkeys(x['problem'] for x in rows))
    plots=[]
    for key,ylabel in [('density','Packing fraction'),('s_full','Certified container scale')]:
        if key not in rows[0]: continue
        s=r'\clearpage\section*{Inline data figure: '+ylabel+'}\n'
        s+=r'\begin{center}\begin{tikzpicture}\begin{axis}[width=0.98\linewidth,height=0.62\linewidth,xlabel={Particle count},ylabel={'+ylabel+r'},legend style={at={(0.5,-0.2)},anchor=north,legend columns=3,font=\scriptsize},grid=major]'
        for fam in families:
            data=sorted([x for x in rows if x['problem']==fam],key=lambda x:int(float(x['n'])))
            coords=' '.join(f'({x["n"]},{float(x[key]):.9g})' for x in data)
            s+=r'\addplot+[mark=none] coordinates {'+coords+r'};\addlegendentry{'+esc(fam)+'}\n'
        s+=r'\end{axis}\end{tikzpicture}\end{center}'
        s+='\n'+r'\noindent Source: all 351 frozen records at commit \texttt{e15b496}. Curves join independently optimized constructions; they are upper-bound observations, not certified optimum curves.'
        plots.append(s.replace('}\\n','}\n'))
    return '\n'.join(plots)

if __name__=='__main__':
    for item in sys.argv[1:]: convert(pathlib.Path(item))
