"""绘图与图表保存功能。

包含中文字体设置、词频柱状图、合作者柱状图，以及将图表保存为
PNG / SVG / PKL 三种格式的工具函数。
"""
from __future__ import annotations

from pathlib import Path
import pickle

import matplotlib.pyplot as plt
import pandas as pd

from vagary.stats import words_by_length


# 色盲友好的定性配色；柱子按名次循环使用，便于区分相邻项目。
BAR_COLORS = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
]


def setup_chinese_font() -> None:
    """设置常见中文字体；缺少其中某一种字体时 matplotlib 会自动尝试下一种。"""
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False


def plot_frequency(
    frequency: pd.DataFrame,
    length: int | None = None,
    top_n: int = 20,
    title: str | None = None,
):
    """绘制横向高频词图，返回 matplotlib 的坐标轴，可继续保存或调整。

    Parameters
    ----------
    frequency : pandas.DataFrame
        由 :func:`~vagary.word_frequency` 生成的词频表。
    length : int | None
        筛选指定字数；``None`` 表示不筛选。
    top_n : int
        取前若干名绘制，默认 20。
    title : str | None
        自定义图表标题；``None`` 时自动生成。

    Returns
    -------
    matplotlib.axes.Axes
        绘制完成的坐标轴对象。
    """
    setup_chinese_font()
    data = frequency if length is None else words_by_length(frequency, length)
    data = data.head(top_n).sort_values("出现作品数")
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.42)))
    colors = [BAR_COLORS[index % len(BAR_COLORS)] for index in range(len(data))]
    ax.barh(data["词语"], data["出现作品数"], color=colors)
    ax.set_xlabel("出现作品数（同一作品重复不重复计数）")
    ax.set_title(title or (f"{length} 字高频词" if length else "高频词"))
    for y, value in enumerate(data["出现作品数"]):
        ax.text(value, y, f" {value}", va="center")
    fig.tight_layout()
    return ax


def plot_collaborators(
    collaborators: pd.DataFrame,
    top_n: int = 20,
    title: str = "合作统计图",
):
    """绘制合作统计横向柱状图。

    Parameters
    ----------
    collaborators : pandas.DataFrame
        由 :func:`~vagary.collaborator_frequency` 生成的合作统计表。
    top_n : int
        取前若干名绘制，默认 20。
    title : str
        图表标题。

    Returns
    -------
    matplotlib.axes.Axes
        绘制完成的坐标轴对象。
    """
    setup_chinese_font()
    data = collaborators.head(top_n).sort_values("合作作品数")
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.42)))
    colors = [BAR_COLORS[index % len(BAR_COLORS)] for index in range(len(data))]
    ax.barh(data["合作者"], data["合作作品数"], color=colors)
    ax.set_xlabel("合作作品数（同一首歌只计一次）")
    ax.set_title(title)
    for y, value in enumerate(data["合作作品数"]):
        ax.text(value, y, f" {value}", va="center")
    fig.tight_layout()
    return ax


def save_chart(ax, output_dir: str | Path = "output/charts", filename: str = "统计图") -> dict[str, Path]:
    """保存一个统计图为 PNG、SVG 与 matplotlib 可编辑的 PKL 文件。

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        由 :func:`plot_frequency` 或 :func:`plot_collaborators` 返回的坐标轴。
    output_dir : str | Path
        输出目录，不存在时自动创建。
    filename : str
        文件名（不含扩展名）。

    Returns
    -------
    dict[str, pathlib.Path]
        三个文件路径，键为 ``"PNG"``、``"SVG"``、``"可编辑PKL"``。

    Notes
    -----
    PNG 适合直接使用，SVG 可在 Illustrator / Inkscape 等软件编辑；
    PKL 是 Python / matplotlib 的可编辑图形对象，可用 ``pickle.load`` 重新打开。
    MATLAB 的 ``.fig`` 是专有格式，matplotlib 不能可靠生成，故不伪造该格式。
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    base = output / filename
    figure = ax.figure
    png_path = base.with_suffix(".png")
    svg_path = base.with_suffix(".svg")
    pkl_path = base.with_suffix(".pkl")
    figure.savefig(png_path, dpi=220, bbox_inches="tight")
    figure.savefig(svg_path, bbox_inches="tight")
    with pkl_path.open("wb") as file:
        pickle.dump(figure, file)
    return {"PNG": png_path, "SVG": svg_path, "可编辑PKL": pkl_path}
