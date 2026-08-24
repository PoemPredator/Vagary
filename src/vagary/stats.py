"""核心统计逻辑：数据加载、分词、词频统计、查询、合作者统计、导出。

所有公开函数均有中文说明，统计单位是"作品数"——同一词在同一首歌
重复出现只计一次。
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------------
# 常量与正则
# ---------------------------------------------------------------------------

# 只保留连续汉字；歌词中的英文、标点、括号声部标记不会进入词频。
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")
# 合作者字段约定只以半角或全角斜杠分隔；不可按"和"等汉字拆分，避免误伤人名。
SPLIT_RE = re.compile(r"[／/]+")


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

def load_works(file_path: str | Path = "vagary.xlsx", sheet_name: str | int = 0) -> pd.DataFrame:
    """读取 Excel，并检查本项目所需的 5 个主要字段。

    Parameters
    ----------
    file_path : str | Path
        Excel 文件路径，默认为当前目录下的 ``vagary.xlsx``。
    sheet_name : str | int
        工作表名称或序号，默认第一个工作表。

    Returns
    -------
    pandas.DataFrame
        已清洗的作品表，空歌词自动转为空字符串。

    Raises
    ------
    ValueError
        当 Excel 缺少必要列时抛出。
    """
    works = pd.read_excel(file_path, sheet_name=sheet_name)
    required = ["歌曲名", "演唱", "作曲", "编曲", "歌词"]
    missing = [col for col in required if col not in works.columns]
    if missing:
        raise ValueError(f"Excel 缺少必要列：{', '.join(missing)}")
    works = works.copy()
    for col in required:
        works[col] = works[col].fillna("").astype(str).str.strip()
    return works


# ---------------------------------------------------------------------------
# 分词
# ---------------------------------------------------------------------------

def _fallback_cut(text: str) -> list[str]:
    """未安装 jieba 时的可运行保底方案：提取连续汉字的 2-4 字滑动短语。"""
    words: list[str] = []
    for block in CHINESE_RE.findall(text):
        for length in range(2, 5):
            words.extend(block[i : i + length] for i in range(len(block) - length + 1))
    return words


def cut_lyrics(
    text: str,
    user_dict: str | Path | None = None,
    use_jieba: bool = True,
) -> list[str]:
    """把歌词分词并仅返回汉字数不少于 2 的词。

    使用 jieba 时会**同时**运行精确模式（细分，``cut_all=False``）与全模式
    （粗分，``cut_all=True``），两种结果取并集后去重。这样同一段文字的
    多种切分可能都会被纳入统计——例如"喜怒哀乐"可同时得到"喜怒""哀乐"
    "喜怒哀乐"等多种词，均计入词频。

    Parameters
    ----------
    text : str
        待分词的歌词文本。
    user_dict : str | Path | None
        个人词典路径（每行：词语、词频、词性，后两项可省略）。
    use_jieba : bool
        是否使用 jieba 分词。若安装了 jieba 默认使用（粗分+细分并集）；
        否则自动使用保底的 2-4 字短语法。

    Returns
    -------
    list[str]
        分词结果（已去重），仅包含长度 >= 2 的纯汉字词。
    """
    if use_jieba:
        try:
            import jieba  # 延迟导入，未安装时 Notebook 仍能运行
            if user_dict:
                dict_path = Path(user_dict)
                if not dict_path.exists():
                    raise FileNotFoundError(f"找不到个人词典：{dict_path}")
                jieba.load_userdict(str(dict_path))
            # 细分（精确模式）：按最合理切分出词；粗分（全模式）：穷举所有可成词片段。
            # 二者并集可覆盖"喜怒哀乐"同时拆成"喜怒""哀乐"等多种分词方式。
            fine = jieba.lcut(text, cut_all=False)
            coarse = jieba.lcut(text, cut_all=True)
            pieces = fine + coarse
        except ModuleNotFoundError:
            pieces = _fallback_cut(text)
    else:
        pieces = _fallback_cut(text)
    # 仅保留长度 >= 2 的纯汉字词；去重以体现"并集"语义（保留首次出现顺序）。
    seen: set[str] = set()
    result: list[str] = []
    for word in pieces:
        if len(word) >= 2 and re.fullmatch(r"[\u4e00-\u9fff]+", word) and word not in seen:
            seen.add(word)
            result.append(word)
    return result


# ---------------------------------------------------------------------------
# 词频统计
# ---------------------------------------------------------------------------

def word_frequency(
    works: pd.DataFrame,
    exclude_words: Iterable[str] = (),
    user_dict: str | Path | None = None,
    use_jieba: bool = True,
) -> pd.DataFrame:
    """按作品数统计词频，返回词语、出现作品数、字数三列。

    每首歌中重复出现的词只算一次；``exclude_words`` 中的词完全不计入。

    Parameters
    ----------
    works : pandas.DataFrame
        由 :func:`load_works` 返回的作品表。
    exclude_words : Iterable[str]
        排除词列表，其中的词不会进入统计。
    user_dict : str | Path | None
        个人词典路径，传给 :func:`cut_lyrics`。
    use_jieba : bool
        是否使用 jieba 分词。

    Returns
    -------
    pandas.DataFrame
        列：``词语``、``出现作品数``、``字数``，按出现作品数降序排列。
    """
    excluded = {str(word).strip() for word in exclude_words if str(word).strip()}
    counter: Counter[str] = Counter()
    for lyrics in works["歌词"]:
        song_words = set(cut_lyrics(lyrics, user_dict, use_jieba)) - excluded
        counter.update(song_words)
    result = pd.DataFrame(
        [{"词语": word, "出现作品数": count, "字数": len(word)} for word, count in counter.items()]
    )
    if result.empty:
        return pd.DataFrame(columns=["词语", "出现作品数", "字数"])
    return result.sort_values(["出现作品数", "字数", "词语"], ascending=[False, True, True]).reset_index(drop=True)


def words_by_length(frequency: pd.DataFrame, length: int, top_n: int | None = None) -> pd.DataFrame:
    """筛选指定字数（例如 2、3、4）的词频表。

    Parameters
    ----------
    frequency : pandas.DataFrame
        由 :func:`word_frequency` 生成的词频表。
    length : int
        要筛选的字数。
    top_n : int | None
        取前若干名，``None`` 表示全部返回。

    Returns
    -------
    pandas.DataFrame
        筛选后的词频表。
    """
    result = frequency[frequency["字数"] == length].copy()
    return result.head(top_n).reset_index(drop=True) if top_n else result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 查询
# ---------------------------------------------------------------------------

def search_word(
    works: pd.DataFrame,
    word: str,
    user_dict: str | Path | None = None,
    use_jieba: bool = True,
) -> pd.DataFrame:
    """按作品查询词语，直接在**原始歌词**中匹配，返回歌曲名、演唱和命中歌词。

    每首命中作品只返回一行；若一首歌有多行命中，这些歌词行会在"命中歌词"
    单元格中用换行合并。

    查询采用原始歌词的子串匹配，**不再依赖分词结果**：只要某首作品的歌词
    文本中包含该词语（作为连续子串）即视为命中，即使分词时该词未被切分为
    独立词元也会被检出。这样与 :func:`word_frequency` 的并集分词口径更一致——
    例如查询"喜怒"，凡歌词中出现"喜怒"二字（含"喜怒哀乐""喜怒无常"等）的作品
    都会返回。

    .. note::
        ``user_dict`` 与 ``use_jieba`` 参数仅为兼容旧调用而保留，当前查询
        不再经过分词，二者不会影响查询结果。

    Parameters
    ----------
    works : pandas.DataFrame
        作品表。
    word : str
        要查询的词语。
    user_dict : str | Path | None
        个人词典路径（兼容保留，不影响结果）。
    use_jieba : bool
        是否使用 jieba 分词（兼容保留，不影响结果）。

    Returns
    -------
    pandas.DataFrame
        列：``歌曲名``、``演唱``、``命中歌词``。
    """
    word = str(word).strip()
    if not word:
        raise ValueError("请输入要查询的词语。")
    rows: list[dict[str, str]] = []
    for _, work in works.iterrows():
        lyrics = str(work["歌词"])
        # 直接在原始歌词中做子串匹配，不再先用分词结果过滤。
        if word not in lyrics:
            continue
        matched_lines = [
            lyric_line.strip()
            for lyric_line in lyrics.splitlines()
            if word in lyric_line.strip()
        ]
        if matched_lines:
            rows.append({
                "歌曲名": work["歌曲名"],
                "演唱": work["演唱"],
                "命中歌词": "\n".join(matched_lines),
            })
    return pd.DataFrame(rows, columns=["歌曲名", "演唱", "命中歌词"])


def song_high_frequency_words(
    works: pd.DataFrame,
    frequency: pd.DataFrame,
    n: int,
    user_dict: str | Path | None = None,
    use_jieba: bool = True,
) -> pd.DataFrame:
    """统计每首歌包含多少个全局排名前 ``n`` 的高频词。

    ``frequency`` 必须是已由 :func:`word_frequency` 生成的词频表，表中从上到下
    的前 ``n`` 个词即查询范围。结果与 ``works`` 行数完全一致，依次给出歌曲名、
    命中数量、命中的高频词；同一首歌内的重复词只算一次。

    Parameters
    ----------
    works : pandas.DataFrame
        作品表。
    frequency : pandas.DataFrame
        已生成的词频表。
    n : int
        取前 n 个高频词，必须大于 0。
    user_dict : str | Path | None
        个人词典路径。
    use_jieba : bool
        是否使用 jieba 分词。

    Returns
    -------
    pandas.DataFrame
        列：``歌曲名``、``前n高频词数量``、``命中的前n高频词``。
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n 必须是大于 0 的整数。")
    top_words = frequency.head(n)["词语"].tolist()
    rows: list[dict[str, object]] = []
    for _, work in works.iterrows():
        song_words = set(cut_lyrics(work["歌词"], user_dict, use_jieba))
        # 依照全局词频排名输出，而不是按字母顺序输出。
        matched_words = [word for word in top_words if word in song_words]
        rows.append({
            "歌曲名": work["歌曲名"],
            "前n高频词数量": len(matched_words),
            "命中的前n高频词": "、".join(matched_words),
        })
    result_df = pd.DataFrame(rows, columns=["歌曲名", "前n高频词数量", "命中的前n高频词"])

    # 【修改点】按照“前n高频词数量”列进行降序排序
    # ascending=False 表示数量多的排在前面
    return result_df.sort_values(by="前n高频词数量", ascending=False)


