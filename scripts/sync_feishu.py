"""把 content/handbook.md 单向同步到一篇飞书云文档（整篇覆盖：仓库 → 飞书）。

正文以仓库为准，飞书只是镜像；在飞书里直接做的修改会在下次同步时被覆盖。

用法（在仓库根目录运行）：
    FEISHU_DOC=<飞书文档链接或 token> python3 scripts/sync_feishu.py
    python3 scripts/sync_feishu.py --dry-run     # 只生成 .sync/feishu.md，不上传

需要先安装并登录 lark-cli（lark-cli auth login）。
转换规则：
    - 去掉一级标题（飞书文档自己的标题就是书名），顶部加一段“以仓库为准”的提示
    - “面试这样说”等引用块转成飞书的提示框（callout）
    - 相对路径的配图 img/xxx.png 改成 lark-cli 能上传的本地路径
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'content' / 'handbook.md'
OUT = ROOT / '.sync' / 'feishu.md'
REPO = 'https://github.com/erha1499/learn-juc'
SITE = 'https://erha1499.github.io/learn-juc/'
BANNER = ('<callout emoji="📌">\n'
          '本文由 GitHub 仓库 [learn-juc](%s) 的 content/handbook.md 单向同步而来，请不要在飞书里直接修改，'
          '改动会在下次同步时被覆盖。交互版：[在线阅读](%s)\n'
          '</callout>') % (REPO, SITE)


def convert(md):
    lines = md.split('\n')
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
    out, in_code, quotes, images = [BANNER], False, 0, 0
    for line in lines:
        if line.startswith('```'):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        if line.startswith('> '):
            body = line[2:]
            if '<' in re.sub(r'`[^`]*`', '', body):
                sys.exit('引用块里有尖括号，转成提示框可能出错，请检查：' + body[:60])
            out.append('<callout emoji="💬">\n' + body + '\n</callout>')
            quotes += 1
            continue
        line, n = re.subn(r'!\[([^\]]*)\]\(img/([^)\s]+)\)', r'![\1](@./content/img/\2)', line)
        images += n
        out.append(line)
    return '\n'.join(out), quotes, images


def main():
    dry = '--dry-run' in sys.argv
    text, quotes, images = convert(SRC.read_text(encoding='utf-8'))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding='utf-8')
    print('已生成 %s：%d 个提示框，%d 张图片' % (OUT.relative_to(ROOT), quotes + 1, images))
    if dry:
        return
    doc = os.environ.get('FEISHU_DOC')
    if not doc:
        sys.exit('请用环境变量 FEISHU_DOC 指定飞书文档的链接或 token')
    cmd = ['lark-cli', 'docs', '+update', '--as', 'user', '--doc', doc, '--command', 'overwrite',
           '--doc-format', 'markdown', '--content', '@./' + str(OUT.relative_to(ROOT))]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except ValueError:
        sys.exit('lark-cli 返回了非 JSON 内容：\n' + (res.stdout or res.stderr)[-2000:])
    if not data.get('ok'):
        sys.exit('同步失败：\n' + json.dumps(data, ensure_ascii=False, indent=2)[-2000:])
    doc_info = data['data']['document']
    uploaded = sum(1 for b in doc_info.get('new_blocks', []) if b.get('block_type') == 'image')
    print('同步完成：%s（修订号 %s，上传图片 %d 张）' % (doc_info.get('url'), doc_info.get('revision_id'), uploaded))
    for w in data['data'].get('warnings') or []:
        print('警告：', w)


if __name__ == '__main__':
    main()
