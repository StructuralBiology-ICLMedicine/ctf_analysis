"""Handles plotting of the CTF information"""
from math import ceil, floor
import numpy as np

from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot
from bokeh.models.widgets import RangeSlider, Slider, TextInput, Button, Tabs, Panel, PreText
from bokeh.models import CustomJS, ColumnDataSource, HoverTool

from ctf_extraction import build_df


def main(files):
    def create_histograms():
        plot_width = 600
        plot_height = 400

        h1 = figure(title="Resolution summary", plot_width=plot_width, plot_height=plot_height)
        res_hist, res_edges = np.histogram(source_available.data['Resolution_limit'], bins=50)
        h1.quad(top=res_hist, bottom=0, left=res_edges[:-1], right=res_edges[1:], alpha=0.5)
        h1.xaxis.axis_label = "Resolution"

        h2 = figure(title="Defocus summary", plot_width=plot_width, plot_height=plot_height)
        def_hist, def_edges = np.histogram(source_available.data['Defocus'], bins=50)
        h2.quad(top=def_hist, bottom=0, left=def_edges[:-1], right=def_edges[1:], alpha=0.5)
        h2.xaxis.axis_label = "Defocus"

        h3 = figure(title="CC Score summary", plot_width=plot_width, plot_height=plot_height)
        cc_hist, cc_edges = np.histogram(source_available.data['CC_score'], bins=50)
        h3.quad(top=cc_hist, bottom=0, left=cc_edges[:-1], right=cc_edges[1:], alpha=0.5)
        h3.xaxis.axis_label = "CC Score"

        h4 = figure(title="Defocus difference summary", plot_width=plot_width, plot_height=plot_height)
        dif_hist, dif_edges = np.histogram(source_available.data['Defocus_difference'], bins=50)
        h4.quad(top=dif_hist, bottom=0, left=dif_edges[:-1], right=dif_edges[1:], alpha=0.5)
        h4.xaxis.axis_label = "Defocus difference"
        return gridplot([h1, h2],
                        [h3, h4])

    def create_scatterplots():
        plot_width = 750
        plot_height = 600

        s1 = figure(title="Defocus vs. Resolution", tools=TOOLS, plot_width=plot_width, plot_height=plot_height)
        s1.xaxis.axis_label = "Defocus"
        s1.yaxis.axis_label = "Estimated resolution"
        s1.circle(source=source_visible, x='Defocus', y='Resolution_limit', color="mediumvioletred", alpha=0.75)

        s2 = figure(title="Defocus difference vs. CC score", tools=TOOLS, plot_width=plot_width,
                    plot_height=plot_height)
        s2.xaxis.axis_label = "Defocus difference"
        s2.yaxis.axis_label = "CC Score"
        s2.circle(source=source_visible, x='Defocus_difference', y='CC_score', color="royalblue", alpha=0.75)

        hover = s1.select_one(HoverTool).tooltips = [
            ("Mic", "@Micrograph_name")
        ]
        hover = s2.select_one(HoverTool).tooltips = [
            ("Mic", "@Micrograph_name")
        ]

        callback = CustomJS(args=dict(source_visible=source_visible,
                                      source_available=source_available), code="""
                var data_visible = source_visible.get('data');
                var data_available = source_available.get('data');

                var res_max = res.value;
                var def_min = def.value[0];
                var def_max = def.value[1];
                var dif_max = dif.value;
                var cc_min = ccs.value;

                for (var key in data_available) {
                    data_visible[key] = [];
                    for (var i=0; i<data_available['Resolution_limit'].length; i++) {
                        if ((data_available['Resolution_limit'][i] <= res_max) &&
                            (data_available['Defocus'][i] >= def_min) &&
                            (data_available['Defocus'][i] <= def_max) &&
                            (data_available['Defocus_difference'][i] <= dif_max) &&
                            (data_available['CC_score'][i] >= cc_min)) {
                                data_visible[key].push(data_available[key][i]);
                        }
                    }
                }
                source_visible.trigger('change');
            """)

        res_slider = Slider(start=0,
                            end=RESOLUTION_MAX,
                            step=0.5,
                            title="Resolution",
                            value=RESOLUTION_MAX)

        defocus_slider = RangeSlider(start=0,
                                     end=DEFOCUS_MAX,
                                     step=1000,
                                     title="Defocus",
                                     value=(0, DEFOCUS_MAX))

        def_diff_slider = Slider(start=0,
                                 end=DEFOCUS_DIFF_MAX,
                                 step=100,
                                 title="Difference",
                                 value=DEFOCUS_DIFF_MAX)

        cc_slider = Slider(start=CC_MIN,
                           end=CC_MAX,
                           step=0.01,
                           title="CC_Score",
                           value=CC_MIN)

        callback.args["res"] = res_slider
        callback.args["def"] = defocus_slider
        callback.args["dif"] = def_diff_slider
        callback.args["ccs"] = cc_slider

        res_slider.js_on_change('value', callback)
        defocus_slider.js_on_change('value', callback)
        def_diff_slider.js_on_change('value', callback)
        cc_slider.js_on_change('value', callback)

        def save_subset_star():
            keep_list = df[
                (df['Resolution_limit'] <= res_slider.value) &
                (df['Defocus'] >= defocus_slider.value[0]) &
                (df['Defocus'] <= defocus_slider.value[1]) &
                (df['Defocus_difference'] <= def_diff_slider.value) &
                (df['CC_score'] >= cc_slider.value)
                ]['Micrograph_name'].values
            write_subset_star(star_in.value, star_out.value, keep_list)

        def write_summary():
            subset_summary.text = "Subset dataset:\n{0}".format(str(df[
                                                                        (df[
                                                                             'Resolution_limit'] <= res_slider.value) &
                                                                        (df['Defocus'] >= defocus_slider.value[0]) &
                                                                        (df['Defocus'] <= defocus_slider.value[1]) &
                                                                        (df[
                                                                             'Defocus_difference'] <= def_diff_slider.value) &
                                                                        (df['CC_score'] >= cc_slider.value)
                                                                        ][['Resolution_limit',
                                                                           'Defocus',
                                                                           'Defocus_difference',
                                                                           'CC_score']].describe()))

        csv_name = TextInput(value="ctf_data.csv", title="Output CSV:")
        save_all_csv = Button(label="Save all csv", button_type="success")
        save_all_csv.on_click(lambda: df.to_csv(csv_name.value, index=False))
        save_subset_csv = Button(label="Save subset csv", button_type="success")
        save_subset_csv.on_click(lambda: df[
            (df['Resolution_limit'] <= res_slider.value) &
            (df['Defocus'] >= defocus_slider.value[0]) &
            (df['Defocus'] <= defocus_slider.value[1]) &
            (df['Defocus_difference'] <= def_diff_slider.value) &
            (df['CC_score'] >= cc_slider.value)
            ].to_csv(csv_name.value, index=False))
        star_in = TextInput(value=default_star, title="Input star:")
        star_out = TextInput(value="subset_micrographs.star", title="Output star:")
        save_star = Button(label="Save star", button_type="success")
        save_star.on_click(save_subset_star)
        total_summary = PreText(text="Total dataset:\n{0}".format(str(df[['Resolution_limit',
                                                                              'Defocus',
                                                                              'Defocus_difference',
                                                                              'CC_score']].describe())), width=600)
        subset_summary = PreText(text='', width=600)
        summary_button = Button(label="Summary Stats", button_type="success")
        summary_button.on_click(write_summary)

        return gridplot([s1, s2],
                        [res_slider, defocus_slider, def_diff_slider, cc_slider, summary_button],
                        [total_summary, subset_summary],
                        [csv_name, star_in, star_out],
                        [save_all_csv, save_star],
                        [save_subset_csv])

    df = build_df(files)

    TOOLS = "crosshair,pan,tap,box_select,wheel_zoom,box_zoom,reset,hover,save"
    default_star = "micrographs_all_gctf.star"
    RESOLUTION_MAX = ceil(df['Resolution_limit'].max())
    DEFOCUS_MAX = ceil(df['Defocus'].max() / 1000) * 1000
    DEFOCUS_DIFF_MAX = ceil(df['Defocus_difference'].max() / 100) * 100
    CC_MIN = floor(df['CC_score'].min() * 100) / 100
    CC_MAX = ceil(df['CC_score'].max() * 100) / 100

    source_visible = ColumnDataSource(df)
    source_available = ColumnDataSource(df)

    scatter_layout = create_scatterplots()
    hist_layout = create_histograms()

    tab1 = Panel(child=scatter_layout, title="Data")
    tab2 = Panel(child=hist_layout, title="Summary")
    tabs = Tabs(tabs=[tab1, tab2])
    doc = curdoc()
    doc.add_root(tabs)