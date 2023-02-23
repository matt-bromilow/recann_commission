from django.db import models
from django.forms import UUIDField
from django.utils import timezone
from django.contrib.auth.models import User  

from django.contrib.auth.models import User

class Employee(models.Model):
    POSITION_CHOICES = (
        ('Senior Recruiter', 'senior recruiter'),
        ('Recruiter', 'recruiter'),
        ('Associate', ',associate'),
    )
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee = models.CharField(max_length=250, unique=True, primary_key=True, default=None)
    position = models.CharField(max_length=100, choices=POSITION_CHOICES,default='recruiter')
    employee_commission = models.DecimalField(max_digits=12, decimal_places=4, default=0.075)
    
#JOBS Imported First

class Jobs(models.Model):
    UNIT_CHOICES = (
        ('hour', 'Hour'),
        ('day', 'Day'),
    )

    INVOICED_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )

    date = models.DateField(default=timezone.now)
    candidate = models.CharField(max_length=250, blank=True, null=True)
    company_name = models.CharField(max_length=250, blank=True, null=True)
    job_description = models.CharField(max_length=250, unique=True, primary_key=True, default=None)
    pay_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    charge_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    employee = models.ForeignKey(Employee, to_field='employee', on_delete=models.DO_NOTHING, default=None)
    custom_commission = models.CharField(max_length=10, choices=INVOICED_CHOICES,default='no')
    employee_commission = models.DecimalField(max_digits=12, decimal_places=4, default=0.0)
    margins_plit = models.DecimalField(max_digits=12, decimal_places=4)
    timestamp = models.DateTimeField(default = timezone.now)
    tid = models.CharField(max_length=250, unique=True, default=None, null=True)
    split_employee = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering =('-timestamp',)

    def __str__(self):
        return self.candidate

    


class Timesheets(models.Model):
    UNIT_CHOICES = (
        ('hour', 'Hour'),
        ('day', 'Day'),
    )

    INVOICED_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )
    timesheet_key = models.CharField(max_length=250, unique=True, primary_key=True, default=None)
    date = models.DateField(default=timezone.now)
    #employee_id = models.CharField(max_length=250, blank=True, null=True)
    company_name = models.CharField(max_length=250, blank=True, null=True)
    entry_quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    units = models.CharField(max_length=10, choices=UNIT_CHOICES)
    pay_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    charge_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    employee = models.ForeignKey(Employee, to_field='employee', on_delete=models.DO_NOTHING, default=None)
    employee_commission = models.DecimalField(max_digits=12, decimal_places=4, default=0.05)
    margins_plit = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    pay_currency = models.CharField(max_length=10, blank=True, null=True)
    charge_currency = models.CharField(max_length=10, blank=True, null=True)
    fx_date = models.DateTimeField(null=True)
    invoice_sent = models.CharField(max_length=10, choices=INVOICED_CHOICES,default='no')
    timestamp = models.DateTimeField(default = timezone.now)
    job = models.ForeignKey(Jobs, to_field='job_description', on_delete=models.CASCADE, default=None , null=True)
    commission_processed = models.CharField(max_length=10, choices=INVOICED_CHOICES,default='no') 
    hours = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    gross_pay_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    gross_charge_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1) 
    gross_pay_rate_gbp = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    gross_charge_rate_gbp = models.DecimalField(max_digits=12, decimal_places=4, default=1) 
    margin = models.DecimalField(max_digits=12, decimal_places=4, default=1) 

    class Meta:
        ordering =('-timestamp',)

    def _get_candidate(self):
        cand = Jobs.objects.first()
        return cand.candidate

    def __str__(self):
        return self.timesheet_key

    def _get_cust_comm(self):
        obj = Jobs.objects.first()
        if obj.custom_commission=="Yes":
            comm = obj.employee_commission or 0
        elif obj.custom_commission=="No":
            comm = 100
        
        y=comm
        return y

    candidate = property(_get_candidate)
    comms = property(_get_cust_comm)

class Commission(models.Model):
    job_key = models.ForeignKey(Jobs, to_field='job_description', on_delete=models.CASCADE, default=None)

    candidate_name = models.CharField(max_length=250, blank=True, null=True)
    employee_name = models.CharField(max_length=250, blank=True, null=True)
    #employee_key = models.ForeignKey(Employee, to_field='employee', on_delete=models.CASCADE, default=None)
    candidate_start_date = models.DateTimeField(default=None)
    commission_rate = models.DecimalField(max_digits=12, decimal_places=4, default=0)
  #  commission_gp_per_hour_gbp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_ts_week_commencing = models.DateTimeField(default=None)
    commission_total_hours = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_gp_per_hour_gbp =  models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_pay_rate =  models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_charge_rate =  models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_original_currency = models.CharField(max_length=10, blank=True, null=True)
    commission_charge_currency = models.CharField(max_length=10, blank=True, null=True)
    commission_fx_rate_to_gbp =  models.DecimalField(max_digits=12, decimal_places=4, default=0)
    commission_fx_rate = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    timesheet_key = models.OneToOneField(Timesheets, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, to_field='employee', on_delete=models.DO_NOTHING, default=None)
    #client_key = 

    def _get_gp_total(self):
        return self.commission_total_hours * self.commission_total_hours

    commission_total_gp_gbp = property(_get_gp_total)
    

class mylogs(models.Model):
    timestamp = models.DateTimeField(default = timezone.now)
    description = models.CharField(max_length=8000, blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    userid = models.CharField(max_length=100, blank=True, null=True)

class month(models.Model):
    date = models.DateField()


