from quickchart import QuickChart, QuickChartFunction

import re
import json


def annotated_progress_bar(percentage: float, label: str) -> str:
    qc = QuickChart()
    qc.width = 500
    qc.height = 150
    qc.version = '3'

    qc.config = {
        'type': 'bar',
        'data': {
            'labels': ['Q1'],
            'datasets': [
                {
                    'label': 'Users',
                    'data': [100],
                    'backgroundColor': QuickChartFunction("getGradientFillHelper('horizontal', ['green', 'yellow', 'orange', 'red'])"),
                },
            ],
        },
        'options': {
            'indexAxis': 'y',
            'layout': {
                'padding': 40,
            },
            'scales': {
                'x': {
                    'display': False,
                },
                'y': {
                    'display': False,
                },
            },
            'plugins': {
                'legend': {
                    'display': False,
                },
                'annotation': {
                    'clip': False,
                    'common': {
                        'drawTime': 'afterDraw',
                    },
                    'annotations': {
                        'low': {
                            'type': 'label',
                            'xValue': 4,
                            'content': ['Low'],
                            'font': {
                                'size': 18,
                                'weight': 'bold',
                            },
                        },
                        'medium': {
                            'type': 'label',
                            'xValue': 50,
                            'content': ['Medium'],
                            'font': {
                                'size': 18,
                                'weight': 'bold',
                            },
                        },
                        'high': {
                            'type': 'label',
                            'xValue': 95,
                            'content': ['High'],
                            'font': {
                                'size': 18,
                                'weight': 'bold',
                            },
                        },
                        'arrow': {
                            'type': 'point',
                            'pointStyle': 'triangle',
                            'backgroundColor': '#000',
                            'radius': 15,
                            'xValue': percentage,
                            'yAdjust': 65,
                        },
                        'label1': {
                            'type': 'label',
                            'xValue': percentage,
                            'yAdjust': 95,
                            'content': [f'{label}', f'{percentage}%'],
                            'font': {
                                'size': 18,
                                'weight': 'bold',
                            },
                        },
                    },
                },
            },
        },
    }

    return qc.get_short_url()
