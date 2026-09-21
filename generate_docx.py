import zipfile
import os
import datetime

BASE = r'D:\claude工作站\石油企业经营实战模拟系统'
OUTPUT = os.path.join(BASE, 'docs', '石化产业链运营实战模拟系统设计报告.docx')

# ── XML namespaces ──
CT  = 'http://schemas.openxmlformats.org/package/2006/content-types'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
WP  = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R   = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

FONT = 'Microsoft YaHei'

def xml_decl():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'

def tag(ns, name):
    return f'{{{ns}}}{name}'

def el(name, text='', attrs=None, children=''):
    """Build an XML element string under WP namespace."""
    a = ''
    if attrs:
        parts = []
        for k, v in attrs.items():
            parts.append(f'{k}="{v}"')
        a = ' ' + ' '.join(parts)
    t = tag(WP, name)
    return f'<{t}{a}>{children}{text}</{t}>'

# ── Paragraph helpers ──
def run(text, bold=False, size=22, color=None):
    """Create a w:r element with formatting."""
    rpr = ''
    if bold:
        rpr += el('b')
    rpr += el('sz', str(size))
    rpr += el('szCs', str(size))
    if color:
        rpr += el('color', attrs={'w:val': color})
    rpr += el('rFonts', attrs={
        'w:ascii': FONT, 'w:hAnsi': FONT, 'w:eastAsia': FONT
    })
    return el('r', children=
        el('rPr', children=rpr) +
        el('t', text, attrs={'xml:space': 'preserve'})
    )

def paragraph(content, bold=False, size=22, align='left', space_after=120, space_before=0):
    """Create a paragraph with a single run, or accept raw inner XML as content."""
    if isinstance(content, str) and not content.startswith('<'):
        content = run(content, bold=bold, size=size)
    ppr = el('pPr', children=
        el('jc', attrs={'w:val': align}) +
        el('spacing', attrs={'w:after': str(space_after), 'w:before': str(space_before),
                             'w:line': '360', 'w:lineRule': 'auto'})
    )
    return el('p', children=ppr + content)

def heading(text, level=1):
    sizes = {1: 32, 2: 28, 3: 24}
    return paragraph(
        run(text, bold=True, size=sizes.get(level, 24)),
        align='left', space_before=200 if level == 1 else 160, space_after=100
    )

def empty_p():
    return paragraph('', space_after=60)

