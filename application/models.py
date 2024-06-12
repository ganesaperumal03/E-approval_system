from django.db import models #type:ignore


class e_approval(models.Model):
    Document_no = models.CharField(max_length=200,primary_key=True)
    Department = models.CharField(max_length=100)
    Org_Unit = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    Sub_Category = models.CharField(max_length=100)
    remarks_Subject = models.CharField(max_length=100)
    Priority = models.CharField(max_length=100)
    Tran_No = models.CharField(max_length=100)
    fin_commit = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=10,blank=True,null=True)
    Tolerance = models.CharField(max_length=100)
    Total_Value = models.CharField(max_length=100)
    In_words = models.CharField(max_length=200,blank=True,null=True)
    Attachment = models.FileField(upload_to='')
    date = models.DateField()
    Attachment_details = models.CharField(max_length=100,blank=True,null=True)
    Technician = models.CharField(max_length=100,blank=True,null=True)
    Staff = models.CharField(max_length=100,blank=True,null=True)
    Staff_date = models.CharField(max_length=100,blank=True,null=True)
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



    Document_no = models.CharField(max_length=200, primary_key=True)


    staff = models.CharField(max_length=100, blank=True, null=True)
    staff_date = models.CharField(max_length=100, blank=True, null=True)
    staff_remarks = models.CharField(max_length=100, blank=True, null=True)
    staff_reason = models.CharField(max_length=100, blank=True, null=True)
    staff_clarification = models.CharField(max_length=100, blank=True, null=True)

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
    Document_no = models.CharField(max_length=200, primary_key=True)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    reroute_comments = models.CharField(max_length=500, blank=True, null=True)
    reroute_clarification = models.CharField(max_length=500, blank=True, null=True)


class auth_list(models.Model):
    Document_no = models.CharField(max_length=200, primary_key=True)
    auth_approval=models.CharField(max_length=100,blank=True, null=True)
    auth_remarks=models.CharField(max_length=100,blank=True, null=True)
    auth_reason=models.CharField(max_length=100,blank=True,null=True)

class doc_remarks(models.Model):
    Document_no = models.CharField(max_length=100, primary_key=True)
    doc_date_and_time = models.DateField(auto_now_add=True)
    doc_approval_id =models.CharField(max_length=20, blank=True,null=True)
    doc_applied_staff_id =models.CharField(max_length=20, blank=True,null=True)
    doc_subject=models.CharField(max_length=100, blank=True,null=True)
    doc_remarks=models.CharField(max_length=100, blank=True,null=True)
    doc_attachment=models.CharField(max_length=100,blank=True,null=True)
    doc_clarification_status=models.CharField(max_length=100,blank=True,null=True)
    doc_clarifictaions_reason=models.CharField(max_length=100,blank=True,null=True)

class clarification(models.Model):
    Document_no = models.CharField(max_length=200, primary_key=True)
    clarification_approval=models.CharField(max_length=500, blank=True, null=True)
    clarification_date_and_time = models.DateField(auto_now_add=True)
    clarification_remarks = models.CharField(max_length=500, blank=True, null=True)
    clarification_reroute_comments = models.CharField(max_length=500, blank=True, null=True)
    clarification_reroute_clarification = models.CharField(max_length=500, blank=True, null=True)
