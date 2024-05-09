from django import forms  # type: ignore
from .models import e_approval,User,auth_list
# forms.py
class EApprovalForm(forms.ModelForm):
    class Meta:
        model = e_approval
        fields = [
            'Document_no', 'Department', 'Org_Unit', 'Category', 'Sub_Category',"staff_id",
            'remarks_Subject', 'Priority', 'Tolerance', 'Attachment_details', 'Total_Value',"date","Tran_No","fin_commit","Technician","HOD","HOD_date","GM",
            "GM_date","vice_principal","vice_principal_date","principal","principal_date"
 ]
        exclude=['Document_no',"Tran_No"]

class userform(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'Name', 'user_name', 'staff_id', 'Department', 'email',
            'role', 'Password', 'conform_Password'
 ]


class auth_form(forms.ModelForm):
    class Meta:
        model = auth_list
        fields = [
            'Document_no', 'hod', 'hod_date', 'hod_remarks', 'hod_reason',
            'hod_clarification', 'gm', 'gm_date', 'gm_remarks', 'gm_reason',
            'gm_clarification', 'vice_principal', 'vice_principal_date', 'vice_principal_remarks', 'vice_principal_reason',
            'vice_principal_clarification', 'principal', 'principal_date', 'principal_remarks', 'principal_reason',
            'principal_clarification',
        ]