# ---------------------------------------------------------------------------
# 合作者统计
# ---------------------------------------------------------------------------

def _names(value: str) -> set[str]:
    """仅按半角或全角斜杠拆分一格中的合作者，保留姓名中的其他文字。"""
    value = str(value).strip()
    if not value or value.lower() == "nan":
        return set()
    return {name.strip() for name in SPLIT_RE.split(value) if name.strip()}


def collaborator_frequency(works: pd.DataFrame, kind: str = "全部合作") -> pd.DataFrame:
    """按作品数统计合作人。

    Parameters
    ----------
    works : pandas.DataFrame
        作品表。
    kind : str
        统计口径，可选 ``"全部合作"``（演唱+作曲+编曲）、``"演唱合作"`` 或
        ``"曲合作"``（作曲+编曲）。一位合作人同一首歌在多个身份出现时，
        仍只计一次。

    Returns
    -------
    pandas.DataFrame
        列：``合作者``、``合作作品数``，按合作作品数降序排列。

    Raises
    ------
    ValueError
        当 ``kind`` 不在允许范围内时抛出。
    """
    mapping = {
        "全部合作": ["演唱", "作曲", "编曲"],
        "演唱合作": ["演唱"],
        "曲合作": ["作曲", "编曲"],
    }
    if kind not in mapping:
        raise ValueError(f"kind 只能是：{', '.join(mapping)}")
    counter: Counter[str] = Counter()
    for _, row in works.iterrows():
        names = set().union(*(_names(row[col]) for col in mapping[kind]))
        counter.update(names)
    result = pd.DataFrame([{"合作者": name, "合作作品数": count} for name, count in counter.items()])
    return result.sort_values(["合作作品数", "合作者"], ascending=[False, True]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 导出
# ---------------------------------------------------------------------------

def export_tables(output_dir: str | Path, frequency: pd.DataFrame, works: pd.DataFrame) -> Path:
    """将核心词频表和三类合作表导出为一个 Excel 工作簿。

    Parameters
    ----------
    output_dir : str | Path
        输出目录，不存在时自动创建。
    frequency : pandas.DataFrame
        由 :func:`word_frequency` 生成的词频表。
    works : pandas.DataFrame
        作品表，用于生成合作统计。

    Returns
    -------
    pathlib.Path
        保存的 Excel 文件路径。
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "统计结果.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frequency.to_excel(writer, sheet_name="全部词频", index=False)
        for length in (2, 3, 4):
            words_by_length(frequency, length).to_excel(writer, sheet_name=f"{length}字词", index=False)
        for kind in ("全部合作", "演唱合作", "曲合作"):
            collaborator_frequency(works, kind).to_excel(writer, sheet_name=kind, index=False)
    return path
