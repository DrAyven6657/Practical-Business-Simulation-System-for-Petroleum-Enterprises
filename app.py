import json
import math
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "oil_enterprise.db"
HOST = "127.0.0.1"
PORT = 8000


HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>石油企业经营实战模拟系统</title>
  <style>
    :root {
      --bg: #f6f7f4;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #65717f;
      --line: #d9ded6;
      --brand: #126b5c;
      --brand-2: #b54b31;
      --gold: #c08a2c;
      --good: #247a4d;
      --bad: #b42318;
      --soft: #edf3ef;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    header {
      background: #102a2a;
      color: #fff;
      padding: 18px 28px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      border-bottom: 4px solid var(--gold);
    }
    header h1 {
      margin: 0;
      font-size: clamp(20px, 3vw, 30px);
      letter-spacing: 0;
    }
    header .sub { color: #cbd7d3; font-size: 14px; margin-top: 6px; }
    button {
      border: 0;
      background: var(--brand);
      color: #fff;
      padding: 10px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
      min-height: 40px;
    }
    button.secondary { background: #40545a; }
    button.warn { background: var(--brand-2); }
    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 22px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }
    .kpi, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, .05);
    }
    .kpi { padding: 16px; }
    .kpi span { color: var(--muted); font-size: 13px; }
    .kpi strong { display: block; font-size: 26px; margin-top: 8px; }
    .layout {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 16px;
      margin-top: 16px;
      align-items: start;
    }
    .panel { padding: 18px; }
    .panel h2 { margin: 0 0 14px; font-size: 18px; }
    label { display: block; font-size: 13px; color: var(--muted); margin: 12px 0 6px; }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      font: inherit;
      background: #fff;
    }
    textarea { resize: vertical; min-height: 74px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      background: #fff;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: right;
      white-space: nowrap;
    }
    th:first-child, td:first-child { text-align: left; }
    th { color: var(--muted); font-weight: 700; background: var(--soft); }
    .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
    .module-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--soft);
      color: var(--brand);
      font-size: 12px;
      font-weight: 700;
      border: 1px solid transparent;
      cursor: pointer;
    }
    .pill.active {
      background: var(--brand);
      color: #fff;
      border-color: var(--brand);
    }
    .module-detail {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .mini-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
      min-height: 82px;
    }
    .mini-card span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .mini-card strong {
      display: block;
      font-size: 18px;
    }
    .hint { color: var(--muted); font-size: 13px; line-height: 1.7; }
    .charts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 14px;
    }
    canvas { width: 100%; height: 220px; background: #fff; border: 1px solid var(--line); border-radius: 8px; }
    .message { margin-top: 10px; font-size: 13px; color: var(--brand); min-height: 20px; }
    @media (max-width: 860px) {
      header { display: block; }
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .layout, .charts, .module-detail { grid-template-columns: 1fr; }
    }
    @media (max-width: 520px) {
      main { padding: 14px; }
      .grid, .row { grid-template-columns: 1fr; }
      th, td { padding: 8px 6px; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>石油企业经营实战模拟系统</h1>
      <div class="sub">采购、生产、销售、库存、资金与利润的一体化经营决策平台</div>
    </div>
    <div>
      <button class="secondary" onclick="loadState()">刷新</button>
      <button class="warn" onclick="resetData()">重置演示数据</button>
    </div>
  </header>
  <main>
    <section class="grid" id="kpis"></section>
    <section class="layout">
      <div class="panel">
        <h2>经营决策录入</h2>
        <form id="decisionForm">
          <div class="row">
            <div>
              <label>季度</label>
              <input name="quarter" id="quarter" readonly>
            </div>
            <div>
              <label>销售单价（元/吨）</label>
              <input name="selling_price" type="number" min="1000" step="10" value="4380">
            </div>
          </div>
          <label>原油采购量（吨）</label>
          <input name="crude_purchase" type="number" min="0" step="100" value="8000">
          <label>计划加工量（吨）</label>
          <input name="production" type="number" min="0" step="100" value="7600">
          <label>成品率（%）</label>
          <input name="yield_rate" type="number" min="50" max="99" step="0.5" value="88">
          <div class="row">
            <div>
              <label>市场推广费（元）</label>
              <input name="marketing_budget" type="number" min="0" step="1000" value="180000">
            </div>
            <div>
              <label>管理费用（元）</label>
              <input name="admin_cost" type="number" min="0" step="1000" value="120000">
            </div>
          </div>
          <label>决策说明</label>
          <textarea name="notes" placeholder="例如：稳定产量、控制采购、提高销售价格。"></textarea>
          <div style="margin-top:14px">
            <button type="submit">提交并模拟</button>
          </div>
          <div class="message" id="message"></div>
        </form>
        <p class="hint">系统根据采购价格、产能、成品率、库存、需求函数和费用自动计算季度结果。连续提交可形成多期经营报表。</p>
      </div>
      <div class="panel">
        <h2>经营记录</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>季度</th><th>采购</th><th>加工</th><th>销量</th><th>收入</th><th>成本</th><th>利润</th><th>现金</th>
              </tr>
            </thead>
            <tbody id="history"></tbody>
          </table>
        </div>
        <div class="charts">
          <canvas id="profitChart" width="520" height="220"></canvas>
          <canvas id="inventoryChart" width="520" height="220"></canvas>
        </div>
      </div>
    </section>
    <section class="panel" style="margin-top:16px">
      <h2>业务模块</h2>
      <div class="module-tabs" id="moduleTabs">
        <button class="pill active" type="button" data-module="purchase">原油采购管理</button>
        <button class="pill" type="button" data-module="production">炼化生产计划</button>
        <button class="pill" type="button" data-module="sales">成品油销售管理</button>
        <button class="pill" type="button" data-module="inventory">库存管理</button>
        <button class="pill" type="button" data-module="finance">财务核算</button>
        <button class="pill" type="button" data-module="report">经营分析报表</button>
      </div>
      <div id="moduleContent"></div>
      <p class="hint" id="analysis"></p>
    </section>
  </main>
  <script>
    const fmt = new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 0 });
    const money = v => "¥" + fmt.format(v);
    let currentState = null;
    let activeModule = "purchase";

    async function api(path, options = {}) {
      const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "请求失败");
      return data;
    }

    function drawLine(canvas, rows, field, color, title) {
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#1f2933";
      ctx.font = "15px Microsoft YaHei";
      ctx.fillText(title, 16, 24);
      if (!rows.length) {
        ctx.fillStyle = "#65717f";
        ctx.fillText("暂无数据", 16, 58);
        return;
      }
      const values = rows.map(r => Number(r[field]));
      const min = Math.min(...values, 0);
      const max = Math.max(...values, 1);
      const pad = 34;
      const w = canvas.width - pad * 2;
      const h = canvas.height - pad * 2 - 10;
      ctx.strokeStyle = "#d9ded6";
      ctx.beginPath();
      ctx.moveTo(pad, canvas.height - pad);
      ctx.lineTo(canvas.width - pad, canvas.height - pad);
      ctx.stroke();
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      values.forEach((v, i) => {
        const x = pad + (rows.length === 1 ? w / 2 : i * w / (rows.length - 1));
        const y = canvas.height - pad - ((v - min) / (max - min || 1)) * h;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      });
      ctx.stroke();
      values.forEach((v, i) => {
        const x = pad + (rows.length === 1 ? w / 2 : i * w / (rows.length - 1));
        const y = canvas.height - pad - ((v - min) / (max - min || 1)) * h;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    function lastRow(state) {
      return state.history.length ? state.history[state.history.length - 1] : null;
    }

    function moduleHtml(state) {
      const s = state.summary;
      const last = lastRow(state);
      const crudePrice = last ? last.crude_price : 3000;
      const lastSales = last ? last.sales_volume : 0;
      const lastProduction = last ? last.actual_production : 0;
      const lastRevenue = last ? last.revenue : 0;
      const lastCost = last ? last.total_cost : 0;
      const modules = {
        purchase: {
          title: "原油采购管理",
          text: "录入采购量后，系统按季度市场价格计算采购成本，并把采购量并入原油库存。",
          cards: [
            ["当前原油库存", `${fmt.format(s.crude_inventory)} 吨`],
            ["参考采购价格", `${money(crudePrice)} / 吨`],
            ["建议操作", s.crude_inventory < 1000 ? "下期增加采购" : "保持采购节奏"]
          ]
        },
        production: {
          title: "炼化生产计划",
          text: "系统根据计划加工量、原油库存和单期产能自动确定实际加工量，再按设定的成品率生成成品油。",
          cards: [
            ["单期最大产能", "8,500 吨"],
            ["最近实际加工", `${fmt.format(lastProduction)} 吨`],
            ["本期成品率", `${last ? last.yield_rate : 88}%`]
          ]
        },
        sales: {
          title: "成品油销售管理",
          text: "系统根据销售单价、推广费用和季节因素预测市场需求，实际销量不会超过可销售库存。",
          cards: [
            ["当前成品油库存", `${fmt.format(s.product_inventory)} 吨`],
            ["最近销售量", `${fmt.format(lastSales)} 吨`],
            ["销售收入", money(lastRevenue)]
          ]
        },
        inventory: {
          title: "库存管理",
          text: "库存模块自动维护原油与成品油期末库存，并把库存水平反映到经营建议中。",
          cards: [
            ["原油库存", `${fmt.format(s.crude_inventory)} 吨`],
            ["成品油库存", `${fmt.format(s.product_inventory)} 吨`],
            ["库存状态", s.product_inventory > 4000 ? "成品油偏高" : "库存正常"]
          ]
        },
        finance: {
          title: "财务核算",
          text: "财务模块汇总销售收入、采购成本、加工成本、仓储成本、营销费用和管理费用，计算利润与现金。",
          cards: [
            ["当前现金", money(s.cash)],
            ["累计利润", money(s.total_profit)],
            ["最近总成本", money(lastCost)]
          ]
        },
        report: {
          title: "经营分析报表",
          text: "报表模块展示经营记录、利润趋势、库存趋势和自动经营建议，可用于课堂演示和小组汇报。",
          cards: [
            ["已模拟季度", `${state.history.length} 期`],
            ["最近季度", last ? last.quarter : "暂无"],
            ["分析建议", state.analysis]
          ]
        }
      };
      const item = modules[activeModule];
      return `
        <h3 style="margin:0 0 8px;font-size:16px">${item.title}</h3>
        <p class="hint" style="margin:0">${item.text}</p>
        <div class="module-detail">
          ${item.cards.map(card => `<div class="mini-card"><span>${card[0]}</span><strong>${card[1]}</strong></div>`).join("")}
        </div>
      `;
    }

    function renderModule() {
      if (!currentState) return;
      document.querySelectorAll("#moduleTabs .pill").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.module === activeModule);
      });
      document.getElementById("moduleContent").innerHTML = moduleHtml(currentState);
    }

    function render(state) {
      currentState = state;
      const s = state.summary;
      document.getElementById("quarter").value = state.next_quarter;
      document.getElementById("kpis").innerHTML = `
        <div class="kpi"><span>当前现金</span><strong>${money(s.cash)}</strong></div>
        <div class="kpi"><span>累计利润</span><strong>${money(s.total_profit)}</strong></div>
        <div class="kpi"><span>原油库存</span><strong>${fmt.format(s.crude_inventory)} 吨</strong></div>
        <div class="kpi"><span>成品油库存</span><strong>${fmt.format(s.product_inventory)} 吨</strong></div>
      `;
      document.getElementById("history").innerHTML = state.history.map(r => `
        <tr>
          <td>${r.quarter}</td>
          <td>${fmt.format(r.crude_purchase)}</td>
          <td>${fmt.format(r.actual_production)}</td>
          <td>${fmt.format(r.sales_volume)}</td>
          <td>${money(r.revenue)}</td>
          <td>${money(r.total_cost)}</td>
          <td style="color:${r.profit >= 0 ? "var(--good)" : "var(--bad)"}">${money(r.profit)}</td>
          <td>${money(r.cash_end)}</td>
        </tr>
      `).join("");
      drawLine(document.getElementById("profitChart"), state.history, "profit", "#126b5c", "季度利润趋势");
      drawLine(document.getElementById("inventoryChart"), state.history, "product_inventory_end", "#b54b31", "成品油库存趋势");
      document.getElementById("analysis").textContent = state.analysis;
      renderModule();
    }

    async function loadState() {
      render(await api("/api/state"));
    }

    async function resetData() {
      if (!confirm("确认重置所有经营记录？")) return;
      await api("/api/reset", { method: "POST", body: "{}" });
      await loadState();
      document.getElementById("message").textContent = "演示数据已重置。";
    }

    document.getElementById("decisionForm").addEventListener("submit", async e => {
      e.preventDefault();
      const form = new FormData(e.target);
      const payload = Object.fromEntries(form.entries());
      for (const key of ["crude_purchase", "production", "selling_price", "marketing_budget", "admin_cost", "yield_rate"]) {
        payload[key] = Number(payload[key]);
      }
      const result = await api("/api/decision", { method: "POST", body: JSON.stringify(payload) });
      document.getElementById("message").textContent = result.message;
      await loadState();
    });

    document.getElementById("moduleTabs").addEventListener("click", e => {
      const btn = e.target.closest("[data-module]");
      if (!btn) return;
      activeModule = btn.dataset.module;
      renderModule();
    });

    loadState();
  </script>
