"""把 content/handbook.md（导读 + 已迁移的单元）转成交互网页，并在正文里插入演示的挂载点。

用法（在仓库根目录）：
    python3 site/build.py
生成：
    docs/index.html      交互学习手册
    docs/lab/index.html  可视化实验室（由 site/lab.html 包装而成）
"""
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
DOC = (ROOT / 'content' / 'handbook.md').read_text(encoding='utf-8')
SHELL = (SITE / 'course.shell.html').read_text(encoding='utf-8')

# ---------- 网页版的少量文字调整（只改“指向图”的说法） ----------
REPL = [
    ('（下方还会画一张状态转换图）', '（下面有一个可以点着走的状态机）'),
    ('线程在三个区域间怎么流转，见下图。', '线程在三个区域间怎么流转，可以在下面的演示里一步步看。'),
    ('一般不降级（下方会画一张升级图）', '一般不降级（下面可以一步步走一遍）'),
    ('引用块里的话可以直接说出口', '展开后的回答可以直接说出口'),
    ('先给出可运行的代码和真实运行结果，再解释为什么。',
     '先给出可运行的代码和真实运行结果，再解释为什么。网页版在关键处嵌了标着「动手」的演示，可以一步步执行。'),
]
for a, b in REPL:
    assert a in DOC, a
    DOC = DOC.replace(a, b, 1)

LINES = DOC.split('\n')


def section(start_prefix, end_prefix):
    s = next(i for i, l in enumerate(LINES) if l.startswith(start_prefix))
    e = next(i for i, l in enumerate(LINES) if l.startswith(end_prefix))
    return LINES[s:e]


# ---------- 行内转换 ----------
ESC_RE = re.compile(r'\\([\\`*_{}\[\]()#+\-.!~|<>])')
LINK_RE = re.compile(r'(?<!\\)\[([^\]]+?)\]\((https?://[^)\s]+)\)')


def inline(s):
    s = s.replace('&#91;', '[')
    keep = []

    def stash(h):
        keep.append(h)
        return '\x00%d\x00' % (len(keep) - 1)

    s = re.sub(r'`([^`]+)`', lambda m: stash('<code>' + html.escape(m.group(1), quote=False) + '</code>'), s)
    s = LINK_RE.sub(lambda m: stash('<a href="%s" target="_blank" rel="noopener">%s</a>' % (
        html.escape(m.group(2)), html.escape(ESC_RE.sub(r'\1', m.group(1)), quote=False))), s)
    s = ESC_RE.sub(r'\1', s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)
    return s


def plain(s):
    return re.sub(r'<[^>]+>', '', inline(s))


# ---------- 块级解析 ----------
def parse(lines):
    blocks, i, n = [], 0, len(lines)
    while i < n:
        L = lines[i]
        if not L.strip():
            i += 1
            continue
        if L.startswith('```'):
            lang = L[3:].strip()
            j = i + 1
            body = []
            while not lines[j].startswith('```'):
                body.append(lines[j])
                j += 1
            blocks.append({'t': 'code', 'lang': lang, 'text': '\n'.join(body)})
            i = j + 1
            continue
        m = re.match(r'^(#{2,4}) (.*)$', L)
        if m:
            blocks.append({'t': 'h', 'lv': len(m.group(1)), 'text': m.group(2)})
            i += 1
            continue
        if L.startswith('|') and i + 1 < n and re.match(r'^\|\s*-', lines[i + 1]):
            rows = []
            j = i
            while j < n and lines[j].startswith('|'):
                if not re.match(r'^\|\s*-', lines[j]):
                    rows.append([c.strip() for c in lines[j].strip().strip('|').split('|')])
                j += 1
            blocks.append({'t': 'table', 'rows': rows, 'raw': L})
            i = j
            continue
        if L.startswith('> '):
            blocks.append({'t': 'quote', 'text': L[2:]})
            i += 1
            continue
        if re.match(r'^(- |\d+\. )', L):
            items = []
            ordered = bool(re.match(r'^\d+\. ', L))
            check = L.startswith('- [ ] ')
            j = i
            while j < n and (re.match(r'^(- |\d+\. )', lines[j]) or re.match(r'^ {2,4}- ', lines[j])):
                cur = lines[j]
                if re.match(r'^ {2,4}- ', cur):
                    items[-1]['sub'].append(cur.strip()[2:])
                else:
                    txt = re.sub(r'^(- \[ \] |- |\d+\. )', '', cur)
                    items.append({'text': txt, 'sub': []})
                j += 1
            blocks.append({'t': 'list', 'ordered': ordered, 'check': check, 'items': items})
            i = j
            continue
        if L.startswith('!['):
            blocks.append({'t': 'embed', 'text': L})
            i += 1
            continue
        blocks.append({'t': 'p', 'text': L})
        i += 1
    return blocks


