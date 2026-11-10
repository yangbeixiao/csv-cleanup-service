import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "clean_csv.py"


def run_job(tmp_path, contents, *options, encoding="utf-8-sig"):
    source = tmp_path / "input.csv"
    source.write_text(contents, encoding=encoding)
    output = tmp_path / "delivery"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), "--output", str(output), *options],
        capture_output=True,
        text=True,
    )
    return result, source, output


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def test_default_preserves_data_and_source(tmp_path):
    original = '编号,备注\n001,"  原样,保留  "\n001,重复编号\n'
    result, source, output = run_job(tmp_path, original)
    assert result.returncode == 0, result.stderr
    assert source.read_text(encoding="utf-8-sig") == original
    assert read_rows(output / "cleaned.csv")[1:] == [
        ["001", "  原样,保留  "], ["001", "重复编号"]
    ]


def test_trim_deduplicate_and_reconcile(tmp_path):
    result, _, output = run_job(
        tmp_path,
        "编号,名称\n001, 苹果 \n001,苹果\n001,梨\n002,桃\n\n,\n",
        "--trim", "--dedupe", "编号", "--drop-empty",
    )
    assert result.returncode == 0, result.stderr
    assert read_rows(output / "cleaned.csv") == [
        ["编号", "名称"], ["001", "苹果"], ["002", "桃"]
    ]
    report = json.loads((output / "report.json").read_text())
    assert report["input_rows"] == 6
    assert report["output_rows"] == 2
    assert report["duplicate_rows"] == 2
    assert report["empty_rows_removed"] == 2
    assert report["changed_cells"] == 1
    assert report["conflicting_duplicates"] == 1
    assert len(report["removed_rows"]) == 4
    assert report["removed_rows"][1]["values"] == ["001", "梨"]


def test_missing_keys_are_retained(tmp_path):
    result, _, output = run_job(
        tmp_path, "编号,名称\n,苹果\n,梨\n", "--dedupe", "编号"
    )
    assert result.returncode == 0, result.stderr
    assert len(read_rows(output / "cleaned.csv")) == 3
    report = json.loads((output / "report.json").read_text())
    assert report["missing_key_rows"] == 2


@pytest.mark.parametrize("contents,options", [
    ("", []),
    ("编号,编号\n1,2\n", []),
    ("编号,\n1,2\n", []),
    ("编号,名称\n1,2,3\n", []),
    ("编号,名称\n1\n", []),
    ('编号,名称\n1,"未闭合\n', []),
    ("编号,名称\n1,苹果\n", ["--dedupe", "不存在"]),
])
def test_invalid_input_produces_no_delivery(tmp_path, contents, options):
    result, _, output = run_job(tmp_path, contents, *options)
    assert result.returncode != 0
    assert not output.exists()
    assert "错误" in result.stderr


def test_existing_delivery_is_not_overwritten(tmp_path):
    output = tmp_path / "delivery"
    output.mkdir()
    existing = output / "cleaned.csv"
    existing.write_text("original")
    result, _, _ = run_job(tmp_path, "编号\n001\n")
    assert result.returncode != 0
    assert existing.read_text() == "original"


def test_gb18030_is_explicitly_supported(tmp_path):
    result, _, output = run_job(
        tmp_path, "编号,名称\n001,苹果\n",
        "--encoding", "gb18030", encoding="gb18030",
    )
    assert result.returncode == 0, result.stderr
    assert read_rows(output / "cleaned.csv")[1] == ["001", "苹果"]


def test_multiline_and_semicolon_input(tmp_path):
    result, _, output = run_job(
        tmp_path, '编号;备注\n001;"第一行\n第二行"\n', "--delimiter", ";"
    )
    assert result.returncode == 0, result.stderr
    assert read_rows(output / "cleaned.csv")[1] == ["001", "第一行\n第二行"]


def test_composite_key(tmp_path):
    result, _, output = run_job(
        tmp_path, "编号,批次\n001,A\n001,B\n001,A\n",
        "--dedupe", "编号", "批次",
    )
    assert result.returncode == 0, result.stderr
    assert len(read_rows(output / "cleaned.csv")) == 3
