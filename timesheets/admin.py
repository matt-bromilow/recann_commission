from csv import list_dialects
from django.contrib import admin
from .models import Timesheets, Jobs, Employee, Commission
from import_export import resources
from import_export.admin import ImportExportModelAdmin



@admin.action(description='Set to Invoiced')
def set_invoiced(modeladmin, request, queryset):
    queryset.update(invoice_sent='yes')

@admin.action(description='Generate Commissions')
def set_commission(modeladmin, request, queryset):
    queryset.update(commission_processed='yes')


class TimesheetResource(resources.ModelResource):
    class Meta:
        model = Timesheets
        import_id_fields = ('timesheet_key', )
        exclude = ('id',)
        fields = ('date',	'job',	'company_name',	'entry_quantity',	'units',	'pay_rate',	'charge_rate',	'employee',	'margins_plit',	'pay_currency',	'pay_currency_fx',	'charge_currency',	'charge_currency_fx',	'hours',	'gross_pay_rate',	'gross_charge_rate',	'gross_pay_rate_gbp',	'gross_charge_rate_gbp',	'margin',	'timesheet_key')
        def cust_comm(self, obj):
            return obj.job.custom_commission


class JobsResource(resources.ModelResource):
    class Meta:
        model = Jobs
        exclude = ('id',)
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('job_description', )#changed from candiate
        fields = ('job_description','candidate','date',		'company_name',	'pay_rate',	'charge_rate',	'employee',	'custom_commission',	'employee_commission',	'margins_plit', 'split_employee')
            
class TimesheetAdmin(ImportExportModelAdmin):
    resource_class = TimesheetResource
    list_display = ('job','commission_processed','employee', 'date','invoice_sent', 'company_name','comms')
    list_filter = ('employee', 'date','invoice_sent', 'company_name')
    search_fields = ('employee', 'company_name')
    date_hierarchy = 'date'
    ordering = ('date', 'employee')
    read_only_fields = ('candidate', 'comms')
    actions = [set_invoiced,set_commission]
    
    @admin.display(description='Custom Commission')
    def cust_comm(self, obj):
        if obj.job.custom_commission=="Yes":
            comm = obj.job.employee_commission or 10
        elif obj.job.custom_commission=="no":
            comm = 100
        return comm


admin.site.register(Timesheets, TimesheetAdmin)


class Job_Admin(ImportExportModelAdmin):
    resource_class=JobsResource
    list_display = ('candidate','company_name',  'date',  'employee', 'pay_rate', 'charge_rate', 'employee_commission')
    list_filter = ('candidate',  'company_name' ,'date')
    search_fields = ('candidate', 'company_name')
    date_hierarchy = 'date'
    ordering = ('date', 'employee')    

admin.site.register(Jobs, Job_Admin)

@admin.register(Employee)
class Employee_Admin(admin.ModelAdmin):
    list_display = ('employee','position',  'employee_commission')
    list_filter = ('employee',  'position')
    search_fields = ('employee', 'position')
    ordering = ('employee', 'employee_commission')  


@admin.register(Commission)
class Employee_Admin(admin.ModelAdmin):
    list_display = ('employee_name','candidate_name',  'commission_total_hours', 'commission_gp_per_hour_gbp', 'commission_total_gp_gbp')
    read_only_fields = ('commission_total_gp_gbp')