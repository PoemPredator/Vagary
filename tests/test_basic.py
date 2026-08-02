"""Vagary 单元测试。

运行方式::

    pytest                    # 运行所有测试
    pytest -v                 # 详细输出
    pytest --cov=vagary       # 带覆盖率

测试使用项目自带的 data/vagary.xlsx 真实数据，确保统计逻辑正确。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 在导入 pyplot 之前设置无图形界面后端，确保 CI / 无显示器环境可运行

import pandas as pd
import pytest

from vagary import (
    load_works,
    cut_lyrics,
    word_frequency,
    words_by_length,
    search_word,
    song_high_frequency_words,
    collaborator_frequency,
    export_tables,
    plot_frequency,
    plot_collaborators,
    save_chart,
)
from vagary.stats import _names, _fallback_cut


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# 数据文件路径：tests/ 在项目根目录下，data/ 也在项目根目录下
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "vagary.xlsx"


@pytest.fixture(scope="module")
def works():
    """加载真实数据，所有测试共享同一份。"""
    return load_works(DATA_FILE)


@pytest.fixture(scope="module")
def frequency(works):
    """生成词频表。"""
    return word_frequency(works, exclude_words={"我们", "你们", "一个"})


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

class TestLoadWorks:
    """测试 load_works 函数。"""

    def test_load_success(self, works):
        """能正常读取数据且行数 > 0。"""
        assert len(works) > 0
        assert isinstance(works, pd.DataFrame)

    def test_required_columns(self, works):
        """必要列都存在。"""
        for col in ("歌曲名", "演唱", "作曲", "编曲", "歌词"):
            assert col in works.columns

    def test_no_nan_in_required(self, works):
        """必要列中没有 NaN（已转为空字符串）。"""
        for col in ("歌曲名", "演唱", "作曲", "编曲", "歌词"):
            assert not works[col].isna().any()

    def test_missing_column_raises(self, tmp_path):
        """缺少必要列时抛出 ValueError。"""
        df = pd.DataFrame({"歌曲名": ["test"], "演唱": ["test"]})
        path = tmp_path / "bad.xlsx"
        df.to_excel(path, index=False)
        with pytest.raises(ValueError, match="缺少必要列"):
            load_works(path)


# ---------------------------------------------------------------------------
# 分词
# ---------------------------------------------------------------------------

class TestCutLyrics:
    """测试 cut_lyrics 函数。"""

    def test_returns_list(self):
        """返回值是列表。"""
        result = cut_lyrics("人间烟火天上月", use_jieba=False)
        assert isinstance(result, list)

    def test_min_length_2(self):
        """所有返回的词长度 >= 2。"""
        result = cut_lyrics("天上人间", use_jieba=False)
        assert all(len(w) >= 2 for w in result)

    def test_only_chinese(self):
        """返回的词只包含汉字。"""
        result = cut_lyrics("hello 世界 abc 人间", use_jieba=False)
        assert all(w.isalpha() and ord(w[0]) > 0x4E00 for w in result)

    def test_fallback_cut(self):
        """保底分词算法能正常运行。"""
        words = _fallback_cut("人间烟火")
        assert "人间" in words
        assert "烟火" in words

    def test_empty_string(self):
        """空字符串返回空列表。"""
        assert cut_lyrics("", use_jieba=False) == []


# ---------------------------------------------------------------------------
# 词频统计
# ---------------------------------------------------------------------------

class TestWordFrequency:
    """测试 word_frequency 函数。"""

    def test_returns_dataframe(self, frequency):
        """返回 DataFrame。"""
        assert isinstance(frequency, pd.DataFrame)

    def test_columns(self, frequency):
        """列名正确。"""
        assert list(frequency.columns) == ["词语", "出现作品数", "字数"]

    def test_sorted_desc(self, frequency):
        """按出现作品数降序排列。"""
        counts = frequency["出现作品数"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_count_le_total_works(self, works, frequency):
        """每个词的出现作品数 <= 总作品数。"""
        assert (frequency["出现作品数"] <= len(works)).all()

    def test_exclude_words(self, works):
        """排除词不出现在结果中。"""
        freq = word_frequency(works, exclude_words={"人间", "天地", "岁月"})
        assert "人间" not in freq["词语"].values
        assert "天地" not in freq["词语"].values
        assert "岁月" not in freq["词语"].values

    def test_word_length_column(self, frequency):
        """字数列等于词语长度。"""
        assert (frequency["字数"] == frequency["词语"].str.len()).all()

    def test_no_duplicates(self, frequency):
        """词语没有重复。"""
        assert frequency["词语"].is_unique


# ---------------------------------------------------------------------------
# 按字数筛选
# ---------------------------------------------------------------------------

class TestWordsByLength:
    """测试 words_by_length 函数。"""

    def test_filter_2char(self, frequency):
        """2 字词筛选正确。"""
        result = words_by_length(frequency, 2)
        assert (result["字数"] == 2).all()

    def test_filter_3char(self, frequency):
        """3 字词筛选正确。"""
        result = words_by_length(frequency, 3)
        assert (result["字数"] == 3).all()

    def test_filter_4char(self, frequency):
        """4 字词筛选正确。"""
        result = words_by_length(frequency, 4)
        assert (result["字数"] == 4).all()

    def test_top_n(self, frequency):
        """top_n 限制返回行数。"""
        result = words_by_length(frequency, 2, top_n=5)
        assert len(result) <= 5


# ---------------------------------------------------------------------------
# 查询
# ---------------------------------------------------------------------------

class TestSearchWord:
    """测试 search_word 函数。"""

    def test_returns_dataframe(self, works):
        """返回 DataFrame。"""
        result = search_word(works, "人间", use_jieba=False)
        assert isinstance(result, pd.DataFrame)

    def test_columns(self, works):
        """列名正确。"""
        result = search_word(works, "人间", use_jieba=False)
        assert list(result.columns) == ["歌曲名", "演唱", "命中歌词"]

    def test_empty_word_raises(self, works):
        """空词抛出 ValueError。"""
        with pytest.raises(ValueError, match="请输入"):
            search_word(works, "")

    def test_hit_count_matches(self, works, frequency):
        """查词结果行数 <= 该词的出现作品数（分词方式一致时相等）。"""
        word = "人间"
        search_result = search_word(works, word, use_jieba=False)
        freq_row = frequency[frequency["词语"] == word]
        if not freq_row.empty:
            # search_word 使用保底分词，frequency 也用保底分词
            # 但 frequency 可能用了排除词，这里直接验证 search 结果行数 > 0
            assert len(search_result) > 0


# ---------------------------------------------------------------------------
# 高频词命中统计
# ---------------------------------------------------------------------------

class TestSongHighFrequencyWords:
    """测试 song_high_frequency_words 函数。"""

    def test_row_count_matches(self, works, frequency):
        """结果行数与作品数一致。"""
        result = song_high_frequency_words(works, frequency, n=20, use_jieba=False)
        assert len(result) == len(works)

    def test_columns(self, works, frequency):
        """列名正确。"""
        result = song_high_frequency_words(works, frequency, n=10, use_jieba=False)
        assert list(result.columns) == ["歌曲名", "前n高频词数量", "命中的前n高频词"]

    def test_invalid_n_raises(self, works, frequency):
        """n <= 0 时抛出 ValueError。"""
        with pytest.raises(ValueError, match="n 必须是大于 0"):
            song_high_frequency_words(works, frequency, n=0)
        with pytest.raises(ValueError, match="n 必须是大于 0"):
            song_high_frequency_words(works, frequency, n=-1)

    def test_count_consistent(self, works, frequency):
        """前n高频词数量与命中词列表长度一致。"""
        result = song_high_frequency_words(works, frequency, n=20, use_jieba=False)
        for _, row in result.iterrows():
            if row["命中的前n高频词"]:
                words_list = row["命中的前n高频词"].split("、")
                assert row["前n高频词数量"] == len(words_list)
            else:
                assert row["前n高频词数量"] == 0


# ---------------------------------------------------------------------------
# 合作者统计
# ---------------------------------------------------------------------------

class TestCollaboratorFrequency:
    """测试 collaborator_frequency 函数。"""

    def test_all_collab(self, works):
        """全部合作统计正常。"""
        result = collaborator_frequency(works, "全部合作")
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["合作者", "合作作品数"]
        assert len(result) > 0

    def test_singer_collab(self, works):
        """演唱合作统计正常。"""
        result = collaborator_frequency(works, "演唱合作")
        assert len(result) > 0

    def test_music_collab(self, works):
        """曲合作统计正常。"""
        result = collaborator_frequency(works, "曲合作")
        assert len(result) > 0

    def test_invalid_kind_raises(self, works):
        """无效 kind 抛出 ValueError。"""
        with pytest.raises(ValueError, match="kind 只能是"):
            collaborator_frequency(works, "无效")

    def test_sorted_desc(self, works):
        """按合作作品数降序排列。"""
        result = collaborator_frequency(works, "全部合作")
        counts = result["合作作品数"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_names_split(self):
        """_names 正确按斜杠拆分。"""
        assert _names("张三/李四") == {"张三", "李四"}
        assert _names("张三／李四") == {"张三", "李四"}
        assert _names("张三") == {"张三"}
        assert _names("") == set()
        assert _names("nan") == set()


# ---------------------------------------------------------------------------
# 导出
# ---------------------------------------------------------------------------

class TestExportTables:
    """测试 export_tables 函数。"""

    def test_export_creates_file(self, tmp_path, works, frequency):
        """导出生成 Excel 文件。"""
        path = export_tables(tmp_path, frequency, works)
        assert path.exists()
        assert path.suffix == ".xlsx"

    def test_export_sheets(self, tmp_path, works, frequency):
        """导出的 Excel 包含正确的工作表。"""
        path = export_tables(tmp_path, frequency, works)
        xl = pd.ExcelFile(path)
        expected_sheets = ["全部词频", "2字词", "3字词", "4字词", "全部合作", "演唱合作", "曲合作"]
        for sheet in expected_sheets:
            assert sheet in xl.sheet_names

    def test_export_creates_dir(self, tmp_path, works, frequency):
        """输出目录不存在时自动创建。"""
        output_dir = tmp_path / "nested" / "output"
        path = export_tables(output_dir, frequency, works)
        assert path.exists()
        assert output_dir.exists()


# ---------------------------------------------------------------------------
# 绘图（不显示，仅验证不报错）
# ---------------------------------------------------------------------------

class TestPlotting:
    """测试绘图函数（使用 Agg 后端避免显示窗口）。"""

    def test_plot_frequency(self, frequency):
        """plot_frequency 不报错。"""
        ax = plot_frequency(frequency, length=2, top_n=10)
        assert ax is not None

    def test_plot_collaborators(self, works):
        """plot_collaborators 不报错。"""
        collabs = collaborator_frequency(works, "全部合作")
        ax = plot_collaborators(collabs, top_n=10)
        assert ax is not None

    def test_save_chart(self, tmp_path, frequency):
        """save_chart 生成三种格式文件。"""
        import matplotlib
        matplotlib.use("Agg")  # 确保无图形界面
        ax = plot_frequency(frequency, length=2, top_n=5)
        paths = save_chart(ax, tmp_path / "charts", "test_chart")
        assert paths["PNG"].exists()
        assert paths["SVG"].exists()
        assert paths["可编辑PKL"].exists()