</body>
</html>
"""


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quarter TEXT NOT NULL UNIQUE,
                crude_purchase REAL NOT NULL,
                production REAL NOT NULL,
                selling_price REAL NOT NULL,
                marketing_budget REAL NOT NULL,
                admin_cost REAL NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quarter TEXT NOT NULL UNIQUE,
                crude_price REAL NOT NULL,
                crude_purchase REAL NOT NULL,
                actual_production REAL NOT NULL,
                sales_volume REAL NOT NULL,
                revenue REAL NOT NULL,
                purchase_cost REAL NOT NULL,
                production_cost REAL NOT NULL,
                storage_cost REAL NOT NULL,
                marketing_budget REAL NOT NULL,
                admin_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                profit REAL NOT NULL,
                cash_end REAL NOT NULL,
                crude_inventory_end REAL NOT NULL,
                product_inventory_end REAL NOT NULL,
                yield_rate REAL NOT NULL DEFAULT 88.0,
                created_at TEXT NOT NULL
            );
            """
        )
        # 兼容旧库结构：为已存在的表补齐 yield_rate 列
        for col_sql in [
            "ALTER TABLE decisions ADD COLUMN yield_rate REAL NOT NULL DEFAULT 88.0",
            "ALTER TABLE results ADD COLUMN yield_rate REAL NOT NULL DEFAULT 88.0",
        ]:
            try:
                conn.execute(col_sql)
            except sqlite3.OperationalError:
                pass


