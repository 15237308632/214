# -*- coding: utf-8 -*-
"""知识库一致性校验: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import bazi as B  # noqa: E402

TG = "甲乙丙丁戊己庚辛壬癸"
DZ = "子丑寅卯辰巳午未申酉戌亥"
GAN_WX = dict(zip(TG, ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]))
GAN_YY = dict(zip(TG, ["阳", "阴"] * 5))
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}


def independent_shishen(me_g, other_g):
    """与 build_data.py 无关的独立推导, 用于交叉校验十神表。"""
    me, other = GAN_WX[me_g], GAN_WX[other_g]
    same = GAN_YY[me_g] == GAN_YY[other_g]
    if other == me:
        return "比肩" if same else "劫财"
    if SHENG[me] == other:
        return "食神" if same else "伤官"
    if KE[me] == other:
        return "偏财" if same else "正财"
    if KE[other] == me:            # 他克我
        return "七杀" if same else "正官"
    if SHENG[other] == me:         # 他生我
        return "偏印" if same else "正印"
    raise AssertionError((me_g, other_g))


class TestData(unittest.TestCase):
    def test_十神表全量交叉校验(self):
        t = B.load("shishen.json")["十神表"]
        for g in TG:
            for o in TG:
                self.assertEqual(t[g][o], independent_shishen(g, o), f"{g}日见{o}")
        self.assertEqual(len(t), 10)

    def test_十二长生阳顺阴逆(self):
        t = B.load("changsheng.json")["表"]
        self.assertEqual(t["甲"]["亥"], "长生")
        self.assertEqual(t["甲"]["卯"], "帝旺")
        self.assertEqual(t["乙"]["午"], "长生")
        self.assertEqual(t["乙"]["寅"], "帝旺")
        self.assertEqual(t["戊"], t["丙"], "戊土寄火宫, 应与丙同")
        self.assertEqual(t["己"], t["丁"], "己土寄火宫, 应与丁同")
        for g in TG:
            self.assertEqual(len(t[g]), 12, f"{g} 应覆盖十二支")
            self.assertEqual(set(t[g].values()), set(B.load("changsheng.json")["阶段"]))

    def test_六十甲子纳音与旬空(self):
        rows = B.load("nayin.json")["六十甲子"]
        self.assertEqual(len(rows), 60)
        self.assertEqual(rows[0]["干支"], "甲子")
        self.assertEqual(rows[0]["纳音"], "海中金")
        self.assertEqual(rows[0]["空亡"], ["戌", "亥"])
        self.assertEqual(rows[10]["旬"], "甲戌旬")
        self.assertEqual(rows[10]["空亡"], ["申", "酉"])
        self.assertEqual(rows[59]["干支"], "癸亥")
        self.assertEqual(rows[59]["纳音"], "大海水")
        self.assertEqual(rows[59]["空亡"], ["子", "丑"])
        self.assertEqual(len({r["干支"] for r in rows}), 60)

    def test_调候一百二十条(self):
        t = B.load("tiaohou.json")
        self.assertEqual(list(t["表"].keys()), list(TG))
        self.assertEqual(sum(len(v) for v in t["表"].values()), 120)
        for g in TG:
            self.assertEqual([x["月支"] for x in t["表"][g]],
                             ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"])
            for row in t["表"][g]:
                self.assertTrue(row["text"].strip())

    def test_五书元数据完整(self):
        cs = B.load("classics.json")["五书"]
        self.assertEqual(len(cs), 5)
        for c in cs:
            for k in ("书名", "年代", "作者", "卷帙", "核心命题", "定位", "版本异说", "来源"):
                self.assertIn(k, c, f"《{c['书名']}》缺 {k}")


class TestPaiPan(unittest.TestCase):
    def test_立春换年(self):
        self.assertEqual(B.pillars_from_solar(2026, 1, 30)["四柱"][0], "乙巳")
        self.assertEqual(B.pillars_from_solar(2026, 2, 10)["四柱"][0], "丙午")

    def test_节气换月与时柱五鼠遁(self):
        p = B.pillars_from_solar(1990, 6, 15, 14, 0)["四柱"]
        self.assertEqual(p, ["庚午", "壬午", "辛亥", "乙未"])
        self.assertEqual(B.hour_gan("辛", "未"), "乙")
        self.assertEqual(B.hour_gan("甲", "子"), "甲")
        self.assertEqual(B.hour_gan("癸", "亥"), "癸")

    def test_月令为节气月(self):
        self.assertEqual(B.pillars_from_solar(2026, 11, 10)["四柱"][1], "己亥")
        self.assertEqual(B.pillars_from_solar(2026, 5, 10)["四柱"][1], "癸巳")

    def test_子时换日可选(self):
        a = B.pillars_from_solar(2026, 11, 10, 23, 0, late_zi=True)
        b = B.pillars_from_solar(2026, 11, 10, 23, 0, late_zi=False)
        self.assertNotEqual(a["四柱"][2], b["四柱"][2], "两派日柱应不同")
        self.assertIn("次日", a["子时换日"])

    def test_四柱字符串解析(self):
        self.assertEqual(B.pillars_from_str("庚午,壬午,辛亥,乙未")["日主"], "辛")
        with self.assertRaises(ValueError):
            B.pillars_from_str("庚午 壬午 辛亥")


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.a = B.analyze(B.pillars_from_solar(1990, 6, 15, 14, 0), "男")

    def test_报告结构齐全(self):
        for k in ("免责", "排盘", "十神", "五行旺衰", "十二长生", "纳音空亡",
                  "干支作用", "神煞", "调候", "格局初判", "大运", "判局次序"):
            self.assertIn(k, self.a)

    def test_重复地支不得误判三会三合(self):
        r = self.a["干支作用"]
        self.assertEqual(r["地支三会"], [], "午午未缺巳, 不得成巳午未三会")
        self.assertEqual(r["地支三合"], [])

    def test_格局顺逆映射(self):
        g = self.a["格局初判"]
        self.assertEqual(g["初判"], "七杀格")
        self.assertEqual(g["顺逆"], "逆用")

    def test_调候不混入日主(self):
        t = self.a["调候"]
        self.assertNotIn("辛", t["候选用神"], "辛为日主, 不应列为用神候选")

    def test_大运顺行首步(self):
        d = self.a["大运"]
        self.assertEqual(d["顺逆"], "顺行")
        self.assertEqual(d["大运"][0]["干支"], "癸未")

    def test_神煞天乙贵人(self):
        self.assertIn("天乙贵人", self.a["神煞"]["命中"])

    def test_文本报告可生成(self):
        s = B.text_report(self.a)
        self.assertIn("七杀格", s)
        self.assertIn("不宣称预测能力", s)
        self.assertGreater(len(s), 800)

    def test_起运折算近似值(self):
        d = self.a["大运"]
        self.assertIn("三日折一岁", d["起运"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
