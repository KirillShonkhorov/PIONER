from typing import Dict, List

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from PydanticModels import Displacements, Stress, ProcessOutputModel


class BokehWriter:
    @staticmethod
    async def create_displacements_plot(displacements_data: Dict[str, List[Displacements]]):
        graphs = {}

        for filename, displacements_list in displacements_data.items():
            source = ColumnDataSource(data=dict(
                node=[d.node for d in displacements_list],
                x=[d.x + d.u for d in displacements_list],
                y=[d.y + d.v for d in displacements_list],
            ))

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="blue", line_color="black")

            script, div = components(p)

            div = div[5:-7]
            script = script[44:-15]

            graphs[filename] = {"scripts": script, "divs": div}

        return graphs

    @staticmethod
    async def create_stress_plot(stress_data: Dict[str, List[Stress]]):
        graphs = {}

        for filename, stress_list in stress_data.items():
            swapped_x = [d.x for d in stress_list]
            swapped_y = [d.y for d in stress_list]
            swapped_x[2], swapped_x[3] = swapped_x[3], swapped_x[2]
            swapped_y[2], swapped_y[3] = swapped_y[3], swapped_y[2]

            source = ColumnDataSource(data=dict(
                int_point=[d.int_point for d in stress_list],
                x=swapped_x,
                y=swapped_y
            ))

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="red", line_color="black")

            script, div = components(p)

            div = div[5:-7]
            script = script[44:-15]

            graphs[filename] = {"scripts": script, "divs": div}

        return graphs

    @classmethod
    async def create_plots(cls, result: ProcessOutputModel) -> ProcessOutputModel:
        displacements_graphs = await cls.create_displacements_plot(result.displacements)
        stress_graphs = await cls.create_stress_plot(result.stress)

        graphs = {
            "displacements": displacements_graphs,
            "stress": stress_graphs
        }

        return graphs
