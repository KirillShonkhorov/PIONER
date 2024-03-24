from typing import Dict, List
from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from PydanticModels import Displacements, Stress, ProcessOutputModel


class BokehWriter:
    @staticmethod
    async def create_displacements_plot(displacements_data: Dict[str, List[Displacements]]):
        plots = []
        for filename, displacements_list in displacements_data.items():

            source = ColumnDataSource(data=dict(
                node=[d.node for d in displacements_list],
                x=[d.x + d.u for d in displacements_list],
                y=[d.y + d.v for d in displacements_list],
            ))

            print(f"Node {source.data.get('node')}. X {source.data.get('x')} Y {source.data.get('y')}")

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="blue", line_color="black")
            plots.append(p)

        # Do not save to file, instead, get components
        script, div = components(gridplot(plots, ncols=1))
        return script, div

    @staticmethod
    async def create_stress_plot(stress_data: Dict[str, List[Stress]]):
        plots = []
        for filename, stress_list in stress_data.items():

            # Swap third and fourth elements in 'x' and 'y'
            swapped_x = [d.x for d in stress_list]
            swapped_y = [d.y for d in stress_list]
            swapped_x[2], swapped_x[3] = swapped_x[3], swapped_x[2]
            swapped_y[2], swapped_y[3] = swapped_y[3], swapped_y[2]

            source = ColumnDataSource(data=dict(
                int_point=[d.int_point for d in stress_list],
                # x=[d.x for d in stress_list],
                # y=[d.y for d in stress_list],
                x=swapped_x,
                y=swapped_y
            ))

            print(f"Int point {source.data.get('int_point')}. X {source.data.get('x')} Y {source.data.get('y')}")

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="red", line_color="black")
            plots.append(p)

        # Do not save to file, instead, get components
        script, div = components(gridplot(plots, ncols=1))
        return script, div

    @classmethod
    async def create_plots(cls, result: ProcessOutputModel) -> ProcessOutputModel:
        displacements_scripts, displacements_divs = await cls.create_displacements_plot(result.displacements)
        stress_scripts, stress_divs = await cls.create_stress_plot(result.stress)

        # Удаляем теги <script> и <div> из полученных данных
        displacements_scripts = displacements_scripts[44:-15]
        displacements_divs = displacements_divs[5:-7]
        stress_scripts = stress_scripts[44:-15]
        stress_divs = stress_divs[5:-7]

        graphs = {
            "displacements": {"scripts": displacements_scripts, "divs": displacements_divs},
            "stress": {"scripts": stress_scripts, "divs": stress_divs}
        }

        return graphs