# ---------- 渲染 ----------
def render_list(b):
    tag = 'ol' if b['ordered'] else 'ul'
    out = ['<%s>' % tag]
    for it in b['items']:
        sub = ''
        if it['sub']:
            sub = '<ul>' + ''.join('<li>%s</li>' % inline(s) for s in it['sub']) + '</ul>'
        out.append('<li>%s%s</li>' % (inline(it['text']), sub))
    out.append('</%s>' % tag)
    return ''.join(out)


def render_table(b):
    head, *body = b['rows']
    h = ''.join('<th>%s</th>' % inline(c) for c in head)
    rows = ''.join('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>' for r in body)
    return '<div class="tbl"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, rows)


def render_code(b):
    lang = b['lang'] or 'text'
    return '<pre class="codeblock" data-lang="%s"><code>%s</code></pre>' % (lang, html.escape(b['text'], quote=False))


def mount(lab):
    return '<div class="lab-mount" data-lab="%s"></div>' % lab


def render_block(b):
    t = b['t']
    if t == 'p':
        return '<p>%s</p>' % inline(b['text'])
    if t == 'list':
        return render_list(b)
    if t == 'table':
        return render_table(b)
    if t == 'code':
        return render_code(b)
    if t == 'quote':
        return '<blockquote><p>%s</p></blockquote>' % inline(b['text'])
    if t == 'mount':
        return mount(b['lab'])
    if t == 'raw':
        return b['html']
    if t == 'embed':
        raise SystemExit('未处理的嵌入图：' + b['text'])
    raise SystemExit('未知块：' + t)


# ---------- 插入演示 ----------
RULES = [  # (动作, 匹配方式, 匹配文本, 演示名)
    ('after', 'p', '按这张表算', 'objlayout'),
    ('replace_embed', 'embed', 'Monitor 的三个区域', 'monitordemo'),
    ('replace_embed', 'embed', 'Java 线程 6 种状态及转换', 'statemachine'),
    ('after', 'p', '“必须用 while”背后是', 'notifydemo'),
    ('after', 'code', 'Thread t = new Thread(() -> {', 'interruptdemo'),
    ('after', 'p', '`getfield` 读', 'race'),
    ('after', 'p', '**场景题：两个线程各对', 'min2'),
    ('after', 'p', '代价是：A 核写了', 'visibility'),
    ('after', 'code', '① hb ②（程序顺序）', 'hb'),
    ('after', 'p', 'synchronized 只保证锁内', 'dcl'),
    ('after', 'p', '异常表第一行的意思是', 'bytecode'),
    ('after', 'table', '| 锁状态 | 其余位存什么', 'markword'),
    ('after', 'p', '把“进内核”展开', 'lifecycle'),
    ('replace_embed', 'embed', 'synchronized 锁升级', 'upgrade'),
]
DROP_AFTER_EMBED = {'monitordemo': '左边是对象本身', 'statemachine': '上排是主线', 'upgrade': '每一级的左侧是对象头'}


