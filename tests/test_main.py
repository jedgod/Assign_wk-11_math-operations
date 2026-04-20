from pathlib import Path

import pytest

import main


def test_load_config_reads_yaml(tmp_path, monkeypatch):
    config = """numbers:\n  a: 2\n  b: 3\npolynomial:\n  coefficients: [1, 0, 1]\n  x_value: 2\n"""
    Path(tmp_path / "config.yml").write_text(config, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    loaded = main.load_config()

    assert loaded["numbers"]["a"] == 2
    assert loaded["numbers"]["b"] == 3
    assert loaded["polynomial"]["coefficients"] == [1, 0, 1]
    assert loaded["polynomial"]["x_value"] == 2


def test_load_config_exits_on_invalid_yaml(tmp_path, monkeypatch, capsys):
    Path(tmp_path / "config.yml").write_text("numbers: [1, 2", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        main.load_config()

    output = capsys.readouterr().out
    assert "Config error:" in output


def test_main_uses_defaults_with_empty_config(tmp_path, monkeypatch, capsys):
    Path(tmp_path / "config.yml").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    main.main()

    output = capsys.readouterr().out
    assert "Addition:" in output
    assert "Subtraction:" in output
    assert "Multiplication:" in output
    assert "Polynomial:" in output
    assert "= 0" in output
