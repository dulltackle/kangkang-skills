#!/usr/bin/env python3
"""检查本技能 Markdown 正文的内联文件链接；不检查仓库路径示例或网络链接。"""

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+"[^"\n]*")?\s*\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')


def check(root):
    root = root.resolve(strict=True)
    errors = []
    count = 0
    if not (root / 'SKILL.md').is_file():
        return 0, ['缺少 SKILL.md']
    for document in sorted(root.rglob('*.md')):
        try:
            source = document.resolve(strict=True)
            if not source.is_relative_to(root):
                raise ValueError('文档指向技能包外')
            content = source.read_text(encoding='utf-8')
        except (OSError, ValueError, RuntimeError) as error:
            errors.append(f'{document.relative_to(root)}：{error}')
            continue
        fence = None
        for number, line in enumerate(content.splitlines(), 1):
            marker = FENCE.match(line)
            if marker:
                token, tail = marker.groups()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence) and not tail.strip():
                    fence = None
                continue
            if fence is not None:
                continue
            for match in LINK.finditer(line):
                link = match.group(1) or match.group(2)
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                count += 1
                try:
                    path = Path(unquote(url.path))
                    if path.is_absolute():
                        raise ValueError('本地引用须为包内相对路径')
                    target = (source.parent / path).resolve(strict=True)
                    if not target.is_relative_to(root):
                        raise ValueError('引用越出技能包，存在未打包的外部依赖')
                    target.read_bytes()
                except (OSError, ValueError, RuntimeError) as error:
                    errors.append(f'{document.relative_to(root)}:{number} {link}：{error}')
    return count, errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path,
                        default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        count, errors = check(args.directory)
    except (OSError, ValueError, RuntimeError) as error:
        count, errors = 0, [str(error)]
    if errors:
        print('\n'.join(errors))
    else:
        print(f'通过：{count} 个内联本地文件引用均位于技能包内且可读。')
    raise SystemExit(1 if errors else 0)
