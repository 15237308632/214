# -*- coding: utf-8 -*-
"""生成自包含的 index.html（数据内联，双击即可离线使用）。

用法: python3 src/build_html.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"

payload = {
    "classics": json.loads((D / "classics.json").read_text(encoding="utf-8"))["五书"],
    "tiaohou": json.loads((D / "tiaohou.json").read_text(encoding="utf-8")),
    "shishen": json.loads((D / "shishen.json").read_text(encoding="utf-8")),
    "changsheng": json.loads((D / "changsheng.json").read_text(encoding="utf-8")),
    "nayin": json.loads((D / "nayin.json").read_text(encoding="utf-8"))["六十甲子"],
    "hechong": json.loads((D / "hechong.json").read_text(encoding="utf-8")),
    "dizhi": json.loads((D / "dizhi.json").read_text(encoding="utf-8")),
    "shensha": json.loads((D / "shensha.json").read_text(encoding="utf-8")),
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>八字命理知识库 · 子平五经检索</title>
<style>
:root{
  --bg:#f6f3ec; --paper:#fffdf8; --ink:#262522; --muted:#6d675d; --line:#ddd6c8;
  --accent:#9c3b2e; --accent-soft:#f3e6e1; --head:#ebe4d6; --ok:#3f6b4a; --shadow:0 2px 12px rgba(60,50,35,.08);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 "Noto Serif CJK SC","Songti SC","SimSun",Georgia,serif}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 70px}
header{border-bottom:3px double var(--accent);padding-bottom:18px;margin-bottom:18px}
h1{margin:0 0 6px;font-size:27px;letter-spacing:2px}
.sub{color:var(--muted);font-size:13px;letter-spacing:1px}
.warn{background:var(--accent-soft);border-left:4px solid var(--accent);padding:12px 16px;margin:16px 0 22px;font-size:13.5px;border-radius:0 6px 6px 0}
nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
nav button{cursor:pointer;border:1px solid var(--line);background:var(--paper);color:var(--ink);padding:8px 15px;border-radius:20px;font-size:14px;font-family:inherit;transition:.15s}
nav button:hover{border-color:var(--accent)}
nav button.on{background:var(--accent);border-color:var(--accent);color:#fff}
.panel{display:none;background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:22px;box-shadow:var(--shadow)}
.panel.on{display:block}
h2{font-size:19px;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 8px;color:var(--accent)}
p{margin:8px 0}
.muted{color:var(--muted);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:var(--head);font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#faf7f0}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:16px;padding:14px;background:#faf7f0;border:1px solid var(--line);border-radius:8px}
select,input[type=text]{font-family:inherit;font-size:14px;padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink);min-width:96px}
input[type=text]{flex:1;min-width:180px}
.card{border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:0 8px 8px 0;padding:16px 18px;margin:14px 0;background:#fffefa}
.card h3{margin:0 0 6px}
.kv{display:grid;grid-template-columns:88px 1fr;gap:4px 12px;font-size:13.5px;margin-top:8px}
.kv b{color:var(--muted);font-weight:600}
ul{padding-left:20px;margin:8px 0}
li{margin:4px 0}
.tag{display:inline-block;background:var(--accent-soft);color:var(--accent);border-radius:4px;padding:1px 7px;font-size:12px;margin-right:5px}
.hit{background:#fff3cd;padding:0 2px}
.matrix td,.matrix th{text-align:center;padding:5px 4px;font-size:12.5px;white-space:nowrap}
.matrix th:first-child{background:var(--head)}
.hl{background:#fdeee0;font-weight:600}
code{background:#f0ece2;padding:1px 5px;border-radius:4px;font-size:13px}
footer{margin-top:30px;color:var(--muted);font-size:12.5px;text-align:center;border-top:1px solid var(--line);padding-top:16px}
a{color:var(--accent)}
@media(max-width:640px){.wrap{padding:16px 12px 50px}.kv{grid-template-columns:1fr}.panel{padding:14px}table{font-size:12px}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>八字命理知识库</h1>
  <div class="sub">子平五经结构化研读库 · 渊海子平 / 滴天髓 / 三命通会 / 子平真诠 / 穷通宝鉴 · v1.0</div>
</header>

<div class="warn"><b>定位与免责：</b>本页是对五部中国传统术数典籍的<strong>文献整理与数据检索</strong>，供文献学、思想史、民俗学研究参考。八字命理属于传统术数、<strong>不是科学</strong>；本库不宣称预测能力，不提供也不构成任何人生、婚恋、医疗、法律、投资决策依据。库内「吉凶」等表述均为古籍记录的转述。</div>

<nav id="nav"></nav>

<div class="panel" id="p-classics"><h2>五书文献卡片</h2><div id="classics"></div></div>

<div class="panel" id="p-tiaohou">
  <h2>《穷通宝鉴》十干 × 十二月调候用神（120 条）</h2>
  <div class="controls">
    <label>日干 <select id="th-gan"></select></label>
    <label>月支 <select id="th-zhi"></select></label>
    <input type="text" id="th-search" placeholder="全文检索 120 条提要，如：丙火 / 上半月 / 通根">
  </div>
  <div id="th-result"></div>
  <h3>全部条目</h3>
  <div id="th-table"></div>
  <p class="muted" id="th-meta"></p>
</div>

<div class="panel" id="p-shishen">
  <h2>十神表（日干 × 他干，100 格）</h2>
  <p class="muted">规则：同我 / 我生 / 我克 / 克我 / 生我 × 阴阳同异。本表由规则推导生成，非手抄。</p>
  <div id="ss-table"></div>
  <h3>沈氏四吉四凶</h3>
  <div id="ss-note"></div>
</div>

<div class="panel" id="p-changsheng">
  <h2>十干十二长生（阳顺阴逆 · 戊己寄火宫）</h2>
  <div id="cs-table"></div>
  <p class="muted" id="cs-note"></p>
</div>

<div class="panel" id="p-nayin">
  <h2>六十甲子纳音与旬空</h2>
  <div class="controls"><input type="text" id="ny-search" placeholder="检索干支或纳音，如：甲子 / 海中金 / 甲辰旬"></div>
  <div id="ny-table"></div>
  <p class="muted">纳音属李虚中古法层；任铁樵《滴天髓阐微》、《子平真诠·论星辰无关格局》均不取以定格局。本库保留仅为文献完整性。</p>
</div>

<div class="panel" id="p-rel">
  <h2>干支作用关系</h2>
  <div id="rel"></div>
</div>

<div class="panel" id="p-shensha">
  <h2>神煞起例</h2>
  <div id="ss2"></div>
</div>

<div class="panel" id="p-help">
  <h2>使用说明与判局次序</h2>
  <h3>命令行</h3>
  <p><code>python3 src/build_data.py</code> 重建数据 ｜ <code>python3 -m unittest discover -s tests -v</code> 18 项校验</p>
  <p><code>python3 src/cli.py --solar "1990-06-15 14:00" --sex 男</code> 由公历排盘并输出完整报告</p>
  <p><code>python3 src/cli.py --pillars "庚午 壬午 辛亥 乙未"</code> 直接给四柱</p>
  <p><code>python3 src/cli.py --query 调候 甲 子</code> 单条查表</p>
  <h3>判局次序</h3>
  <ol>
    <li>定月令、节气、日主（历法层）</li>
    <li>调候：冬夏先寻水火，春秋再看燥湿 ——《穷通宝鉴》</li>
    <li>格局：月令透干定格，审成败救应与相神 ——《子平真诠》</li>
    <li>旺衰理气：得时得地得势、衰旺真机、中和流通 ——《滴天髓》</li>
    <li>神煞 / 纳音 / 六亲：辅助参断 ——《渊海子平》《三命通会》</li>
    <li>岁运：大运顺逆与流年引发</li>
  </ol>
  <p class="muted"><b>注意：</b>三套坐标系（格局 / 旺衰 / 调候）不可混用，须先显式声明主用哪一套。详见 <code>docs/09-判局SOP与流派分歧.md</code>。</p>
  <h3>本页数据来源</h3>
  <p class="muted">全部内容由 <code>src/build_data.py</code> 生成并内联，双击即可离线使用；无外部依赖、无网络请求。完整研读笔记见 <code>docs/</code>。</p>
</div>

<footer>八字命理知识库 v1.0 · 2026-11-10 · 传统术数文献的结构化整理，非预测工具</footer>
</div>

<script>
const DATA = __DATA__;
const TG = "甲乙丙丁戊己庚辛壬癸";
const DZ = "子丑寅卯辰巳午未申酉戌亥";
const MONTHS = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"];
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* 导航 */
const tabs = [["classics","五书卡片"],["tiaohou","调候 120 条"],["shishen","十神表"],["changsheng","十二长生"],["nayin","纳音空亡"],["rel","合冲刑害"],["shensha","神煞起例"],["help","使用说明"]];
$("#nav").innerHTML = tabs.map((t,i)=>`<button data-k="${t[0]}" class="${i===0?'on':''}">${t[1]}</button>`).join("");
function show(k){
  document.querySelectorAll("nav button").forEach(b=>b.classList.toggle("on",b.dataset.k===k));
  document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("on",p.id==="p-"+k));
}
$("#nav").addEventListener("click",e=>{if(e.target.dataset.k)show(e.target.dataset.k)});

/* 五书 */
$("#classics").innerHTML = DATA.classics.map(c=>`
 <div class="card"><h3>${c["排序"]}. 《${esc(c["书名"])}》 <span class="tag">${esc(c["卷帙"])}</span></h3>
 <div class="kv">
  <b>年代</b><span>${esc(c["年代"])}</span>
  <b>作者/注者</b><span>${esc(c["作者"])}</span>
  <b>核心命题</b><span>${esc(c["核心命题"])}</span>
  <b>定位</b><span>${esc(c["定位"])}</span>
  <b>版本异说</b><span>${esc(c["版本异说"]||"—")}</span>
  <b>篇章结构</b><span>${(c["结构"]||[]).map(esc).join("；")}</span>
 </div>
 <p class="muted">来源：${(c["来源"]||[]).map(u=>`<a href="${u}" target="_blank" rel="noopener">${esc(new URL(u).hostname)}</a>`).join(" · ")}</p>
 </div>`).join("");

/* 调候 */
const thGan=$("#th-gan"), thZhi=$("#th-zhi");
thGan.innerHTML=[...TG].map(g=>`<option value="${g}">${g}</option>`).join("");
thZhi.innerHTML=MONTHS.map((z,i)=>`<option value="${i}">${z}月（${i+1}月）</option>`).join("");
function thRow(g,i){
  const r=DATA.tiaohou["表"][g][i];
  return `<div class="card"><h3>${g} 生 ${r["月支"]}月 <span class="tag">${r["季"]}</span><span class="tag">${r["节"]}</span></h3>
   <p>${esc(r["text"])}</p>
   <p class="muted">候选用神（机器提取、已剔除日主）：<b>${r["yongshen候选"].filter(x=>x!==g).join("、")||"—"}</b>　｜　月序 ${r["月序"]}</p></div>`;
}
function renderTh(){
  const g=thGan.value,i=+thZhi.value,q=$("#th-search").value.trim();
  $("#th-result").innerHTML=thRow(g,i);
  let rows=[];
  [...TG].forEach(gg=>DATA.tiaohou["表"][gg].forEach((r,ii)=>rows.push({g:gg,r})));
  const hit=rows.filter(x=>!q||x.r.text.includes(q)||x.g.includes(q));
  $("#th-table").innerHTML=`<table><thead><tr><th>日干</th><th>月支</th><th>季/节</th><th>原文提要</th><th>候选用神</th></tr></thead><tbody>`+
    hit.map(x=>`<tr${x.g===g&&x.r["月支"]===MONTHS[i]?' class="hl"':''}><td>${x.g}</td><td>${x.r["月支"]}</td><td>${x.r["季"]}/${x.r["节"]}</td><td>${esc(x.r.text)}</td><td>${x.r["yongshen候选"].filter(y=>y!==x.g).join("、")}</td></tr>`).join("")+
    `</tbody></table>`;
  $("#th-meta").textContent=`共 ${rows.length} 条，当前显示 ${hit.length} 条｜${DATA.tiaohou.meta["核心命题"]}｜优先级异说：${DATA.tiaohou.meta["优先级异说"]}`;
}
[thGan,thZhi,$("#th-search")].forEach(el=>el.addEventListener("input",renderTh));
renderTh();

/* 十神表 */
$("#ss-table").innerHTML=`<table class="matrix"><thead><tr><th>日干 ＼ 他干</th>${[...TG].map(g=>`<th>${g}</th>`).join("")}</tr></thead><tbody>`+
 [...TG].map(g=>`<tr><th>${g}</th>${[...TG].map(o=>`<td>${DATA.shishen["十神表"][g][o]}</td>`).join("")}</tr>`).join("")+`</tbody></table>`;
const s4=DATA.shishen["沈氏四吉四凶"];
$("#ss-note").innerHTML=`<p>四吉神（顺用）：<b>${s4["四吉神(顺用)"].join("、")}</b>　｜　四凶神（逆用）：<b>${s4["四凶神(逆用)"].join("、")}</b></p>
 <p>原文：${esc(s4["原文"])}</p><p class="muted">${esc(s4["重要限定"])}</p>`;

/* 长生 */
const csStages=DATA.changsheng["阶段"];
$("#cs-table").innerHTML=`<table class="matrix"><thead><tr><th>日干 ＼ 地支</th>${[...DZ].map(z=>`<th>${z}</th>`).join("")}</tr></thead><tbody>`+
 [...TG].map(g=>`<tr><th>${g}</th>${[...DZ].map(z=>`<td>${DATA.changsheng["表"][g][z]}</td>`).join("")}</tr>`).join("")+`</tbody></table>`;
$("#cs-note").textContent=DATA.changsheng.meta["异说"];

/* 纳音 */
function renderNy(){
 const q=$("#ny-search").value.trim();
 const rows=DATA.nayin.filter(x=>!q||x["干支"].includes(q)||x["纳音"].includes(q)||x["旬"].includes(q));
 $("#ny-table").innerHTML=`<table><thead><tr><th>序</th><th>干支</th><th>纳音</th><th>旬</th><th>空亡</th></tr></thead><tbody>`+
  rows.map(x=>`<tr><td>${x["序"]}</td><td><b>${x["干支"]}</b></td><td>${x["纳音"]}</td><td>${x["旬"]}</td><td>${x["空亡"].join("、")}</td></tr>`).join("")+`</tbody></table>`+
  `<p class="muted">显示 ${rows.length} / 60 条</p>`;
}
$("#ny-search").addEventListener("input",renderNy);renderNy();

/* 合冲刑害 */
const R=DATA.hechong;
function kvTable(obj,title,cols){return `<h3>${title}</h3><table><thead><tr><th>${cols[0]}</th><th>${cols[1]}</th></tr></thead><tbody>`+Object.entries(obj).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(typeof v==="object"?JSON.stringify(v):v)}</td></tr>`).join("")+`</tbody></table>`}
function listTable(arr,title){return `<h3>${title}</h3><p>${arr.map(esc).join("　·　")}</p>`}
$("#rel").innerHTML=
  kvTable(R["天干"]["五合"],"天干五合",["合","化"])+
  listTable(R["天干"]["四冲"].map(x=>x["对"]),"天干四冲")+
  kvTable(R["地支"]["六合"],"地支六合",["合","化"])+
  kvTable(R["地支"]["三合局"],"三合局",["局","化"])+
  kvTable(R["地支"]["三会方"],"三会方",["方","化"])+
  listTable(R["地支"]["六冲"],"六冲")+
  `<h3>相刑</h3><p>寅巳申：${R["地支"]["相刑"]["寅巳申"]}　｜　丑未戌：${R["地支"]["相刑"]["丑未戌"]}　｜　子卯：${R["地支"]["相刑"]["子卯"]}　｜　自刑：${R["地支"]["相刑"]["自刑"].join("、")}</p>`+
  listTable(R["地支"]["六害"],"六害")+listTable(R["地支"]["相破"],"相破（各本有异）")+
  `<h3>关键辨</h3><ul>${R["关键辨"].map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`+
  `<p class="muted">成局条件：三合 / 三会须三个不同地支齐备，重复地支不算。</p>`;

/* 神煞 */
const S=DATA.shensha;
$("#ss2").innerHTML=`<div class="warn"><b>层位说明：</b>${esc(S.meta["说明"])}　${esc(S.meta["定位"])}</div>`+
 ["以日干(或年干)起","以年支或日支三合局起","以月支起"].map(k=>
  `<h3>${esc(k)}</h3><table><thead><tr><th>神煞</th><th>起例</th></tr></thead><tbody>`+
  Object.entries(S[k]).filter(([a,v])=>typeof v==="object").map(([a,v])=>`<tr><td>${esc(a)}</td><td>${esc(JSON.stringify(v))}</td></tr>`).join("")+`</tbody></table>`).join("")+
 `<p class="muted">${esc(S["以日干(或年干)起"]["note_羊刃"])}</p><p class="muted">${esc(S.note)}</p>`;

show("classics");
</script>
</body>
</html>
"""

out = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
p = ROOT / "index.html"
p.write_text(out, encoding="utf-8")
print(f"已生成 {p}  ({p.stat().st_size} bytes)")
