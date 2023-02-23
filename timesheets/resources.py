from import_export import resources
from .models import Timesheets, Jobs, Employee, Commission

class JobsResource(resources.ModelResource):

    def skip_row(self, instance, original):
        check=[]
        new=Jobs.objects.all()
        for p in new:
            check.append(p.candidate)
        if instance.candidate in check:
            return True
        else:
            print("no")
            return False
    class Meta:
        model = Jobs
        exclude = ('id',)
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('job_description', )#changed from candiate
        fields = ('job_description','candidate','date',		'company_name',	'pay_rate',	'charge_rate',	'employee',	'custom_commission',	'employee_commission',	'margins_plit','tid', 'split_employee')
        

class TimesheetResource(resources.ModelResource):
    class Meta:
        model = Timesheets
        import_id_fields = ('timesheet_key', )
        exclude = ('id',)
        fields = ('date',	'job',	'company_name',	'entry_quantity',	'units',	'pay_rate',	'charge_rate',	'employee',	'margins_plit',	'pay_currency',	'pay_currency_fx',	'charge_currency',	'charge_currency_fx',	'hours',	'gross_pay_rate',	'gross_charge_rate',	'gross_pay_rate_gbp',	'gross_charge_rate_gbp',	'margin',	'timesheet_key')
        def cust_comm(self, obj):
            return obj.job.custom_commission