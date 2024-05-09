from django.db import models # type: ignore

# Create your models here.


class e_approval(models.Model):
    Document_no = models.CharField(max_length=20,primary_key=True)
    Department = models.CharField(max_length=100)
    Org_Unit = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    Sub_Category = models.CharField(max_length=100)
    remarks_Subject = models.CharField(max_length=100)
    Priority = models.CharField(max_length=100)
    Tran_No = models.CharField(max_length=100)
    fin_commit = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=100,blank=True,null=True)
    Tolerance = models.CharField(max_length=100)
    Total_Value = models.CharField(max_length=100)
    Attachment = models.CharField(max_length=100)
    date = models.DateField()
    Attachment_details = models.CharField(max_length=100,blank=True,null=True)
    Technician = models.CharField(max_length=100,blank=True,null=True)
    HOD = models.CharField(max_length=100,blank=True,null=True)
    HOD_date = models.CharField(max_length=100,blank=True,null=True)

    GM = models.CharField(max_length=100,blank=True,null=True)
    GM_date = models.CharField(max_length=100,blank=True,null=True)

    vice_principal = models.CharField(max_length=100,blank=True,null=True)
    vice_principal_date = models.CharField(max_length=100,blank=True,null=True)

    principal = models.CharField(max_length=100,blank=True,null=True)
    principal_date = models.CharField(max_length=100,blank=True,null=True)


    def __str__(self):
        return self.Document_no


class User(models.Model):
    Name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=100)
    Department = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)
    conform_Password = models.CharField(max_length=100)

class auth_list(models.Model):
    Document_no = models.CharField(max_length=20, primary_key=True)

    hod = models.CharField(max_length=100, blank=True, null=True)
    hod_date = models.CharField(max_length=100, blank=True, null=True)
    hod_remarks = models.CharField(max_length=100, blank=True, null=True)
    hod_reason = models.CharField(max_length=100, blank=True, null=True)
    hod_clarification = models.CharField(max_length=100, blank=True, null=True)
    
    gm = models.CharField(max_length=100, blank=True, null=True)
    gm_date = models.CharField(max_length=100, blank=True, null=True)
    gm_remarks = models.CharField(max_length=100, blank=True, null=True)
    gm_reason = models.CharField(max_length=100, blank=True, null=True)
    gm_clarification = models.CharField(max_length=100, blank=True, null=True)
    
    vice_principal = models.CharField(max_length=100, blank=True, null=True)
    vice_principal_date = models.CharField(max_length=100, blank=True, null=True)
    vice_principal_remarks = models.CharField(max_length=100, blank=True, null=True)
    vice_principal_reason = models.CharField(max_length=100, blank=True, null=True)
    vice_principal_clarification = models.CharField(max_length=100, blank=True, null=True)
    
    principal = models.CharField(max_length=100, blank=True, null=True)
    principal_date = models.CharField(max_length=100, blank=True, null=True)
    principal_remarks = models.CharField(max_length=100, blank=True, null=True)
    principal_reason = models.CharField(max_length=100, blank=True, null=True)
    principal_clarification = models.CharField(max_length=100, blank=True, null=True)

class clarification(models.Model):
    Document_no = models.CharField(max_length=20, primary_key=True)

    remarks = models.CharField(max_length=500, blank=True, null=True)
    reroute_comments = models.CharField(max_length=500, blank=True, null=True)
    reroute_clarification = models.CharField(max_length=500, blank=True, null=True)

    
