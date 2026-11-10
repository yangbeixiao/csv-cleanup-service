import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


class InputError(ValueError):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, "错误：命令参数无效，请使用 --help 查看用法。\n")


def prepare(args: argparse.Namespace) -> tuple[list[str], list[list[str]], dict[str, Any]]:
    if args.output.exists():
        raise InputError("输出目录已存在，请指定一个新目录。")
    if len(args.delimiter) != 1 or args.delimiter in '\r\n"':
        raise InputError("分隔符必须是一个有效字符。")

    cleaned: list[list[str]] = []
    seen: dict[tuple[str, ...], list[str]] = {}
    report: dict[str, Any] = {
        "input_rows": 0,
        "output_rows": 0,
        "duplicate_rows": 0,
        "empty_rows_removed": 0,
        "changed_cells": 0,
        "conflicting_duplicates": 0,
        "missing_key_rows": 0,
        "removed_rows": [],
        "rules": {
            "trim": args.trim,
            "drop_empty": args.drop_empty,
            "dedupe_columns": args.dedupe or [],
            "keep": "first",
            "encoding": args.encoding,
            "delimiter": args.delimiter,
        },
    }
    with args.source.open(encoding=args.encoding, newline="") as handle:
        reader = csv.reader(handle, delimiter=args.delimiter, strict=True)
        header = next(reader, [])
        if not header or any(not name.strip() for name in header):
            raise InputError("文件缺少有效表头，或表头含空列名。")
        if len(set(header)) != len(header):
            raise InputError("表头含重复列名。")
        if args.dedupe and any(name not in header for name in args.dedupe):
            raise InputError("去重列不存在，请核对表头。")
        key_indices = [header.index(name) for name in (args.dedupe or [])]

        for record, original in enumerate(reader, start=1):
            report["input_rows"] += 1
            if original and len(original) != len(header):
                raise InputError(f"第 {record} 条数据记录的列数与表头不一致。")
            row = [value.strip() for value in original] if args.trim else original[:]
            report["changed_cells"] += sum(a != b for a, b in zip(original, row))
            reason = ""
            if args.drop_empty and not any(row):
                report["empty_rows_removed"] += 1
                reason = "empty"
            elif key_indices:
                key = tuple(row[index] for index in key_indices) if row else ()
                if not key or any(not value for value in key):
                    report["missing_key_rows"] += 1
                elif key in seen:
                    report["duplicate_rows"] += 1
                    report["conflicting_duplicates"] += row != seen[key]
                    reason = "duplicate"
                else:
                    seen[key] = row
            if reason:
                report["removed_rows"].append({
                    "source_record": record,
                    "reason": reason,
                    "values": original,
                })
            else:
                cleaned.append(row)

    report["output_rows"] = len(cleaned)
    return header, cleaned, report


def main() -> int:
    parser = ArgumentParser(description="本地 CSV 整理：保留文本编号，按明确规则处理。")
    parser.add_argument("source", type=Path, help="输入 CSV 文件")
    parser.add_argument("--output", required=True, type=Path, help="尚不存在的输出目录")
    parser.add_argument("--encoding", choices=("utf-8-sig", "gb18030"), default="utf-8-sig")
    parser.add_argument("--delimiter", default=",", help="输入分隔符，默认逗号")
    parser.add_argument("--trim", action="store_true", help="删除单元格首尾空白")
    parser.add_argument("--drop-empty", action="store_true", help="删除空记录")
    parser.add_argument("--dedupe", nargs="+", help="按指定列组合去重，保留第一条")
    args = parser.parse_args()
    try:
        header, rows, report = prepare(args)
        args.output.mkdir(parents=True, exist_ok=False)
        with (args.output / "cleaned.csv").open("x", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)
        with (args.output / "report.json").open("x", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except InputError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except UnicodeError:
        print("错误：文件编码不匹配，请确认输入编码。", file=sys.stderr)
        return 1
    except csv.Error:
        print("错误：CSV 格式无效或字段过长，请检查文件。", file=sys.stderr)
        return 1
    except OSError:
        print("错误：文件读写失败，请检查路径、权限和剩余空间。", file=sys.stderr)
        return 1
    print(
        f"完成：输入 {report['input_rows']} 条，输出 {report['output_rows']} 条，"
        f"移除重复 {report['duplicate_rows']} 条，移除空记录 {report['empty_rows_removed']} 条。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