def apply_rules(blocks):
    used = set()
    for act, kind, text, lab in RULES:
        for idx, b in enumerate(blocks):
            hit = False
            if kind == 'p' and b['t'] == 'p' and b['text'].startswith(text):
                hit = True
            elif kind == 'code' and b['t'] == 'code' and text in b['text']:
                hit = True
            elif kind == 'table' and b['t'] == 'table' and b['raw'].startswith(text):
                hit = True
            elif kind == 'embed' and b['t'] == 'embed' and text in b['text']:
                hit = True
            if not hit:
                continue
            if act == 'after':
                blocks.insert(idx + 1, {'t': 'mount', 'lab': lab})
            else:
                blocks[idx] = {'t': 'mount', 'lab': lab}
                nxt = blocks[idx + 1]
                assert nxt['t'] == 'p' and nxt['text'].startswith(DROP_AFTER_EMBED[lab]), (lab, nxt)
                del blocks[idx + 1]
            used.add(lab)
            break
    return used


# ---------- 自测答案 ----------
ANSWERS = json.loads((ROOT / 'content' / 'answers.json').read_text(encoding='utf-8'))

MOTTO = {
    '一': 'Java 线程就是内核线程；线程之间的排队、等待和唤醒，都发生在对象的 monitor 上。',
    '二': '写进了自己的缓存，不等于别人看得见。',
    '三': '锁记在对象头里，能不进内核就不进内核。',
}
CN = {'一': 1, '二': 2, '三': 3}


def render_unit(lines, cn):
    num = CN[cn]
    head = lines[0][3:]
    m = re.match(r'^单元(\S+) (.+?)：(.+)$', head)
    title, sub = m.group(2), m.group(3)
    blocks = parse(lines[1:])
    used = apply_rules(blocks)
    out = []
    toc = []
    out.append('<header class="u-head"><div class="u-no">单元%s</div><h1>%s</h1><p class="u-sub">%s</p><p class="motto">%s</p></header>'
               % (cn, html.escape(title), html.escape(sub), MOTTO[cn]))
    i = 0
    sec_open = False
    mode = None
    quiz_n = 0
    while i < len(blocks):
        b = blocks[i]
        if b['t'] == 'h' and b['lv'] == 3:
            if sec_open:
                out.append('</section>')
            text = b['text']
            mm = re.match(r'^(\d+)\.(\d+) ', text)
            if mm:
                sid = 'u%d-%s' % (num, mm.group(2))
                mode = None
            elif text == '面试这样说':
                sid = 'u%d-interview' % num
                mode = 'interview'
            elif text == '自测':
                sid = 'u%d-quiz' % num
                mode = 'quiz'
            else:
                raise SystemExit('未知小节：' + text)
            cls = ' class="%s"' % mode if mode else ''
            out.append('<section id="%s"%s><h2>%s</h2>' % (sid, cls, inline(text)))
            if mode == 'interview':
                out.append('<p class="hint">先合上答案，自己用 30 秒说一遍，再展开对照。</p>')
            toc.append((sid, plain(text)))
            sec_open = True
            i += 1
            continue
        if not sec_open:
            if b['t'] == 'p' and b['text'].startswith('本单元的核心'):
                out.append('<p class="core">%s</p>' % inline(b['text']))
            elif b['t'] == 'p' and b['text'] == '**学习目标**':
                goals = blocks[i + 1]
                assert goals['t'] == 'list'
                rows = []
                for it in goals['items']:
                    lab, _, rest = it['text'].partition('：')
                    rows.append('<div class="g-row"><span class="g-tag g-%s">%s</span><span>%s</span></div>' % (
                        {'必会': 'must', '加分': 'plus', '了解': 'know'}[lab], lab, inline(rest)))
                out.append('<div class="goals"><div class="g-h">学习目标</div>%s</div>' % ''.join(rows))
                i += 2
                continue
            else:
                out.append(render_block(b))
            i += 1
            continue
        if mode == 'interview' and b['t'] == 'p' and b['text'].startswith('**问：'):
            q = b['text'].strip('*')
            a = blocks[i + 1]
            assert a['t'] == 'quote'
            out.append('<details class="qa"><summary>%s</summary><div class="ans">%s</div></details>' % (html.escape(q), inline(a['text'])))
            i += 2
            continue
        if mode == 'quiz' and b['t'] == 'list' and b['check']:
            items = []
            for it in b['items']:
                quiz_n += 1
                qid = 'u%d-q%d' % (num, quiz_n)
                ans = ANSWERS.get(it['text'])
                if ans is None:
                    raise SystemExit('缺少自测答案：' + it['text'])
                items.append('<li class="qz" data-qid="%s"><div class="qz-q">%s</div><div class="qz-act"><button type="button" class="btn sm qz-show" aria-expanded="false">看答案</button><label class="qz-ok"><input type="checkbox" class="qz-cb"> 我会了</label></div><div class="qz-a" hidden>%s</div></li>'
                             % (qid, inline(it['text']), ans))
            out.append('<p class="hint">先自己回答，再点开答案对照；勾上“我会了”的题会记在这台设备的浏览器里。<span class="qz-progress"></span></p><ol class="quizlist">%s</ol>' % ''.join(items))
            i += 1
            continue
        out.append(render_block(b))
        i += 1
    if sec_open:
        out.append('</section>')
    return '\n'.join(out), toc, used, title


