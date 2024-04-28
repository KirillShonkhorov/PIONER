"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [25.04.24]
Purpose: [Bokeh renderer class. Renders graphic elements of a web page.]
"""

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from PydanticModels import *


class BokehWriter:
    @classmethod
    async def create_plots(cls, result: ProcessOutputModel) -> GraphsModel:
        """
        The method combines graphic elements.
        :return: ProcessOutputModel.graphs = GraphsModel
        """
        logging.info(f"\t****Start combines elements Bokeh****\t")

        displacements_graphs = await cls.create_displacements_plot(result.displacements)
        stress_graphs = await cls.create_stress_plot(result.stress)

        logging.info("\t****Finish combines elements Bokeh****\t")

        return GraphsModel(displacements=displacements_graphs, stress=stress_graphs)

    @staticmethod
    async def create_displacements_plot(displacements_data) -> Dict[str, PlotModel]:
        """
        Draws graphic elements based on data from "Displacements".
        :exception: 509
        :return: Dict[displacements_file_name, PlotModel]
        """
        logging.info(f"\t\t****Start drawing 'Displacements' element Bokeh****\t\t")

        graphs = {}
        try:
            for file_name, displacements_list in displacements_data.items():
                source = ColumnDataSource(data=dict(
                    node=[d.node for d in displacements_list],
                    x=[d.x + d.u for d in displacements_list],
                    y=[d.y + d.v for d in displacements_list],
                ))

                p = figure(title=file_name, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
                p.patch('x', 'y', source=source, fill_color="blue", line_color="black")

                script, div = components(p)

                script = script[44:-15]
                div = div[5:-7]

                logging.debug(f"In '{file_name}'\nscript = '{script}'\ndiv = '{div}'")

                graphs[file_name] = PlotModel(script=script, div=div)

            return graphs

        except Exception as error509:
            logging.exception(f"JSON-RPC_Server error while drawing 'Displacements' element Bokeh:\n{error509}")
            raise Error(data={'details': f"JSON-RPC_Server error while drawing 'Displacements' element Bokeh:\n{error509}", 'status_code': 509})
        finally:
            logging.debug(f"Plots in 'Displacements' = {graphs}")
            logging.info(f"\t\t****Finish drawing 'Displacements' element Bokeh****\t\t")

    @staticmethod
    async def create_stress_plot(stress_data) -> Dict[str, PlotModel]:
        """
        Draws graphic elements based on data from "Stress".
        :exception: 510
        :return: Dict[stress_file_name, PlotModel]
        """
        logging.info(f"\t\t****Start drawing 'Stress' element Bokeh****\t\t")

        graphs = {}
        try:
            for file_name, stress_list in stress_data.items():
                swapped_x = [d.x for d in stress_list]
                swapped_y = [d.y for d in stress_list]
                swapped_x[2], swapped_x[3] = swapped_x[3], swapped_x[2]
                swapped_y[2], swapped_y[3] = swapped_y[3], swapped_y[2]

                source = ColumnDataSource(data=dict(
                    int_point=[d.int_point for d in stress_list],
                    x=swapped_x,
                    y=swapped_y
                ))

                p = figure(title=file_name, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
                p.patch('x', 'y', source=source, fill_color="red", line_color="black")

                script, div = components(p)

                div = div[5:-7]
                script = script[44:-15]

                logging.debug(f"In '{file_name}'\nscript = '{script}'\ndiv = '{div}'")

                graphs[file_name] = PlotModel(script=script, div=div)

            return graphs

        except Exception as error510:
            logging.exception(f"JSON-RPC_Server error while drawing 'Stress' element Bokeh:\n{error510}")
            raise Error(data={'details': f"JSON-RPC_Server error while drawing 'Stress' element Bokeh:\n{error510}", 'status_code': 510})
        finally:
            logging.debug(f"Plots in 'Stress' = {graphs}")
            logging.info(f"\t\t****Finish drawing 'Stress' element Bokeh****\t\t")
