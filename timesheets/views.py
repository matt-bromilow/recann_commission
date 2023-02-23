from urllib.request import Request
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from decimal import Decimal
from django.views.generic import View
import json
from django.views.generic.base import TemplateView
from .models import Commission
from .scripts import pdf_export
from django.template.loader import render_to_string
import os, datetime
import tablib

import psycopg2.extensions
DEC2FLOAT = psycopg2.extensions.new_type(
psycopg2._psycopg.DECIMAL.values, # oids for the decimal type
'DEC2FLOAT', # the new typecaster name
psycopg2.extensions.FLOAT) # the typecaster creating floats
psycopg2.extensions.register_type(DEC2FLOAT)
    
summary_data = """SELECT employee_id, SUM(commission_total_hours) AS total_hours_paid,  SUM(commission_gp_per_hour_gbp) AS total_comm_paid
    FROM public.timesheets_commission
    WHERE commission_ts_week_commencing = (SELECT date FROM timesheets_month LIMIT 1)
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

    sqlcreatefunc="""create or replace function get_Commission(cname text)
   returns numeric(12,4)
   language plpgsql
   AS
   $$
declare 
commsam numeric(12,4);
begin
	SELECT MAX(employee_commission) INTO commsam FROM public.timesheets_employee 
	WHERE employee::text = cname;
	return commsam;