def render_home(lines):
    blocks = parse(lines[1:])
    out = []
    for b in blocks:
        if b['t'] == 'h':
            out.append('<h2 id="home-%d">%s</h2>' % (len(out), inline(b['text'])))
        else:
            out.append(render_block(b))
    return '\n'.join(out)


home = render_home(section('## 导读', '## 单元一'))
units = []
all_used = set()
for cn, a, z in [('一', '## 单元一', '## 单元二'), ('二', '## 单元二', '## 单元三'), ('三', '## 单元三', '## 单元四')]:
    body, toc, used, title = render_unit(section(a, z), cn)
    all_used |= used
    units.append({'cn': cn, 'body': body, 'toc': toc, 'title': title})

need = {r[3] for r in RULES}
if all_used != need:
    raise SystemExit('有演示没插进去：%s' % (need - all_used))

views = ['<article class="view" id="view-home" data-view="home" hidden>%s</article>' % ('<!--HOME-HERO-->' + '<div class="prose">' + home + '</div>')]
for k, u in enumerate(units, 1):
    views.append('<article class="view" id="view-u%d" data-view="u%d" hidden><div class="prose">%s</div><!--PAGER-u%d--></article>' % (k, k, u['body'], k))
toc_json = json.dumps([{'id': 'u%d' % k, 'cn': u['cn'], 'title': u['title'], 'sections': [{'id': s, 'title': t} for s, t in u['toc']]} for k, u in enumerate(units, 1)], ensure_ascii=False)

def full_page(fragment):
    """页面源码里 <title>、<link>、<style> 在前，正文在后；拆开后包成完整的 HTML 文档。"""
    cut = fragment.index('</style>') + len('</style>')
    return ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>[hidden]{display:none!important} img{max-width:100%}</style>\n'
            + fragment[:cut] + '\n</head>\n<body>\n' + fragment[cut:] + '\n</body>\n</html>\n')


page = SHELL.replace('<!--VIEWS-->', '\n'.join(views)).replace('/*TOC_JSON*/null', toc_json)
out = ROOT / 'docs' / 'index.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(full_page(page), encoding='utf-8')
lab = ROOT / 'docs' / 'lab' / 'index.html'
lab.parent.mkdir(parents=True, exist_ok=True)
lab.write_text(full_page((SITE / 'lab.html').read_text(encoding='utf-8')), encoding='utf-8')
print('写出 docs/index.html（演示 %d 个，小节 %d 个）和 docs/lab/index.html' % (len(all_used), sum(len(u['toc']) for u in units)))
