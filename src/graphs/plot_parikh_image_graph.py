#!/usr/bin/env python3
# coding=utf-8

# file name: plot_parikh_image_graph.py
#
# Script to analyze result data of Parikh image state language abstraction optimization for product construction algorithm.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT


from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import sys

from pathlib import Path


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
    print(df)

    #for column_name in df.columns:
        #df[column_name] = pd.to_numeric(df[column_name])

    return df


def plot_graph(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """
    Plot graph depicting restaurant driver utility per minute.
    Args:
        df (pd.DataFrame): Data frame to plot.
        fig_location (str): Location where to store the generated figure. If None, do not store at all.
        show_figure (bool): Whether to show the generated figure.
    """
    vehicle_type_map = {
        #"FP.B.states": "Basic",
        "FP.C.states": "Combined LA + PI",
        "FP.P.no_lengths.states": "Parikh image",
        "FP.L.smt_free.states": "Length abstraction",
    }

    value_vars = [
        "FP.C.states",
        #"FP.P.no_lengths.states",
        "FP.L.smt_free.states",
    ]

    hue_order = [
        "Length abstraction",
        "Combined LA + PI",
        #"FP.P.no_lengths.states",
    ]


    df = df.melt(id_vars=["Larger automaton", "Smaller automaton", "FP.B.states"], value_vars=value_vars, var_name='type',
                 value_name='count')
    df.loc[:, "type"] = df["type"].map(vehicle_type_map).astype('category')

    #df["count"] = df["count"].fillna(0)
    #df.loc[:, "count"] = df["count"].astype('int')
    #print(df)

    sns.set_theme(style="whitegrid")
    sbg = sns.relplot(x="FP.B.states", y="count", hue="type", data=df, hue_order=hue_order)
    sbg.map_dataframe(sns.lineplot, 'FP.B.states', 'FP.B.states', color='grey', )
    #plt.yticks(df.loc[:, "count"].unique())
    #plt.xticks([i for i in range(0, df.loc[:, "count"].max())])
    sbg.set_axis_labels("Čas od začátku směny (min)", "Počet rozvážejících řidičů")
    sbg.set(xscale="log", yscale="log")
    sbg.despine()
    sbg._legend.set_title("Druh vozidla")
    axis = sbg.axes.flat
    for ax in axis:
        ax.tick_params(bottom=True, left=True, labelleft=True, labelbottom=True)

    if fig_location:
        sbg.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    """
    Runs the main script operations when run as a standalone script.
    """
    data_file = Path(sys.argv[1])
    print(data_file.stem)
    #df = get_dataframe(f"{filename}.csv", False)
    df = get_dataframe(data_file, False)
    #plot_graph(df, fig_location=f"{data_file.stem}.png", show_figure=False)
    plot_graph(df, fig_location=f"test.png", show_figure=False)