end;
$$;"""




    obj = []
    obj2 = []
    obj3 = []
    context = {}
    from django.db import connection, transaction
    cursor = connection.cursor()
    # Data retrieval operation - no commit required
    cursor.execute(sqlcreatefunc) #create function if not on local system
    cursor.execute("SELECT candidate, custom_commission,employee_commission, tid   FROM public.timesheets_jobs WHERE employee_id = 'Unassigned' ORDER BY candidate")
    sql = cursor.fetchall()
    for row in sql:
        #print(row[0])
        mydict = {"name":row[0],"CC":row[1],"comm":row[2],"tid":row[3]}
        obj.append(mydict)

    cursor.execute("SELECT employee, employee_commission * 100 FROM public.timesheets_employee;")
    sql = cursor.fetchall()
    for row in sql:
        #print(row[0])
        mydict = {"employee":row[0],"commission":row[1]}
        obj2.append(mydict)

    cursor.execute("SELECT distinct date FROM public.timesheets_timesheets;")
    sql = cursor.fetchall()
    for row in sql:
        mydict = {"date":row[0].strftime('%Y-%m-%d')}
        obj3.append(mydict)

        #jsoncx = json.dumps(sql,  use_decimal=True)
    #jsoncx = json.dumps(sql, cls=JSONEncoder)
    context = {"unnassiged": obj, "consultants": obj2, "dates": obj3}

    #print("QUERY RAN")
    #print(request.POST)
    if request.method == 'POST' and 'run_script' in request.POST:
        obj = []
        # import function to run
        from .scripts import getCurrency
        #print(request.POST['filename'])
        # call function
        getCurrency.convertFile(request.POST['filename']) 

    #start import test
        from import_export import resources
        from .resources import JobsResource, TimesheetResource
        from .models import Jobs

    #Import Jobs
        dataset = tablib.Dataset()
        job_resource = JobsResource()
        with open('./output.csv', 'r') as fh:
            imported_data  =  dataset.load(fh, format='csv')
        result =  job_resource.import_data(dataset, dry_run=False)

    #Import Timesheets
        dataset = tablib.Dataset()
        ts_resource = TimesheetResource()
        with open('./output.csv', 'r') as fh:
            imported_data  =  dataset.load(fh, format='csv')
        result =  ts_resource.import_data(dataset, dry_run=False)

        print(imported_data)
        print(result.has_errors())
        print('success')

        from django.db import connection, transaction
        cursor = connection.cursor()
        # Data retrieval operation - no commit required
        cursor.execute("SELECT candidate, custom_commission,employee_commission,tid   FROM public.timesheets_jobs WHERE employee_id = 'Unassigned' ORDER BY candidate")
        sql = cursor.fetchall()
        for row in sql:
            #print(row[0])
            mydict = {"name":row[0],"CC":row[1],"comm":row[2],"tid":row[3]}
            obj.append(mydict)
        #jsoncx = json.dumps(sql,  use_decimal=True)
        jsoncx = json.dumps(sql, cls=JSONEncoder)
        context = {"unnassiged": obj , "dates": obj3}
        #print("QUERY RAN")
        #print(context)
        #print(context)
    elif request.method == 'POST' and 'submit_changes' in request.POST:
        print('Submit started')
        #print(request.POST['9713633082282397545_cons'])
        #print(request.POST)
        tsql = ""
        for itm in request.POST:
            #print(itm[-4:])
            if itm[-4:] == 'cons':
                sql = "UPDATE timesheets_jobs SET employee_id = '" + request.POST[itm]
                con = request.POST[itm]
            if itm[-4:] == 'comm':
                if(request.POST[itm])=='':
                    sql2 = sql + "' ,custom_commission= 'No', employee_commission =get_Commission('" + con + "')"
                else:
                    sql2 = sql + ",custom_commission= 'Yes', employee_commission =" + request.POST[itm]
            if itm[-4:] == 'secc':
                sql3 = sql2 + " ,split_employee= '" + request.POST[itm] + "'"
            if itm[-4:] == 'marg':
                if(request.POST[itm])=='':
                    sql4 = sql3 + ",margins_plit= 0 FROM public.timesheets_jobs t WHERE timesheets_jobs.tid = '" + itm[:-5] + "'"
                else:
                    sql4 = sql3 + ",margins_plit=" + request.POST[itm] +" FROM public.timesheets_jobs t WHERE timesheets_jobs.tid = '" + itm[:-5] + "'"
                print('SQL4:' + sql4)
                cursor.execute(sql4)
                sql = ""
    elif request.method == 'POST' and 'select_month' in request.POST:
        print(request.POST["dt"])
        cursor.execute("truncate table timesheets_month;")
        cursor.execute("insert into timesheets_month (date) VALUES('" + request.POST["dt"] + "')")
        #print(request.POST)



    return render(request, "index.html", context)


def importLatestTimesheets(request):
    return HttpResponse("Timesheets")
    


def splitdict(lst):
    output=[]
    for key_value in lst:
        key, value = key_value.split(': ', 1)
        if not output or key in output[-1]:
            output.append({})
        output[-1][key] = value
    return output


class Statement(TemplateView):
    template_name = 'statement.html'
    def get_context_data(self,*args, **kwargs):
        context = super(Statement, self).get_context_data(*args,**kwargs)
        #context['users'] = Commission.objects.all()
        YD = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        mydir = os.path.join(os.getcwd(), YD)
        print(mydir)
        os.makedirs(mydir)
        employee = exec_sql(summary_data)
        for emp in employee:
            context['summary'] = emp
            context['users'] = Commission.objects.filter(employee_id=emp['employee_id'])
            #print(context)
            open('temp.html', "w").write(render_to_string('statement.html',  context))
            pdf = pdf_export.export_pdf('temp.html', emp['employee_id'] + '.pdf', './'+ YD)
            os.rename(emp['employee_id'] + '.pdf', ""  + YD + '/' + emp['employee_id'] + '.pdf')
        #os.rename("output.csv", ""  + YD + '/' + "data.csv")
        return context

def DisplayStatement(request):
    context = {'statment':'test'}   
    return render(request, "statement.html", context)    


class GeneratePdf(View):
    def get(self, *args, **kwargs):
        #data = Commission.objects.all()
        #context = {'users': data}
        #open('temp.html', "w").write(render_to_string('statement.html',  context))
        pdf = pdf_export.export_pdf('temp.html', 'MATTB.pdf', 'Y')

         # rendering the template
        #doc_pdf = weasyprint.HTML('temp.html').write_pdf('sample.pdf')
        return HttpResponseRedirect('../')



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
