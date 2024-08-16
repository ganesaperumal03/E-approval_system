from django import forms #type:ignore
from .models import e_approval,User,auth_list,doc_remarks
# forms.py
class EApprovalForm(forms.ModelForm):
    class Meta:
        model = e_approval
        fields = [
            'Document_no', 'Department', 'Org_Unit', 'Category',"staff_id","Attachment",'Department_code','Head_of_account','remarks_Subject1',
            'remarks_Subject', 'Priority', 'Tolerance', 'sub_category','Attachment_details','Total_Value',"date","Tran_No","fin_commit","Technician","HOD","HOD_date","GM",
            "GM_date","Vice_Principal","Vice_Principal_date","Principal","Principal_date"
 ]
        exclude=['Document_no',"Tran_No","Attachment",'Department_code']
        Attachment = forms.FileField(required=False)

class userform(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'Name', 'user_name', 'staff_id', 'Department', 'email','Department_code',
            'role', 'Password', 'confirm_Password'
 ]
        exclude=['Department_code']

class auth_form(forms.ModelForm):
    class Meta:
        model = auth_list
        fields = [
            'Document_no', 'hod', 'hod_date', 'hod_remarks', 'hod_reason',
            'hod_clarification', 'gm', 'gm_date', 'gm_remarks', 'gm_reason',
            'gm_clarification', 'Vice_Principal', 'Vice_Principal_date', 'Vice_Principal_remarks', 'Vice_Principal_reason',
            'Vice_Principal_clarification', 'Principal', 'Principal_date', 'Principal_remarks', 'Principal_reason',
            'Principal_clarification',
        ]


class doc_remarks_form(forms.ModelForm):
    class Meta:
        model = doc_remarks
        fields = [
            "Document_no","doc_subject","doc_remarks","doc_attachment","doc_approval_id","doc_applied_staff_id"
 ]

class ClarificationUpdateForm(forms.ModelForm):
    class Meta:
        model = e_approval
        fields = [
            'Category',
            'Priority', 'Total_Value', 'fin_commit'
        ]

class DocRemarksUpdateForm(forms.ModelForm):
    class Meta:
        model = doc_remarks
        fields = [
            'doc_clarification_status'
        ]
# l