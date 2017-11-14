"""Handles plotting of the CTF information"""
from math import ceil, floor
import numpy as np

from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot
from bokeh.models.widgets import RangeSlider, Slider, TextInput, Button, Tabs, Panel, PreText
from bokeh.models import CustomJS, ColumnDataSource, HoverTool

from helper.ctf_log_extraction import build_df, write_subset_star


def main(files):
    """Create plots"""
    def create_histograms():
        """Output grid for all histograms"""
        def plot_histogram(data, label):
            """Create a single histogram"""
            hist = figure(title=label, plot_width=600, plot_height=400)
            data_hist, edges_hist = np.histogram(data, bins=50)
            hist.quad(top=data_hist, bottom=0, left=edges_hist[:-1],
                      right=edges_hist[1:], alpha=0.5)
            hist.xaxis.axis_label = label
            return hist

        hist1 = plot_histogram(source_available.data['Resolution_limit'], 'Resolution')
        hist2 = plot_histogram(source_available.data['Defocus'], 'Defocus')
        hist3 = plot_histogram(source_available.data['CC_score'], 'CC Score')
        hist4 = plot_histogram(source_available.data['Defocus_difference'], 'Defocus Difference')

        return gridplot([hist1, hist2],
                        [hist3, hist4])

    def create_scatterplots():
        """Output scatterplot layout"""
        plot_width = 750
        plot_height = 600

        scatter1 = figure(title="Defocus vs. Resolution",
                          tools=TOOLS,
                          plot_width=plot_width,
                          plot_height=plot_height)
        scatter1.xaxis.axis_label = "Defocus"
        scatter1.yaxis.axis_label = "Estimated resolution"
        scatter1.circle(source=source_visible,
                        x='Defocus',
                        y='Resolution_limit',
                        color="mediumvioletred",
                        alpha=0.75)

        scatter2 = figure(title="Defocus difference vs. CC score",
                          tools=TOOLS,
                          plot_width=plot_width,
                          plot_height=plot_height)
        scatter2.xaxis.axis_label = "Defocus difference"
        scatter2.yaxis.axis_label = "CC Score"
        scatter2.circle(source=source_visible,
                        x='Defocus_difference',
                        y='CC_score',
                        color="royalblue",
                        alpha=0.75)

        hover = scatter1.select_one(HoverTool).tooltips = [
            ("Mic", "@Micrograph_name")
        ]
        hover = scatter2.select_one(HoverTool).tooltips = [
            ("Mic", "@Micrograph_name")
        ]

        callback = CustomJS(args=dict(source_visible=source_visible,
                                      source_available=source_available), code="""
                var data_visible = source_visible.data;
                var data_available = source_available.data;

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
                source_visible.change.emit();
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

        sliders = {"res": res_slider,
                   "def": defocus_slider,
                   "dif": def_diff_slider,
                   "ccs": cc_slider}
        for (key, slider) in sliders.iteritems():
            callback.args[key] = slider
            slider.js_on_change('value', callback)

        def save_subset_star():
            """"Save selected subset to new star file"""
            keep_list = data[
                (data['Resolution_limit'] <= res_slider.value) &
                (data['Defocus'] >= defocus_slider.value[0]) &
                (data['Defocus'] <= defocus_slider.value[1]) &
                (data['Defocus_difference'] <= def_diff_slider.value) &
                (data['CC_score'] >= cc_slider.value)
                ]['Micrograph_name'].values
            write_subset_star(star_in.value, star_out.value, keep_list)

        def write_summary():
            """Write summary data of selected subset"""
            subset_summary.text = "Subset dataset:\n{0}".format(str(data[
                (data['Resolution_limit'] <= res_slider.value) &
                (data['Defocus'] >= defocus_slider.value[0]) &
                (data['Defocus'] <= defocus_slider.value[1]) &
                (data['Defocus_difference'] <= def_diff_slider.value) &
                (data['CC_score'] >= cc_slider.value)
                ][['Resolution_limit', 'Defocus',
                   'Defocus_difference', 'CC_score']].describe()))

        csv_name = TextInput(value="ctf_data.csv", title="Output CSV:")
        save_all_csv = Button(label="Save all csv", button_type="success")
        save_all_csv.on_click(lambda: data.to_csv(csv_name.value, index=False))
        save_subset_csv = Button(label="Save subset csv", button_type="success")
        save_subset_csv.on_click(lambda: data[
            (data['Resolution_limit'] <= res_slider.value) &
            (data['Defocus'] >= defocus_slider.value[0]) &
            (data['Defocus'] <= defocus_slider.value[1]) &
            (data['Defocus_difference'] <= def_diff_slider.value) &
            (data['CC_score'] >= cc_slider.value)
            ].to_csv(csv_name.value, index=False))
        star_in = TextInput(value=default_star, title="Input star:")
        star_out = TextInput(value="subset_micrographs.star", title="Output star:")
        save_star = Button(label="Save star", button_type="success")
        save_star.on_click(save_subset_star)
        total_summary = PreText(text="Total dataset:\n{0}".format(str(data[[
            'Resolution_limit',
            'Defocus',
            'Defocus_difference',
            'CC_score']].describe())), width=600)
        subset_summary = PreText(text='', width=600)
        summary_button = Button(label="Summary Stats", button_type="success")
        summary_button.on_click(write_summary)

        return gridplot([scatter1, scatter2],
                        [res_slider, defocus_slider, def_diff_slider, cc_slider, summary_button],
                        [total_summary, subset_summary],
                        [csv_name, star_in, star_out],
                        [save_all_csv, save_star],
                        [save_subset_csv])

    data = build_df(files)

    TOOLS = "crosshair,pan,tap,box_select,wheel_zoom,box_zoom,reset,hover,save"
    default_star = "micrographs_all_gctf.star"
    RESOLUTION_MAX = ceil(data['Resolution_limit'].max())
    DEFOCUS_MAX = ceil(data['Defocus'].max() / 1000) * 1000
    DEFOCUS_DIFF_MAX = ceil(data['Defocus_difference'].max() / 100) * 100
    CC_MIN = floor(data['CC_score'].min() * 100) / 100
    CC_MAX = ceil(data['CC_score'].max() * 100) / 100

    source_visible = ColumnDataSource(data)
    source_available = ColumnDataSource(data)

    scatter_layout = create_scatterplots()
    hist_layout = create_histograms()

    tab1 = Panel(child=scatter_layout, title="Data")
    tab2 = Panel(child=hist_layout, title="Summary")
    tabs = Tabs(tabs=[tab1, tab2])
    doc = curdoc()
    doc.add_root(tabs)
