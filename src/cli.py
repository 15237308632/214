# -*- coding: utf-8 -*-
"""八字命理知识库 · 命令行检索入口

  python3 src/cli.py --demo
  python3 src/cli.py --solar "1990-06-15 14:00" --sex 男
  python3 src/cli.py --pillars "庚午 壬午 辛亥 乙未" --sex 男 --json out.json
  python3 src/cli.py --query 调候 甲 子
  python3 src/cli.py --query 十神 甲 辛
  python3 src/cli.py --query 长生 甲 子
  python3 src/cli.py --query 纳音 甲子
  python3 src/cli.py --query 书 子平真诠
  python3 src/cli.py --list
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import bazi as B  # noqa: E402


def cmd_query(args):
    toks = args.query or []
    kind = toks[0].lower() if toks else ""
    rest = toks[1:]
    if kind in ("调候", "tiaohou"):
        if len(rest) < 2:
            print("用法: --query 调候 <日干> <月支>   例: --query 调候 甲 子")
            return 1
        g, z = rest[0], rest[1]
        t = B.load("tiaohou.json")
        idx = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
        if g not in B.TG or z not in idx:
            print("日干须为十天干之一, 月支须为十二地支之一")
            return 1
        row = t["表"][g][idx.index(z)]
        print(f"\n《穷通宝鉴》 {g} 生 {z}月 ({row['季']} / {row['节']})")
        print("  " + row["text"])
        print("  候选用神(机器提取): " + "、".join(x for x in row["yongshen候选"] if x != g))
        print("  优先级异说: " + t["meta"]["优先级异说"])
    elif kind in ("十神", "shishen"):
        if len(rest) < 2:
            print("用法: --query 十神 <日干> <他干>")
            return 1
        print(f"{rest[0]}日见{rest[1]} → {B.ten_god(rest[0], rest[1])}")
        print(B.load("shishen.json")["定义"][B.ten_god(rest[0], rest[1])]["取象"])
        print(B.load("shishen.json")["沈氏四吉四凶"]["重要限定"])
    elif kind in ("长生", "changsheng"):
        if len(rest) < 2:
            print("用法: --query 长生 <日干> <地支>")
            return 1
        t = B.load("changsheng.json")
        print(f"{rest[0]} 在 {rest[1]}: {t['表'][rest[0]][rest[1]]}")
        print("异说: " + t["meta"]["异说"])
    elif kind in ("纳音", "nayin"):
        if not rest:
            print("用法: --query 纳音 <干支>")
            return 1
        m = {x["干支"]: x for x in B.load("nayin.json")["六十甲子"]}
        x = m.get(rest[0])
        print(f"{rest[0]}: 纳音 {x['纳音']} / {x['旬']} / 空亡 {'、'.join(x['空亡'])}" if x else "未找到该干支")
    elif kind in ("书", "classic", "典籍"):
        cs = B.load("classics.json")["五书"]
        kw = rest[0] if rest else ""
        hit = [c for c in cs if kw in c["书名"] or kw in c["作者"] or kw in c["核心命题"]]
        for c in (hit or cs):
            print(f"\n《{c['书名']}》 {c['年代']}")
            print(f"  作者/注者: {c['作者']}")
            print(f"  卷帙: {c['卷帙']}")
            print(f"  核心: {c['核心命题']}")
            print(f"  定位: {c['定位']}")
            print(f"  异说: {c.get('版本异说', '—')}")
    else:
        print("支持的检索: 调候 / 十神 / 长生 / 纳音 / 书")
        return 1
    return 0


def cmd_list(args):
    print("\n【五部经典】")
    for c in B.load("classics.json")["五书"]:
        print(f"  {c['排序']}. 《{c['书名']}》 {c['卷帙']} — {c['核心命题'][:38]}…")
    print("\n【数据表】")
    for p in sorted(B.DATA.glob("*.json")):
        print(f"  data/{p.name:<22} {p.stat().st_size:>7} bytes")
    print("\n【目录】docs/ 研读笔记与概念; src/ 引擎与生成器; tests/ 校验; index.html 浏览器检索")
    return 0


def main():
    ap = argparse.ArgumentParser(description="八字命理知识库 CLI", formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--solar", help='公历出生时间 "YYYY-MM-DD HH:MM", 北京时间')
    ap.add_argument("--pillars", help='直接给四柱 "庚午 壬午 辛亥 乙未"')
    ap.add_argument("--sex", default="男", help="性别, 用于大运顺逆 (默认 男)")
    ap.add_argument("--late-zi", action="store_true", default=True, help="23时归次日(默认)")
    ap.add_argument("--json", help="把完整分析结果写入 JSON 文件")
    ap.add_argument("--query", nargs="+", metavar="ARG", help="检索数据表, 见 --query 调候 甲 子")
    ap.add_argument("--list", action="store_true", help="列出五书与数据表")
    ap.add_argument("--demo", action="store_true", help="运行示例命例")
    args = ap.parse_args()

    if args.list:
        return cmd_list(args)
    if args.query:
        return cmd_query(args)

    if args.demo:
        base = B.pillars_from_solar(1990, 6, 15, 14, 0)
    elif args.solar:
        try:
            date, hm = args.solar.split()
            y, m, d = (int(x) for x in date.split("-"))
            h, mi = (int(x) for x in hm.split(":"))
        except ValueError:
            print('时间格式应为 "YYYY-MM-DD HH:MM"')
            return 1
        base = B.pillars_from_solar(y, m, d, h, mi)
    elif args.pillars:
        base = B.pillars_from_str(args.pillars)
    else:
        ap.print_help()
        return 0

    a = B.analyze(base, args.sex)
    print(B.text_report(a))
    if args.json:
        out = Path(args.json)
        out.write_text(json.dumps(a, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n完整结构化结果已写入: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
