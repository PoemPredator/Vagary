"""命令行入口。

使用方式::

    # 运行完整统计并导出结果到 output/
    python -m vagary --data data/vagary.xlsx --output output/

    # 查询某个词在哪些作品中出现
    python -m vagary --data data/vagary.xlsx --search 夜色

    # 指定个人词典和排除词
    python -m vagary --data data/vagary.xlsx --user-dict data/personal_dict.txt \
        --exclude 我们 你们 一个

也可在项目根目录执行 ``python -m vagary`` （使用默认路径）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vagary.stats import load_works, word_frequency, search_word, collaborator_frequency
from vagary.plotting import plot_frequency, plot_collaborators, save_chart


def main(argv: list[str] | None = None) -> int:
    """命令行主函数，返回退出码。"""
    parser = argparse.ArgumentParser(
        prog="vagary",
        description="Vagary 原创填词作品统计工具",
    )
    parser.add_argument(
        "--data", "-d",
        default="data/vagary.xlsx",
        help="Excel 数据文件路径（默认 data/vagary.xlsx）",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="输出目录（默认 output）",
    )
    parser.add_argument(
        "--user-dict",
        default=None,
        help="个人词典文件路径（可选）",
    )
    parser.add_argument(
        "--exclude", "-e",
        nargs="*",
        default=[],
        help="排除词列表，空格分隔（可选）",
    )
    parser.add_argument(
        "--search", "-s",
        default=None,
        help="查询某个词在哪些作品中出现",
    )
    parser.add_argument(
        "--no-jieba",
        action="store_true",
        help="不使用 jieba，使用保底分词算法",
    )
    args = parser.parse_args(argv)

    # ---- 读取数据 ----
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"错误：找不到数据文件 {data_path}", file=sys.stderr)
        return 1

    works = load_works(data_path)
    print(f"成功读取 {len(works)} 首作品。")

    # ---- 查询模式 ----
    if args.search:
        results = search_word(works, args.search, user_dict=args.user_dict, use_jieba=not args.no_jieba)
        if results.empty:
            print(f"未找到包含「{args.search}」的作品。")
        else:
            print(f"共 {len(results)} 首作品包含「{args.search}」：\n")
            for _, row in results.iterrows():
                print(f"  《{row['歌曲名']}》 — {row['演唱']}")
        return 0

    # ---- 完整统计模式 ----
    freq = word_frequency(
        works,
        exclude_words=args.exclude,
        user_dict=args.user_dict,
        use_jieba=not args.no_jieba,
    )
    print(f"共得到 {len(freq)} 个候选词。")
    print("\n前 20 高频词：")
    print(freq.head(20).to_string(index=False))

    # 合作统计
    all_collabs = collaborator_frequency(works, "全部合作")
    print("\n全部合作（前 10 名）：")
    print(all_collabs.head(10).to_string(index=False))

    # 导出表格
    from vagary.stats import export_tables
    output_path = export_tables(args.output, freq, works)
    print(f"\n已导出统计表：{output_path.resolve()}")

    # 绘制并保存图表
    charts_dir = Path(args.output) / "charts"
    for length in (2, 3, 4):
        ax = plot_frequency(freq, length=length, top_n=20, title=f"{length} 字高频词（按作品数）")
        save_chart(ax, charts_dir, f"{length}字高频词")
    ax = plot_collaborators(all_collabs, top_n=20, title="全部合作统计（前 20 名）")
    save_chart(ax, charts_dir, "全部合作统计")
    print(f"图表已保存至：{charts_dir.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