def reset_db():
    init_db()
    with connect() as conn:
        conn.execute("DELETE FROM decisions")
        conn.execute("DELETE FROM results")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('decisions', 'results')")


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_history(conn):
    return rows_to_dicts(conn.execute("SELECT * FROM results ORDER BY id").fetchall())


def latest_summary(history):
    if not history:
        return {
            "cash": 5_000_000,
            "crude_inventory": 2_000,
            "product_inventory": 1_000,
            "total_profit": 0,
        }
    last = history[-1]
    return {
        "cash": last["cash_end"],
        "crude_inventory": last["crude_inventory_end"],
        "product_inventory": last["product_inventory_end"],
        "total_profit": sum(row["profit"] for row in history),
    }


def next_quarter(history):
    start_year = 2026
    idx = len(history)  # 已完成的季度数，0-based
    year = start_year + idx // 4
    quarter = idx % 4 + 1
    return f"{year}Q{quarter}"


def market_crude_price(period_index):
    """返回在合理区间内波动的原油市场价（单位：元/吨）"""
    base = 3000
    long_cycle = 400 * math.sin(period_index * math.pi / 6)
    seasonal = 150 * math.sin(period_index * 1.3)
    return round(base + long_cycle + seasonal, 2)


def simulate_decision(data, history):
    required = ["quarter", "crude_purchase", "production", "selling_price", "marketing_budget", "admin_cost", "yield_rate"]
    for key in required:
        if key not in data:
            raise ValueError(f"缺少字段：{key}")
    for key in required[1:]:
        if float(data[key]) < 0:
            raise ValueError(f"{key} 不能为负数")

    summary = latest_summary(history)
    period_index = len(history) + 1
    crude_price = market_crude_price(period_index)
    capacity = 8_500
    yield_rate = float(data["yield_rate"]) / 100.0  # 百分比转小数
    unit_process_cost = 430
    product_storage_cost = 35
    crude_purchase = float(data["crude_purchase"])
    planned_production = float(data["production"])
    selling_price = float(data["selling_price"])
    marketing_budget = float(data["marketing_budget"])
    admin_cost = float(data["admin_cost"])

    available_crude = summary["crude_inventory"] + crude_purchase
    actual_production = min(planned_production, available_crude, capacity)
    product_output = actual_production * yield_rate
    crude_inventory_end = available_crude - actual_production
    available_product = summary["product_inventory"] + product_output

    seasonal = 850 * math.sin(period_index * math.pi / 2)
    market_demand = max(0, 13_000 - selling_price * 1.65 + marketing_budget / 280 + seasonal)
    sales_volume = min(available_product, market_demand)
    product_inventory_end = available_product - sales_volume

    revenue = sales_volume * selling_price
    purchase_cost = crude_purchase * crude_price
    production_cost = actual_production * unit_process_cost
    storage_cost = product_inventory_end * product_storage_cost + crude_inventory_end * 12
    total_cost = purchase_cost + production_cost + storage_cost + marketing_budget + admin_cost
    profit = revenue - total_cost
    cash_end = summary["cash"] + profit

    return {
        "quarter": str(data["quarter"]),
        "crude_price": round(crude_price, 2),
        "crude_purchase": round(crude_purchase, 2),
        "actual_production": round(actual_production, 2),
        "sales_volume": round(sales_volume, 2),
        "revenue": round(revenue, 2),
        "purchase_cost": round(purchase_cost, 2),
        "production_cost": round(production_cost, 2),
        "storage_cost": round(storage_cost, 2),
        "marketing_budget": round(marketing_budget, 2),
        "admin_cost": round(admin_cost, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "cash_end": round(cash_end, 2),
        "crude_inventory_end": round(crude_inventory_end, 2),
        "product_inventory_end": round(product_inventory_end, 2),
        "yield_rate": float(data["yield_rate"]),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_analysis(history, summary):
    if not history:
        return "尚未提交经营决策。建议先录入第一季度采购、生产、销售价格和费用预算，系统将自动生成经营结果。"
    last = history[-1]
    messages = []
    if last["profit"] < 0:
        messages.append("最近一期亏损，需检查采购量、售价与库存积压。")
    else:
        messages.append("最近一期盈利，经营方案具备延续基础。")
    if summary["product_inventory"] > 4000:
        messages.append("成品油库存偏高，可降低产量或加大推广。")
    if summary["crude_inventory"] < 800:
        messages.append("原油库存偏低，下期需关注采购保障。")
    if summary["cash"] < 1_000_000:
        messages.append("现金余额较低，应压缩费用并控制采购节奏。")
    if len(history) >= 2 and history[-1]["profit"] > history[-2]["profit"]:
        messages.append("利润较上一期改善，价格和产销策略效果较好。")
    return " ".join(messages)


def get_state():
    with connect() as conn:
        history = get_history(conn)
    summary = latest_summary(history)
    return {
        "next_quarter": next_quarter(history),
        "summary": summary,
        "history": history,
        "analysis": build_analysis(history, summary),
    }


def save_decision(data):
    with connect() as conn:
        history = get_history(conn)
        expected = next_quarter(history)
        if str(data.get("quarter")) != expected:
            raise ValueError(f"当前应录入 {expected}，请刷新页面后重试。")
        result = simulate_decision(data, history)
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """
            INSERT INTO decisions (
                quarter, crude_purchase, production, selling_price,
                marketing_budget, admin_cost, yield_rate, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["quarter"],
                data["crude_purchase"],
                data["production"],
                data["selling_price"],
                data["marketing_budget"],
                data["admin_cost"],
                data["yield_rate"],
                data.get("notes", ""),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO results (
                quarter, crude_price, crude_purchase, actual_production,
                sales_volume, revenue, purchase_cost, production_cost,
                storage_cost, marketing_budget, admin_cost, total_cost,
                profit, cash_end, crude_inventory_end, product_inventory_end,
                yield_rate, created_at
            ) VALUES (
                :quarter, :crude_price, :crude_purchase, :actual_production,
                :sales_volume, :revenue, :purchase_cost, :production_cost,
                :storage_cost, :marketing_budget, :admin_cost, :total_cost,
                :profit, :cash_end, :crude_inventory_end, :product_inventory_end,
                :yield_rate, :created_at
            )
            """,
            result,
        )
    return result


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/state":
            self.send_json(get_state())
        else:
            self.send_json({"error": "接口不存在"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/decision":
                data = self.read_json()
                result = save_decision(data)
                self.send_json({"message": f"{result['quarter']} 模拟完成，利润 {result['profit']:.0f} 元。", "result": result})
            elif path == "/api/reset":
                reset_db()
                self.send_json({"message": "数据已重置"})
            else:
                self.send_json({"error": "接口不存在"}, 404)
        except (ValueError, json.JSONDecodeError, sqlite3.IntegrityError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": f"服务器错误：{exc}"}, 500)


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"石油企业经营实战模拟系统已启动：http://{HOST}:{PORT}")
    print("按 Ctrl+C 停止服务。")
    server.serve_forever()


if __name__ == "__main__":
    main()
