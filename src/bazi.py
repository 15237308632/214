# -*- coding: utf-8 -*-
"""
八字命理知识库 · 排盘与分析引擎

能力边界(务必先读):
- 精确部分: 干支历换算(立春换年、节气换月、日柱、时柱)由 sxtwl 寿星天文历提供;
  十神、十二长生、纳音、空亡、合冲刑害、神煞、调候用神检索由本库规则表计算, 确定性可复现。
- 近似部分: 起运岁数按「三日为一岁、一日为四月」的传统折算, 未纳入真太阳时/经度订正;
  出生时间请以北京时间为准, 跨时区需自行换算。
- 判断部分: 格局仅做「月令透干初判」, 成格败格、相神、有情有力等须人工综合, 程序不代裁。
- 定位: 中国传统术数文献的结构化整理工具, 供文献学/民俗学研究, 不宣称预测能力,
  不构成任何人生、医疗、法律、投资决策依据。
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import sxtwl
except ImportError as e:
    raise SystemExit("缺少依赖 sxtwl (寿星天文历), 请执行: pip3 install sxtwl") from e

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TG = "甲乙丙丁戊己庚辛壬癸"
DZ = "子丑寅卯辰巳午未申酉戌亥"
WX = "木火土金水"
PILLAR_NAMES = ["年柱", "月柱", "日柱", "时柱"]
CN_TZ = timezone(timedelta(hours=8))


def load(name: str):
    p = DATA / name
    if not p.exists():
        raise FileNotFoundError(f"未找到 {p}, 请先运行 python3 src/build_data.py")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ 基础工具
def gan_wx(g: str) -> str:
    return load("tiangan.json")["干"][g]["五行"]


def gan_yy(g: str) -> str:
    return load("tiangan.json")["干"][g]["阴阳"]


def zhi_wx(z: str) -> str:
    return load("dizhi.json")["支"][z]["五行"]


def cang(z: str):
    return load("dizhi.json")["支"][z]["藏干"]


def ten_god(day_gan: str, other_gan: str) -> str:
    return load("shishen.json")["十神表"][day_gan][other_gan]


def hour_branch(hour: int) -> str:
    """23-1 子, 1-3 丑 ... 21-23 亥。"""
    return DZ[((hour + 1) // 2) % 12]


def hour_gan(day_gan: str, hz: str) -> str:
    """五鼠遁: 甲己还加甲, 乙庚丙作初, 丙辛从戊起, 丁壬庚子居, 戊癸壬子真。"""
    i = TG.index(day_gan)
    return TG[(2 * (i % 5) + DZ.index(hz)) % 10]


def sexagenary_index(gz: str) -> int:
    """返回 0..59, 六十甲子序。"""
    g, z = gz[0], gz[1]
    for i in range(60):
        if TG[i % 10] == g and DZ[i % 12] == z:
            return i
    raise ValueError(f"非法干支: {gz}")


def gz_by_index(i: int) -> str:
    i %= 60
    return TG[i % 10] + DZ[i % 12]


def local_to_jd(y, m, d, h=0, mi=0) -> float:
    """北京时间(UTC+8)转儒略日。"""
    dt = datetime(y, m, d, h, mi, tzinfo=CN_TZ)
    return 2440587.5 + dt.timestamp() / 86400.0


# ------------------------------------------------------------------ 排四柱
def pillars_from_solar(y: int, m: int, d: int, h: int = 12, mi: int = 0,
                       late_zi: bool = True) -> dict:
    """
    由公历(北京时间)排四柱。
    late_zi=True  时 23:00-24:00 归次日(子时换日, 通行做法);
    late_zi=False 时 23:00-24:00 仍归当日(晚子时派)。
    """
    if not (1 <= m <= 12 and 1 <= d <= 31 and 0 <= h <= 23 and 0 <= mi <= 59):
        raise ValueError("日期或时间超出范围")
    day_date = datetime(y, m, d)
    use_day = day_date + timedelta(days=1) if (late_zi and h == 23) else day_date
    day = sxtwl.fromSolar(use_day.year, use_day.month, use_day.day)

    def gz(obj):
        return TG[obj.tg] + DZ[obj.dz]

    hz = hour_branch(h)
    pillars = [gz(day.getYearGZ()), gz(day.getMonthGZ()), gz(day.getDayGZ()),
               hour_gan(TG[day.getDayGZ().tg], hz) + hz]
    return {
        "输入": f"{y:04d}-{m:02d}-{d:02d} {h:02d}:{mi:02d} (北京时间 UTC+8)",
        "四柱": pillars,
        "日主": pillars[2][0],
        "月令": pillars[1][1],
        "子时换日": "23时归次日" if late_zi else "23时仍归当日(晚子时派)",
        "换年": "立春", "换月": "节(非气)",
        "节气当天": "是" if day.hasJieQi() else "否",
        "注意": "节气日前后出生请核对交节时刻; 本函数按日粒度取干支, 未纳入真太阳时。",
    }


def pillars_from_str(s: str) -> dict:
    """由四柱字符串排盘, 形如 '丙午 己亥 戊子 乙卯' 或 '丙午,己亥,戊子,乙卯'。"""
    parts = [p for p in s.replace(",", " ").replace("，", " ").split() if p]
    if len(parts) != 4:
        raise ValueError("需要四柱, 例如: 丙午 己亥 戊子 乙卯")
    for p in parts:
        if len(p) != 2 or p[0] not in TG or p[1] not in DZ:
            raise ValueError(f"非法干支: {p}")
        sexagenary_index(p)
    return {"输入": s, "四柱": parts, "日主": parts[2][0], "月令": parts[1][1],
            "换年": "立春", "换月": "节(非气)", "注意": "直接给定四柱, 未经历法校验。"}


# ------------------------------------------------------------------ 十神 / 藏干
def ten_gods(pillars: list) -> dict:
    dg = pillars[2][0]
    out = {}
    for name, gz in zip(PILLAR_NAMES, pillars):
        g, z = gz[0], gz[1]
        out[name] = {
            "干支": gz,
            "天干十神": "日主" if name == "日柱" else ten_god(dg, g),
            "藏干": [{"干": x, "十神": ten_god(dg, x), "位": "本气" if i == 0 else "中气" if i == 1 else "余气"}
                     for i, x in enumerate(cang(z))],
        }
    return {"日主": dg, "四柱": out}


# ------------------------------------------------------------------ 五行 / 旺衰
def wuxing_profile(pillars: list) -> dict:
    """天干各计 1, 地支本气计 1、中气 0.6、余气 0.3(仅为可视化权重, 非典籍定法)。"""
    weight = [1.0, 0.6, 0.3]
    score = {w: 0.0 for w in WX}
    detail = []
    for name, gz in zip(PILLAR_NAMES, pillars):
        score[gan_wx(gz[0])] += 1.0
        detail.append({"柱": name, "干": gz[0], "五行": gan_wx(gz[0]), "权重": 1.0})
        for i, x in enumerate(cang(gz[1])):
            w = weight[min(i, 2)]
            score[gan_wx(x)] += w
            detail.append({"柱": name, "藏干": x, "五行": gan_wx(x), "权重": w})
    month_zhi = pillars[1][1]
    season = "春" if month_zhi in "寅卯辰" else "夏" if month_zhi in "巳午未" else "秋" if month_zhi in "申酉戌" else "冬"
    wx_state = load("wuxing.json")["四季旺相休囚死"][season]
    return {
        "季节": season, "月令五行": zhi_wx(month_zhi),
        "旺相休囚死": wx_state,
        "五行计数": {k: round(v, 2) for k, v in score.items()},
        "明细": detail,
        "note": "加权计数只是可视化辅助, 典籍论旺衰以「得时、得地、得势」与月令司令为准, 不可仅以数量定强弱。",
    }


def changsheng_profile(pillars: list) -> dict:
    dg = pillars[2][0]
    t = load("changsheng.json")["表"][dg]
    return {"日主": dg, "四支": {name: {"支": gz[1], "阶段": t[gz[1]]}
                                 for name, gz in zip(PILLAR_NAMES, pillars)},
            "note": load("changsheng.json")["meta"]["异说"]}


# ------------------------------------------------------------------ 纳音 / 空亡
def nayin_profile(pillars: list) -> dict:
    table = load("nayin.json")["六十甲子"]
    m = {x["干支"]: x for x in table}
    day = m[pillars[2]]
    return {
        "四柱纳音": [{"柱": n, "干支": gz, "纳音": m[gz]["纳音"]} for n, gz in zip(PILLAR_NAMES, pillars)],
        "日柱旬": day["旬"], "空亡": day["空亡"],
        "落空": [n for n, gz in zip(PILLAR_NAMES, pillars) if gz[1] in day["空亡"]],
        "note": load("nayin.json")["meta"]["说明"],
    }


# ------------------------------------------------------------------ 干支作用
def relations_profile(pillars: list) -> dict:
    r = load("hechong.json")
    gans = [gz[0] for gz in pillars]
    zhis = [gz[1] for gz in pillars]
    found = {"天干合": [], "天干冲": [], "地支六合": [], "地支三合": [], "地支三会": [],
             "地支六冲": [], "相刑": [], "六害": []}
    for i in range(4):
        for j in range(i + 1, 4):
            pair = gans[i] + gans[j]
            for he in r["天干"]["五合"]:
                if set(he) == {gans[i], gans[j]}:
                    found["天干合"].append({"柱": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "合": he, "化": r["天干"]["五合"][he]})
            for ch in r["天干"]["四冲"]:
                if set(ch["对"]) == {gans[i], gans[j]}:
                    found["天干冲"].append({"柱": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "冲": ch["对"]})
            zpair = {zhis[i], zhis[j]}
            for he, hua in r["地支"]["六合"].items():
                if set(he) == zpair:
                    found["地支六合"].append({"柱": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "合": he, "化": hua})
            for ch in r["地支"]["六冲"]:
                if set(ch) == zpair:
                    found["地支六冲"].append({"柱": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "冲": ch})
            for hai in r["地支"]["六害"]:
                if set(hai) == zpair:
                    found["六害"].append({"柱": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "害": hai})
    for ju, hua in r["地支"]["三合局"].items():
        # 必须三个不同地支齐备, 重复地支(如午、午、未)不得算成局
        if set(ju) <= set(zhis):
            found["地支三合"].append({"局": ju, "化": hua,
                                     "柱": [PILLAR_NAMES[k] for k, z in enumerate(zhis) if z in ju]})
    for fang, hua in r["地支"]["三会方"].items():
        if set(fang) <= set(zhis):
            found["地支三会"].append({"方": fang, "化": hua,
                                     "柱": [PILLAR_NAMES[k] for k, z in enumerate(zhis) if z in fang]})
    xing = r["地支"]["相刑"]
    for key, label in [("寅巳申", xing["寅巳申"]), ("丑未戌", xing["丑未戌"]), ("子卯", xing["子卯"])]:
        if set(key) <= set(zhis):
            found["相刑"].append({"刑": key, "名": label,
                                 "柱": [PILLAR_NAMES[k] for k, z in enumerate(zhis) if z in key]})
    ziji = xing["自刑"]
    hit = [PILLAR_NAMES[k] for k, z in enumerate(zhis) if z in ziji]
    if len(hit) >= 2:
        found["相刑"].append({"刑": "自刑", "名": "辰午酉亥自刑", "柱": hit})
    found["辨"] = r["关键辨"]
    return found


# ------------------------------------------------------------------ 神煞
def shensha_profile(pillars: list) -> dict:
    s = load("shensha.json")
    dg = pillars[2][0]
    day_zhi = pillars[2][1]
    year_zhi = pillars[0][1]
    month_zhi = pillars[1][1]
    zhis = [gz[1] for gz in pillars]
    hits = {}

    for key, rule in s["以日干(或年干)起"].items():
        if not isinstance(rule, dict) or key.startswith("note"):
            continue
        val = None
        for k, v in rule.items():
            if dg in k:
                val = v
                break
        if val is None:
            continue
        want = val if isinstance(val, list) else [val]
        hit = [PILLAR_NAMES[i] for i, z in enumerate(zhis) if z in want]
        if hit:
            hits[key] = {"起例": "".join(want), "落": hit}

    # 以三合局起的神煞: 年支或日支任一入局即查
    for key, rule in s["以年支或日支三合局起"].items():
        for ju, target in rule.items():
            if year_zhi in ju or day_zhi in ju:
                hit = [PILLAR_NAMES[i] for i, z in enumerate(zhis) if z == target]
                if hit:
                    hits[key] = {"起例": f"{ju}→{target}", "落": hit}
                break

    for key, rule in s["以月支起"].items():
        if key == "天德贵人":
            idx = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"].index(month_zhi)
            val = list(rule.values())[idx]
        else:
            val = None
            for ju, v in rule.items():
                if month_zhi in ju:
                    val = v
                    break
        if val:
            hit = [PILLAR_NAMES[i] for i, gz in enumerate(pillars) if val in gz]
            if hit:
                hits[key] = {"起例": val, "落": hit}

    return {"命中": hits, "权重": s["meta"]["定位"], "note": s["meta"]["说明"],
            "羊刃异说": s["以日干(或年干)起"]["note_羊刃"]}


# ------------------------------------------------------------------ 调候
def tiaohou_profile(pillars: list) -> dict:
    t = load("tiaohou.json")
    dg, mz = pillars[2][0], pillars[1][1]
    idx = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"].index(mz)
    row = t["表"][dg][idx]
    gans = [gz[0] for gz in pillars]
    zhis = [gz[1] for gz in pillars]
    # 原文常以日主自身作主语(如「辛无己不生」), 机器提取会混入日主, 此处剔除
    cand = [x for x in row["yongshen候选"] if x != dg]
    return {
        "日主": dg, "月令": mz, "节": row["节"], "季": row["季"],
        "原文提要": row["text"], "候选用神": cand,
        "候选用神是否透干": {g: (g in gans) for g in cand},
        "候选用神是否得地": {g: any(g in cang(z) for z in zhis) for g in cand},
        "优先级异说": t["meta"]["优先级异说"],
        "上半月下半月": t["meta"]["上半月下半月"],
        "来源": t["meta"]["书名"],
        "note": "yongshen候选为按原文出现顺序机器提取, 取用须读原文; 透干/得地仅为检索辅助。",
    }


# ------------------------------------------------------------------ 格局初判
def geju_profile(pillars: list) -> dict:
    g = load("geju.json")
    dg = pillars[2][0]
    mz = pillars[1][1]
    hidden = cang(mz)
    exposed = [(PILLAR_NAMES[i], gz[0], ten_god(dg, gz[0]))
               for i, gz in enumerate(pillars) if i != 2 and gz[0] in hidden]
    ben = hidden[0]
    ben_ss = ten_god(dg, ben)
    if ben_ss in ("比肩", "劫财"):
        ge = "建禄月劫" if ben_ss == "比肩" else "月劫(阳刃须另辨)"
        reason = "月令本气为比劫, 月令无用神, 须另取财官煞食透干会支"
    elif exposed:
        # 优先本气透出
        pick = next((x for x in exposed if x[1] == ben), exposed[0])
        ge, reason = pick[2] + "格", f"月令藏干 {pick[1]}({pick[2]}) 透于{pick[0]}"
    else:
        ge, reason = ben_ss + "格", f"月令藏干未透, 以本气 {ben}({ben_ss}) 定格"
    alias = {"七杀": "七杀(偏官)"}
    info = g["八格"].get(alias.get(ben_ss, ben_ss), {})
    return {
        "初判": ge, "依据": reason, "月令": mz, "藏干": hidden,
        "透出": exposed, "顺逆": info.get("顺逆"),
        "成格参考": info.get("成"), "败格参考": info.get("败"),
        "相神": g["成败救应"]["相神"],
        "原文": g["meta"]["原文"],
        "限定": "仅为月令透干初判。成格败格还须审相神、位置、刑冲会合、有情有力、清浊纯杂, 程序不作最终裁定。",
        "异说": g["note"],
    }


# ------------------------------------------------------------------ 大运
JIE_INDEX = {1: "小寒", 3: "立春", 5: "惊蛰", 7: "清明", 9: "立夏", 11: "芒种",
             13: "小暑", 15: "立秋", 17: "白露", 19: "寒露", 21: "立冬", 23: "大雪"}


def jeqi_jd_list(year: int):
    out = []
    for y in (year - 1, year, year + 1):
        for jq in sxtwl.getJieQiByYear(y):
            if jq.jqIndex in JIE_INDEX:
                out.append((jq.jd, JIE_INDEX[jq.jqIndex]))
    return sorted(set(out))


def dayun_profile(base: dict, sex: str = "男", steps: int = 10) -> dict:
    """
    大运顺逆: 阳年男 / 阴年女 顺行; 阴年男 / 阳年女 逆行。
    起运按「三日折一岁」传统算法, 结果为近似值。
    """
    pillars = base["四柱"]
    year_gan = pillars[0][0]
    yang = gan_yy(year_gan) == "阳"
    forward = (yang and sex in ("男", "M", "m")) or ((not yang) and sex in ("女", "F", "f"))
    y, m, d = (int(x) for x in base["输入"][:10].split("-")) if base["输入"][:4].isdigit() else (None, None, None)
    h, mi = (int(x) for x in base["输入"][11:16].split(":")) if ":" in base["输入"] else (12, 0)
    if y:
        birth_jd = local_to_jd(y, m, d, h, mi)
        jqs = jeqi_jd_list(y)
        deltas = [(abs(jd - birth_jd), jd - birth_jd, nm) for jd, nm in jqs]
        target = min((x for x in deltas if (x[1] > 0) == forward), default=min(deltas))
        days = abs(target[1])
        start_age = days / 3.0
        start_note = f"距{'下一' if forward else '上一'}节「{target[2]}」约 {days:.2f} 天, 三日折一岁 ≈ {start_age:.2f} 岁起运(近似)"
    else:
        start_age, start_note = 0.0, "由四柱直接给定, 未提供出生时刻, 无法折算起运岁数"

    mi_idx = sexagenary_index(pillars[1])
    seq = []
    for k in range(1, steps + 1):
        gz = gz_by_index(mi_idx + (k if forward else -k))
        seq.append({"序": k, "干支": gz,
                    "天干十神": ten_god(pillars[2][0], gz[0]),
                    "约起始岁": round(start_age + (k - 1) * 10, 2),
                    "约区间": f"{round(start_age + (k - 1) * 10, 1)}–{round(start_age + k * 10, 1)} 岁"})
    return {"顺逆": "顺行" if forward else "逆行", "判定": f"年干 {year_gan}({'阳' if yang else '阴'}) × {sex}",
            "起运": start_note, "大运": seq,
            "note": "未纳入真太阳时与出生地经度订正; 交节前后出生请复核节气精确时刻。"}


# ------------------------------------------------------------------ 汇总
def analyze(base: dict, sex: str = "男") -> dict:
    p = base["四柱"]
    return {
        "免责": "本结果为传统术数文献的结构化整理, 供文化研究参考, 不宣称预测能力, 不构成任何决策依据。",
        "排盘": base,
        "十神": ten_gods(p),
        "五行旺衰": wuxing_profile(p),
        "十二长生": changsheng_profile(p),
        "纳音空亡": nayin_profile(p),
        "干支作用": relations_profile(p),
        "神煞": shensha_profile(p),
        "调候": tiaohou_profile(p),
        "格局初判": geju_profile(p),
        "大运": dayun_profile(base, sex),
        "判局次序": [
            "1. 定月令、节气、日主(历法层)",
            "2. 调候: 冬夏先寻水火, 春秋再看燥湿 —— 《穷通宝鉴》",
            "3. 格局: 月令透干定格, 审成败救应与相神 —— 《子平真诠》",
            "4. 旺衰理气: 得时得地得势、衰旺真机、中和流通 —— 《滴天髓》",
            "5. 神煞/纳音/六亲: 辅助参断 —— 《渊海子平》《三命通会》",
            "6. 岁运: 大运顺逆与流年引发",
            "注意: 三套坐标系(格局/旺衰/调候)不可混用, 须显式声明采用哪一套为主。",
        ],
    }


def text_report(a: dict) -> str:
    L = []
    L.append("=" * 68)
    L.append("八字命理知识库 · 结构化分析报告")
    L.append(a["免责"])
    L.append("=" * 68)
    b = a["排盘"]
    L.append(f"\n【排盘】{b['输入']}")
    L.append("  " + "  ".join(f"{n}:{gz}" for n, gz in zip(PILLAR_NAMES, b["四柱"])))
    L.append(f"  日主 {b['日主']}  月令 {b['月令']}  ({b.get('换年','')}换年 / {b.get('换月','')}换月)")
    if b.get("注意"):
        L.append("  ! " + b["注意"])

    L.append("\n【十神与藏干】")
    for n, v in a["十神"]["四柱"].items():
        L.append(f"  {n} {v['干支']}  天干:{v['天干十神']}  藏干:" +
                 " ".join(f"{x['干']}({x['十神']}/{x['位']})" for x in v["藏干"]))

    w = a["五行旺衰"]
    L.append(f"\n【五行与月令】季:{w['季节']}  月令五行:{w['月令五行']}")
    L.append("  五行加权: " + "  ".join(f"{k}{v}" for k, v in w["五行计数"].items()))
    L.append("  旺相休囚死: " + "  ".join(f"{k}={v}" for k, v in w["旺相休囚死"].items()))

    cs = a["十二长生"]["四支"]
    L.append("\n【十二长生(日主对四支)】 " + "  ".join(f"{n}:{v['支']}={v['阶段']}" for n, v in cs.items()))

    ny = a["纳音空亡"]
    L.append("\n【纳音与空亡】 " + "  ".join(f"{x['柱']}:{x['纳音']}" for x in ny["四柱纳音"]))
    L.append(f"  {ny['日柱旬']}  空亡:{'、'.join(ny['空亡'])}  落空柱:{'、'.join(ny['落空']) or '无'}")

    r = a["干支作用"]
    L.append("\n【干支作用(实际出现)】")
    for k in ["天干合", "天干冲", "地支六合", "地支三合", "地支三会", "地支六冲", "相刑", "六害"]:
        if r[k]:
            L.append(f"  {k}: " + "; ".join(str(x) for x in r[k]))

    ss = a["神煞"]["命中"]
    L.append("\n【神煞(辅助)】 " + ("; ".join(f"{k}→{'、'.join(v['落'])}" for k, v in ss.items()) or "无起例明确者"))

    t = a["调候"]
    L.append(f"\n【调候 · {t['日主']}生{t['月令']}月({t['季']}/{t['节']})】")
    L.append("  " + t["原文提要"])
    L.append("  候选用神: " + "、".join(t["候选用神"]))
    L.append("  透干: " + "  ".join(f"{k}:{'是' if v else '否'}" for k, v in t["候选用神是否透干"].items()))

    g = a["格局初判"]
    L.append(f"\n【格局初判】{g['初判']}  顺逆:{g['顺逆']}")
    L.append("  依据: " + g["依据"])
    L.append("  " + g["限定"])

    dy = a["大运"]
    L.append(f"\n【大运】{dy['顺逆']}  {dy['起运']}")
    L.append("  " + " ".join(f"{x['干支']}({x['天干十神']})" for x in dy["大运"][:8]))

    L.append("\n【判局次序】")
    for x in a["判局次序"]:
        L.append("  " + x)
    L.append("\n" + "=" * 68)
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print(text_report(analyze(pillars_from_solar(1990, 6, 15, 14, 0), "男")))
    else:
        print(__doc__)