# ── Table helper ──
def make_table(headers, rows, col_widths=None):
    n = len(headers)
    if col_widths is None:
        col_widths = [9000 // n] * n

    # Table properties
    tbl_pr = el('tblPr', children=
        el('tblStyle', attrs={'w:val': 'TableGrid'}) +
        el('tblW', attrs={'w:w': '9000', 'w:type': 'dxa'})
    )
    tbl_grid = el('tblGrid', children=
        ''.join(el('gridCol', attrs={'w:w': str(w)}) for w in col_widths)
    )

    # Header row
    h_cells = ''
    for i, h in enumerate(headers):
        tc_pr = el('tcPr', children=
            el('tcW', attrs={'w:w': str(col_widths[i]), 'w:type': 'dxa'}) +
            el('shd', attrs={'w:fill': '126B5C', 'w:val': 'clear'})
        )
        p = paragraph(run(h, bold=True, size=20, color='FFFFFF'), align='center', space_after=40)
        h_cells += el('tc', children=tc_pr + p)
    header_row = el('tr', children=h_cells)

    # Data rows
    data_rows = ''
    for row in rows:
        d_cells = ''
        for i, c in enumerate(row):
            tc_pr = el('tcPr', children=
                el('tcW', attrs={'w:w': str(col_widths[i]), 'w:type': 'dxa'}) +
                el('tcBorders', children=
                    el('top', attrs={'w:val': 'single', 'w:sz': '4', 'w:color': 'D9DED6'}) +
                    el('bottom', attrs={'w:val': 'single', 'w:sz': '4', 'w:color': 'D9DED6'})
                )
            )
            p = paragraph(run(str(c), size=20), align='center', space_after=20)
            d_cells += el('tc', children=tc_pr + p)
        data_rows += el('tr', children=d_cells)

    return el('tbl', children=tbl_pr + tbl_grid + header_row + data_rows)

# ══════════════════════════════════════════════
# BUILD DOCUMENT BODY
# ══════════════════════════════════════════════
body = ''

# ── Title ──
body += paragraph(run('石化产业链运营实战模拟系统设计报告', bold=True, size=36),
                   align='center', space_after=60)
body += paragraph(run('——基于 Python 标准库的单文件 Web 应用', size=22),
                   align='center', space_after=300)

# ═══════════════ 一 ═══════════════
body += heading('一、设计思路', 1)

body += heading('1.1 项目背景', 2)
body += paragraph('本系统面向石化产业链运营实战模拟课程，构建涵盖"原油采购→炼化生产→成品油销售→库存管理→财务核算→经营分析"全链条的企业经营模拟平台。学生以管理者角色按季度录入经营决策，系统根据动态市场价格、产能约束、库存限制和需求函数自动计算经营结果，帮助理解产业链各环节联动关系及经营决策对利润、库存、现金流的影响。')

body += heading('1.2 设计原则', 2)
body += make_table(
    ['原则', '说明'],
    [
        ['零依赖部署', '仅使用 Python 标准库（http.server + sqlite3 + json），复制即运行'],
        ['单文件架构', 'HTML/CSS/JS、API、数据库、模拟算法集中在 app.py 一个文件中'],
        ['确定性模拟', '输入确定则输出确定，无随机因子，便于课堂对比分析'],
        ['响应式界面', 'CSS Grid 布局 + 媒体查询，适配桌面端和移动端'],
    ],
    col_widths=[2400, 6600]
)
body += empty_p()

body += heading('1.3 技术架构', 2)
body += paragraph('系统采用四层架构：浏览器端使用原生 JavaScript + Canvas API 实现页面渲染和趋势图绘制；服务端使用 http.server 的 ThreadingHTTPServer 提供 RESTful API；模拟引擎实现采购、生产、销售、库存、财务的完整计算链条；数据层使用 SQLite 文件数据库，包含 decisions（决策）和 results（结果）两张表。')

body += heading('1.4 核心算法', 2)
body += paragraph(run('市场价格函数', bold=True, size=22) + run('：P(t) = 2850 + 120×sin(t×1.3) + t×35，基础价2850元/吨，正弦波动振幅120元/吨，线性增长35元/吨/季度，模拟国际油价周期性变化与长期上涨趋势。', size=22))
body += empty_p()
body += paragraph(run('市场需求函数', bold=True, size=22) + run('：D = max(0, 13000 - 1.65×售价 + 推广费/280 + 850×sin(t×π/2))。售价每提高1元，需求减少1.65吨；每280元推广费带来1吨需求增量；季节振幅850吨，4季度一个周期。', size=22))
body += empty_p()
body += paragraph(run('生产约束链', bold=True, size=22) + run('：可用原油 = 期初库存 + 采购量 → 实际加工量 = min(计划量, 可用原油, 8500吨产能) → 成品油产出 = 加工量×88% → 可售库存 = 期初成品油 + 产出。', size=22))
body += empty_p()
body += paragraph(run('财务核算', bold=True, size=22) + run('：利润 = 销售收入 -（采购成本 + 生产成本 + 仓储成本 + 推广费 + 管理费）；期末现金 = 期初现金 + 本期利润。', size=22))

# ═══════════════ 二 ═══════════════
body += heading('二、系统功能模块图', 1)
body += paragraph('系统划分为六大功能模块，各模块通过数据库和 API 进行数据交换，形成"采购→生产→销售→库存→财务→分析"的完整业务闭环。')

body += heading('2.1 模块总览', 2)
body += make_table(
    ['模块名称', '核心功能', '输入', '输出'],
    [
        ['原油采购管理', '录入采购量，市场价格计算成本', '采购量（吨）', '采购成本、期末库存'],
        ['炼化生产计划', '产能约束 + 成品率换算', '计划加工量（吨）', '实际加工量、成品油产出'],
        ['成品油销售管理', '售价与推广费→需求预测', '单价、推广费', '市场需求、实际销量'],
        ['库存管理', '自动维护原油与成品油库存', '系统自动计算', '期末库存、预警提示'],
        ['财务核算', '收入汇总 + 五项成本归集', '系统自动计算', '利润、现金余额'],
        ['经营分析报表', 'KPI + 记录表 + 趋势图', '经营结果数据', '可视化分析报告'],
    ],
    col_widths=[2200, 2800, 2000, 2000]
)
body += empty_p()

body += heading('2.2 模块关系说明', 2)
body += paragraph('采购模块为生产模块提供原油库存；生产模块将原油转化为成品油，影响库存模块；销售模块从库存模块提取成品油进行销售；财务模块汇总所有模块的成本与收入数据；分析模块读取财务与库存数据进行可视化展示。各模块之间呈单向数据流，边界清晰，耦合度低。')

# ═══════════════ 三 ═══════════════
body += heading('三、系统流程图', 1)

body += heading('3.1 系统启动流程', 2)
body += paragraph('① 执行 python app.py → ② 初始化 SQLite 数据库，创建 decisions 和 results 表 → ③ 启动 HTTP 服务监听 127.0.0.1:8000 → ④ 浏览器访问首页，服务端返回内嵌 HTML 页面 → ⑤ 前端自动请求 GET /api/state 获取初始状态 → ⑥ 页面渲染 KPI 面板、决策表单、经营记录表和分析建议。')

body += heading('3.2 决策提交与模拟流程', 2)
body += paragraph('① 用户在表单填写季度决策（采购量、加工量、售价、推广费、管理费）→ ② 点击"提交并模拟"→ ③ 前端 POST /api/decision 发送 JSON → ④ 后端验证季度匹配 → ⑤ 调用 simulate_decision() 执行十步模拟：')
body += paragraph('(1) 获取原油市场价格 → (2) 计算可用原油 → (3) 产能约束确定实际加工量 → (4) 按88%成品率生成成品油 → (5) 需求函数预测市场销量 → (6) 库存约束确定实际销量 → (7) 更新期末原油与成品油库存 → (8) 汇总收入和五项成本，计算利润与现金 → (9) 保存决策到 decisions 表 → (10) 保存结果到 results 表。')
body += paragraph('⑥ 返回 JSON 结果给前端 → ⑦ 前端自动刷新 KPI、经营记录表、趋势图和分析建议。')

body += heading('3.3 数据重置流程', 2)
body += paragraph('用户点击"重置演示数据"→ 确认对话框 → POST /api/reset → 删除 decisions 和 results 表中全部记录并重置自增序列 → 前端刷新恢复初始状态（现金500万、原油2000吨、成品油1000吨）。')

# ═══════════════ 四 ═══════════════
body += heading('四、数据字典', 1)

body += heading('4.1 decisions 表（经营决策表）', 2)
body += make_table(
    ['字段名', '类型', '约束', '说明'],
    [
        ['id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT', '自增主键'],
        ['quarter', 'TEXT', 'NOT NULL, UNIQUE', '经营季度，如 2026Q1'],
        ['crude_purchase', 'REAL', 'NOT NULL', '原油采购量（吨）'],
        ['production', 'REAL', 'NOT NULL', '计划加工量（吨）'],
        ['selling_price', 'REAL', 'NOT NULL', '成品油销售单价（元/吨）'],
        ['marketing_budget', 'REAL', 'NOT NULL', '市场推广费用（元）'],
        ['admin_cost', 'REAL', 'NOT NULL', '管理费用（元）'],
        ['notes', 'TEXT', '可空', '决策说明备注'],
        ['created_at', 'TEXT', 'NOT NULL', '创建时间（ISO 8601）'],
    ],
    col_widths=[1800, 1200, 3000, 3000]
)
body += empty_p()

body += heading('4.2 results 表（经营结果表）', 2)
body += make_table(
    ['字段名', '类型', '说明'],
    [
        ['id', 'INTEGER', '自增主键'],
        ['quarter', 'TEXT', '经营季度'],
        ['crude_price', 'REAL', '当季原油价格（元/吨）'],
        ['crude_purchase', 'REAL', '实际采购量（吨）'],
        ['actual_production', 'REAL', '实际加工量（吨）'],
        ['sales_volume', 'REAL', '实际销售量（吨）'],
        ['revenue', 'REAL', '销售收入（元）'],
        ['purchase_cost', 'REAL', '采购成本（元）'],
        ['production_cost', 'REAL', '生产成本（元）'],
        ['storage_cost', 'REAL', '仓储成本（元）'],
        ['marketing_budget', 'REAL', '推广费（元）'],
        ['admin_cost', 'REAL', '管理费（元）'],
        ['total_cost', 'REAL', '总成本（元）'],
        ['profit', 'REAL', '本期利润（元）'],
        ['cash_end', 'REAL', '期末现金余额（元）'],
        ['crude_inventory_end', 'REAL', '期末原油库存（吨）'],
        ['product_inventory_end', 'REAL', '期末成品油库存（吨）'],
        ['created_at', 'TEXT', '生成时间（ISO 8601）'],
    ],
    col_widths=[2600, 1200, 5200]
)
body += empty_p()

body += heading('4.3 系统初始参数', 2)
body += make_table(
    ['参数', '默认值', '说明'],
    [
        ['初始现金', '5,000,000 元', '经营起始资金'],
        ['初始原油库存', '2,000 吨', '期初原油储备'],
        ['初始成品油库存', '1,000 吨', '期初成品油储备'],
        ['单期最大产能', '8,500 吨', '每季度加工上限'],
        ['成品率', '88%', '原油→成品油转化率'],
        ['单位加工成本', '430 元/吨', '每吨原油加工费用'],
        ['成品油仓储费', '35 元/吨', '每吨成品油季度仓储费'],
        ['原油仓储费', '12 元/吨', '每吨原油季度仓储费'],
        ['原油基础价格', '2,850 元/吨', '价格函数基准值'],
    ],
    col_widths=[2600, 2200, 4200]
)
body += empty_p()

body += heading('4.4 API 接口', 2)
body += make_table(
    ['接口', '方法', '说明'],
    [
        ['/', 'GET', '返回 HTML 页面'],
        ['/api/state', 'GET', '返回经营状态 JSON（含 KPI、历史记录、分析建议）'],
        ['/api/decision', 'POST', '提交季度决策 JSON，返回模拟结果'],
        ['/api/reset', 'POST', '清空 decisions 和 results 表，恢复初始状态'],
    ],
    col_widths=[2200, 1200, 5600]
)

# ═══════════════ 五 ═══════════════
body += heading('五、个人实践心得体会', 1)

body += heading('5.1 对石化产业链的认知提升', 2)
body += paragraph('通过开发本系统，我深刻理解了石化产业链各环节之间的紧密耦合关系。采购量过大会占用资金并增加仓储成本，采购量过小则导致停工待料；产能刚性和成品率固定意味着生产计划必须在库存约束下制定；售价每提高1元，需求减少约1.65吨，价格弹性直接影响销售收入。初始现金500万元看似充足，若连续亏损，现金很快枯竭。这些变量之间的博弈让我体会到——企业经营本质上是在多重约束下寻找全局最优的过程，任何一个环节的失误都可能传导至整条经营链条。')

body += heading('5.2 技术实现方面的成长', 2)
body += paragraph(run('Python 标准库的深度应用：', bold=True) + run('完全依赖 http.server、sqlite3、json 等内置模块构建了完整的 Web 应用，认识到标准库完全可以支撑中等复杂度的系统开发。ThreadingHTTPServer 提供多线程并发能力，sqlite3.Row 提供便捷的字典式查询接口。', size=22))
body += empty_p()
body += paragraph(run('前后端一体化设计：', bold=True) + run('将 HTML/CSS/JS 以内嵌字符串形式放在 Python 文件中，实现了"单文件复制即运行"的极简部署体验。虽然不适合大型项目，但在课程展示和作业提交场景下极具优势。', size=22))
body += empty_p()
body += paragraph(run('Canvas 图表绘制：', bold=True) + run('使用原生 Canvas API 绘制利润和库存折线图，处理了单数据点居中、多数据点分布等边界情况，避免引入第三方图表库，保持了零依赖原则。', size=22))
body += empty_p()
body += paragraph(run('SQLite 的适用场景：', bold=True) + run('零配置、文件级数据库特性与"单文件运行"理念高度契合，连接即用，无需安装数据库服务。', size=22))

body += heading('5.3 遇到的困难与解决方案', 2)
body += make_table(
    ['困难', '解决方案'],
    [
        ['需求函数参数缺乏实际数据支撑', '调整参数使模拟结果落于合理区间，利用正弦函数模拟季节周期'],
        ['Canvas 仅1条记录时图表显示异常', '特殊处理单数据点情况，将其绘制在画布中央而非边缘'],
        ['前端表单数值类型为字符串', '使用 Number() 对六个数值字段做显式类型转换'],
        ['季度编号始终为2026Qx，无法跨年', '优化 next_quarter() 函数，增加年份进位逻辑'],
    ],
    col_widths=[3600, 5400]
)
body += empty_p()

body += heading('5.4 不足与改进方向', 2)
body += paragraph('(1) 当前仅有一个市场原油价格，未来可引入多供应商比价机制；(2) 需求函数为确定性公式，可增加随机扰动或场景模式（如政策利好、市场竞争加剧）；(3) 缺少用户系统，无法区分不同小组的经营数据；(4) 不支持报表导出 Excel/PDF 格式；(5) 趋势图交互性不足，不支持缩放和数据点详情。')

body += heading('5.5 课程启示与总结', 2)
body += paragraph('本次开发实践是一次将编程技能、系统设计方法和企业管理知识三者融合的综合性训练。从需求分析、系统设计、编码实现到测试验证的完整流程，让我对软件开发全生命周期有了更清晰的认识。系统虽小，但覆盖 Web 开发、数据库设计、数学建模、前端交互等多个技术维度，是一份很有价值的课程实践成果。')
body += empty_p()
body += paragraph(run('最大的体会：', bold=True) + run('技术选型应以业务需求为导向。本次"零依赖、单文件"的设计正是为满足课程"易部署、便展示、好提交"的实际需求。企业经营是系统工程，"局部最优不等于全局最优"——这一管理原理通过模拟系统得到了直观而生动的验证。', size=22))

# ══════════════════════════════════════════════
# ASSEMBLE DOCX
# ══════════════════════════════════════════════

doc_xml = f'''{xml_decl()}
<w:document xmlns:w="{WP}" xmlns:r="{R}">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>'''

# ── [Content_Types].xml ──
content_types = f'''{xml_decl()}
<Types xmlns="{CT}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

# ── _rels/.rels ──
rels_xml = f'''{xml_decl()}
<Relationships xmlns="{REL}">
  <Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/>
</Relationships>'''

# ── word/_rels/document.xml.rels ──
doc_rels = f'''{xml_decl()}
<Relationships xmlns="{REL}">
  <Relationship Id="rId1" Type="{R}/styles" Target="styles.xml"/>
</Relationships>'''

# ── word/styles.xml ──
styles_xml = f'''{xml_decl()}
<w:styles xmlns:w="{WP}">
  <w:style w:type="paragraph" w:styleId="1">
    <w:name w:val="heading 1"/>
    <w:pPr><w:spacing w:before="360" w:after="200"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="2">
    <w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="3">
    <w:name w:val="heading 3"/>
    <w:pPr><w:spacing w:before="200" w:after="80"/></w:pPr>
  </w:style>
</w:styles>'''

# ── Write ZIP ──
with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types.encode('utf-8'))
    z.writestr('_rels/.rels', rels_xml.encode('utf-8'))
    z.writestr('word/_rels/document.xml.rels', doc_rels.encode('utf-8'))
    z.writestr('word/document.xml', doc_xml.encode('utf-8'))
    z.writestr('word/styles.xml', styles_xml.encode('utf-8'))

print(f'Done: {OUTPUT}')
print(f'Size: {os.path.getsize(OUTPUT)} bytes')
