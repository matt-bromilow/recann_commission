from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from django.views.generic import View
import json
from django.views.generic.base import TemplateView
from .models import Commission
from .scripts import genpdf
from django.template.loader import render_to_string

import psycopg2.extensions
DEC2FLOAT = psycopg2.extensions.new_type(
psycopg2._psycopg.DECIMAL.values, # oids for the decimal type
'DEC2FLOAT', # the new typecaster name
psycopg2.extensions.FLOAT) # the typecaster creating floats
psycopg2.extensions.register_type(DEC2FLOAT)
    
summary_data = """SELECT employee_id, SUM(commission_total_hours) AS total_hours_paid,  SUM(commission_fx_rate_to_gbp) AS total_comm_paid
    FROM public.timesheets_commission
    WHERE commission_ts_week_commencing ='2022-03-01'
    GROUP BY employee_id, commission_ts_week_commencing"""



class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def exec_sql(sql):
    obj=[]
    from django.db import connection, transaction
    cursor = connection.cursor()
    cursor.execute(sql)
    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    for row in rows:
        zip_iterator = zip(column_names, row)
        obj.append(dict(zip_iterator))
        

    return obj

def home(request):
    context = {}
    if request.method == 'POST' and 'run_script' in request.POST:
        obj = []
        # import function to run
        from .scripts import getCurrency
        print(request.POST['filename'])
        # call function
        getCurrency.convertFile(request.POST['filename']) 

        from django.db import connection, transaction
        cursor = connection.cursor()
        # Data retrieval operation - no commit required
        cursor.execute("SELECT candidate, custom_commission,employee_commission   FROM public.timesheets_jobs WHERE employee_id = 'Unassigned' ORDER BY candidate")
        sql = cursor.fetchall()
        for row in sql:
            #print(row[0])
            mydict = {"name":row[0],"CC":row[1],"comm":row[2]}
            obj.append(mydict)
        #jsoncx = json.dumps(sql,  use_decimal=True)
        jsoncx = json.dumps(sql, cls=JSONEncoder)
        context = {"unnassiged": obj}
        print("QUERY RAN")
        #print(context)
        #print(context)

    return render(request, "index.html", context)


def importLatestTimesheets(request):
    return HttpResponse("Timesheets")
    




class Statement(TemplateView):
    template_name = 'statement.html'
    def get_context_data(self,*args, **kwargs):
        context = super(Statement, self).get_context_data(*args,**kwargs)
        context['users'] = Commission.objects.all()
        context['summary'] = exec_sql(summary_data)
        print(context)
        return context

def DisplayStatement(request):
    context = {'statment':'test'}   
    return render(request, "statement.html", context)    


class GeneratePdf(View):
    def get(self, *args, **kwargs):
        data = Commission.objects.all()
        context = {'users': data}
        open('temp.html', "w").write(render_to_string('statement.html',  context))
        print(context)
        pdf = genpdf.html_to_pdf('temp.html')
         # rendering the template
        #doc_pdf = weasyprint.HTML('temp.html').write_pdf('sample.pdf')
        return HttpResponse(pdf, content_type='application/pdf')


def employee_group():
    obj = []

    from django.db import connection, transaction
    cursor = connection.cursor()
    # Data retrieval operation - no commit required
    cursor.execute(sql2)
    row2 = cursor.fetchall()
    for row2 in sql2:
        #print(row[0])
        mydict = {"emp":row2[0],"hr":row2[1],"comm":row2[2]}
        obj.append(mydict)
