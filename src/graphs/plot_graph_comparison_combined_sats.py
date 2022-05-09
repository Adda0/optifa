#!/usr/bin/env python3
# coding=utf-8

# file name: plot_graph_comparison_length_abstraction_parikh_image.py
#
# Script to analyze comparison of length and Parikh image state language abstraction optimizations for product
# construction algorithm.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT
from copy import deepcopy

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import sys

from pathlib import Path
from enum import Enum, unique


def get_dataframe(filename: str = "../../combined_results_appended.csv", verbose: bool = False) -> pd.DataFrame:
    """
    Gets data frame from specified data file.

    Args:
        filename (str): Name of the file with the data.
        verbose (bool): Whether to print informational messages.

    Returns:
        pd.DataFrame: Data in a data frame.
    """
    df = pd.read_csv(filename)
    # print(df)

    # for column_name in df.columns:
    # df[column_name] = pd.to_numeric(df[column_name])

    return df


def plot_graph_scatter_comparison(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """
    Plot graph depicting scatter comparison of basic and length abstraction / Parikh image construction algorithms.
    Args:
        df (pd.DataFrame): Data frame to plot.
        fig_location (str): Location where to store the generated figure. If None, do not store at all.
        show_figure (bool): Whether to show the generated figure.
    """

    df_et = df.filter(["ET.C.len.unsat", "ET.C.par.sat", "ET.C.par.unsat", "ET.C.processed"], axis=1)
    df_et.rename(
        columns={"ET.C.len.unsat": "FP.C.len.unsat", "ET.C.par.sat": "FP.C.par.sat", "ET.C.par.unsat": "FP.C.par.unsat",
                 "ET.C.processed": "FP.C.processed"}, inplace=True)

    df_fp = df.filter(["FP.C.len.unsat", "FP.C.par.sat", "FP.C.par.unsat", "FP.C.processed"], axis=1)
    df_fp = pd.concat([df_fp, df_et])
    df_fp.reset_index(inplace=True, drop=True)

    print(df_fp)


    # df_fp = df_fp[df_fp["FP.C.states"] <= df_fp[f"FP.L.smt_free.states"]]

    sns.set_theme(style="whitegrid")
    #df_fp.set_index('Day').plot(kind='bar', stacked=True, color=['steelblue', 'red'])
    sbg = sns.catplot(kind="bar", x=f"FP.C.processed",
                      y="FP.C.len.unsat", data=df_fp, legend=True)
    # sbg = sns.displot(x=f"{test_type.value}.B.states", y="count", hue="type", data=df, hue_order=hue_order, legend=True)
    # sbg.map_dataframe(sns.lineplot, f"{test_type.value}.B.states", f"{test_type.value}.B.states", color="grey", alpha=0.4)
    #sbg.ax.axline(xy1=(0, 0), slope=1, color="grey", alpha=.4, dashes=(5, 2))
    # plt.yticks(df.loc[:, "count"].unique())
    # plt.xticks([i for i in range(0, df.loc[:, "count"].max())])
    # sbg.set_axis_labels("Čas od začátku směny (min)", "Počet rozvážejících řidičů")
    max_val_axis = max(df[f"FP.L.smt_free.states"].max(), df[f"FP.C.states"].max()) * 1.3
    sbg.set(
        #xscale="symlog", yscale="symlog",
        xlabel=None, ylabel=None,
        #xlim=(-.1, max_val_axis), ylim=(-.1, max_val_axis),
    )
    sbg.despine()
    # sbg._legend.set_title("Druh vozidla")
    axis = sbg.axes.flat
    for ax in axis:
        ax.tick_params(bottom=True, left=True, labelleft=True, labelbottom=True)

    if fig_location:
        sbg.savefig(fig_location, format="pdf")

    if show_figure:
        plt.show()


if __name__ == "__main__":
    """
    Runs the main script operations when run as a standalone script.
    """
    data_file = Path(sys.argv[1])
    df = get_dataframe(data_file, False)
    plot_graph_scatter_comparison(df, fig_location=f"graph_combined_sats_comparison.pdf", show_figure=False)
