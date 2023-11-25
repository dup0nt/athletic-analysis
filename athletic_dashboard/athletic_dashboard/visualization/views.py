from django.shortcuts import render

from .api_data import *
import pandas as pd


# Create your views here.

def print_database(request):

    header = update_tokens(request)
    df = get_database(header, 'activities')

    df_html = df.to_html()

    context = {
        "df_html": df_html
    }
    return render(request, 'athelete_and_testerdata.html', context)
