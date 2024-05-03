from django import forms
from .models import e_approval,User
# forms.py
class EApprovalForm(forms.ModelForm):
    class Meta:
        model = e_approval
        fields = [
            'Document_no', 'Department', 'Org_Unit', 'Category', 'Sub_Category',"staff_id",
            'remarks_Subject', 'Priority', 'Tolerance', 'Attachment_details', 'Total_Value',"date","Tran_No","fin_commit","Technician","HOD","HOD_date","GM",
            "GM_date","vise_principal","vise_principal_date","principal","principal_date"
 ]

class userform(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'Name', 'user_name', 'staff_id', 'Department', 'email',
            'role', 'Password', 'conform_Password'
 ]
