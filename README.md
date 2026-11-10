# CSV 表格整理

提供 CSV 单表整理代处理服务，也可以免费下载代码自行运行。

[English service details](#csv-cleanup-service-in-english) · [English enquiry form](https://github.com/yangbeixiao/csv-cleanup-service/issues/new?template=enquiry-en.yml)

## 服务范围与试报价

**19.9 元/单**，限一份 CSV、表头外不超过 1,000 条记录、不超过 20 列。报价为试报价，接单前确认范围、交付时间和交易方式。付费内容是按约定规则代处理及核对交付，代码自行运行免费。

可选择的操作：

- 删除单元格首尾空白。
- 删除空记录。
- 按明确指定的一列或多列组合去重，保留第一条；去重键任一部分为空的记录继续保留。

交付整理后的 `cleaned.csv` 和含处理规则、行数核对、删除记录原值的 `report.json`。工具不转换数字或日期，不处理 Excel 工作簿、公式计算、多表合并或业务含义判断。

## 询单

[填写公开询单表](https://github.com/yangbeixiao/csv-cleanup-service/issues/new?template=enquiry.yml)，只填写文字规则与完全虚构的示例。

**Issue 对所有人公开。请勿上传真实客户文件、姓名、电话、证件、账号、订单等敏感内容。** 示例须为 100% 人工编造的数据，不能用简单遮挡的真实数据代替。服务能否接受、真实文件如何安全交接，须在接单前另行确认；未约定安全交接方式时不要发送真实文件。

目前尚未配置收款。询单不需要付款，也不代表已经接单。只有范围、交付时间和交易方式全部确认后才接单。不承诺持续在线。

## 免费自行运行

需要 Python 3.10 或更新版本，运行工具无需第三方依赖。在仓库目录执行：

```bash
python3 clean_csv.py input.csv --output delivery
```

默认保留全部记录与字段值。按已确定的规则处理时，显式添加选项：

```bash
python3 clean_csv.py input.csv --output delivery --trim --drop-empty --dedupe 编号
python3 clean_csv.py input.csv --output delivery2 --dedupe 编号 批次
```

输入默认为 UTF-8，支持 UTF-8 BOM；其他支持的输入编码可用 `--encoding gb18030` 指定。分号分隔文件可用 `--delimiter ';'`。输出为带 BOM 的 UTF-8、逗号分隔 CSV。

输出目录必须尚不存在。程序拒绝空白或重复表头、缺失的去重列及列数不匹配的非空记录，输入校验失败不会生成交付目录。每条空记录或重复记录的删除均保留在 JSON 报告中；报告同样可能包含原始敏感数据，应与结果文件一并妥善保存。

## 使用限制

工具保留文本编号的前导零，但 Excel 等软件直接打开 CSV 时可能自行转换类型。请通过“从文本/CSV 导入”并将编号等相关列设为文本。以 `=` 等字符开头的值也会原样保留，应按文本导入，避免被表格软件解释为公式。

工具在内存中处理整个文件，服务只接受上述小文件范围。输入文件不会被覆盖；写盘中断可能留下不完整的输出目录，该目录不得作为交付结果，请排除磁盘或权限问题后换一个新目录重跑。

## 测试

测试使用 pytest，仅测试时需要安装：

```bash
python3 -m pip install pytest
python3 -m pytest -q
```

测试覆盖原值与前导零保留、明确规则去重、缺失键保留、行数核对、异常输入拒绝、已有输出保护和编码处理。

## CSV cleanup service in English

**USD 5 trial quote** for assisted cleanup of one CSV file with up to 1,000 data records, excluding the header, and up to 20 columns. The source code is free to download and run. The paid service covers processing a file to agreed rules and checking the delivery.

Supported operations are trimming leading and trailing whitespace, removing empty records, and deduplicating on explicitly specified columns. Deduplication keeps the first record; records with any missing key component are retained. Delivery includes `cleaned.csv` and `report.json`, with the applied rules, record counts, and original values of removed records. This service does not cover Excel workbooks, formula calculation, date or number conversion, merging files, or deciding business rules.

[Submit an English enquiry](https://github.com/yangbeixiao/csv-cleanup-service/issues/new?template=enquiry-en.yml) using written requirements and **100% synthetic examples only**. Issues and replies are public. Do not upload customer files, real records, personal information, credentials, or payment information, including partially masked real data. A safe file handoff must be agreed before any real file is sent.

Payment is not configured. An enquiry requires no payment and does not constitute an accepted order. Scope, delivery time, and a payment method must be agreed before work is accepted. Availability is not continuous, and no income or sales outcome is promised.

To run the tool yourself, use Python 3.10 or later. There are no third-party runtime dependencies:

```bash
python3 clean_csv.py input.csv --output delivery
python3 clean_csv.py input.csv --output delivery2 --trim --drop-empty --dedupe id batch
```

The output directory must be new. Defaults preserve all records and field values. To retain leading zeros and avoid interpreting formula-like text, import the CSV into your spreadsheet application with the relevant columns set to text. The tool processes the file in memory. A disk write failure can leave an incomplete output directory; do not deliver it, and retry with a new directory after resolving the failure. The JSON report can contain original data and needs the same protection as the CSV.

For tests, install pytest in your Python environment and run:

```bash
python3 -m pip install pytest
python3 -m pytest -q
```
