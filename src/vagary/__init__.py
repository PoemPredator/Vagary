"""Vagary —— 原创填词作品统计工具包。

统计单位是"作品数"：同一词在同一首歌重复出现，只计一次。

快速上手
-------
>>> from vagary import load_works, word_frequency
>>> works = load_works("data/vagary.xlsx")
>>> freq = word_frequency(works)
>>> freq.head(10)
"""
from vagary.stats import (
    load_works,
    cut_lyrics,
    word_frequency,
    words_by_length,
    search_word,
    song_high_frequency_words,
    collaborator_frequency,
    export_tables,
)
from vagary.plotting import (
    setup_chinese_font,
    plot_frequency,
    plot_collaborators,
    save_chart,
)

__version__ = "1.0.0"

__all__ = [
    # stats
    "load_works",
    "cut_lyrics",
    "word_frequency",
    "words_by_length",
    "search_word",
    "song_high_frequency_words",
    "collaborator_frequency",
    "export_tables",
    # plotting
    "setup_chinese_font",
    "plot_frequency",
    "plot_collaborators",
    "save_chart",
    # meta
    "__version__",
]
