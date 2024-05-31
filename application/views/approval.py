import re
from django.shortcuts import render, redirect, get_object_or_404  #type:ignore
from datetime import datetime  #type:ignore
from django.contrib.auth import login as auth_login  #type:ignore
from django.contrib.auth import authenticate       #type:ignore
from django.contrib.auth import logout as auth_logout   #type:ignore
from django.shortcuts import render, redirect         #type:ignore
from django.contrib.auth.decorators import login_required     #type:ignore
import os
from django.core.paginator import Paginator    #type:ignore
from django.conf import settings     #type:ignore
from application.form import EApprovalForm,userform,auth_form,doc_remarks_form,DocRemarksUpdateForm,ClarificationUpdateForm    #type:ignore
from application.models import e_approval,User,doc_remarks     #type:ignore
from django.contrib import messages #type:ignore
from django.db.models import Q  #type:ignore
import pandas as pd  
from num2words import num2words   


def save_uploaded_pdfs(file_dict):
    profile_images_directory = os.path.join('media')
    os.makedirs(profile_images_directory, exist_ok=True)

    file_paths = {}

    for field_name, file_obj in file_dict.items():
        base_file_name = f'{field_name}_{file_obj.name}'
        file_path = os.path.join(profile_images_directory, base_file_name)

        # Check if the file already exists, if yes, append a number
        counter = 1
        while os.path.exists(file_path):
            new_file_name = f'{field_name}_{counter}_{file_obj.name}'
            file_path = os.path.join(profile_images_directory, new_file_name)
            counter += 1

        with open(file_path, 'wb') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        file_paths[field_name] = file_path

    return file_paths


# def in_words(Total_Value):
#     p = inflect.engine()
#     In_words= p.number_to_words(Total_Value)
import pandas as pd
from django.shortcuts import render, redirect
from application.form import EApprovalForm
from application.models import e_approval, User
import logging

logger = logging.getLogger(__name__)

def create_form(request):
    # Get user data from session
    user_data = request.session.get('user_data', {})
    staff_id = user_data.get("staff_id")
    name = user_data.get("name")
    department = user_data.get("Department")
    role = user_data.get("role")

    # Read the CSV file
    excel_file_path = 'category.csv'
    try:
        df = pd.read_csv(excel_file_path)
    except pd.errors.EmptyDataError:
        # Handle empty file case
        df = pd.DataFrame(columns=['Sub_category'])
    category = df['Sub_category'].tolist()

    if request.method == 'POST':
        form = EApprovalForm(request.POST)
        if form.is_valid():
            # Get cleaned data
            department = form.cleaned_data['Department']
            category = form.cleaned_data['Category']
            sub_category = form.cleaned_data['Sub_Category']
            
            # Calculate counts
            count = e_approval.objects.count() + 1
            tran_count = e_approval.objects.filter(Department=department).count() + 1
            
            # Format counts with leading zeros
            count_no = f"{count:05d}"
            tran_count_no = f"{tran_count:05d}"
            
            # Construct document and transaction numbers
            doc_no = f'rit/ac{department}/{category}/{sub_category}/{count_no}'
            tran_no = f'rit/ac{department}/{category}/{sub_category}/{tran_count_no}'

            # Get staff user
            staff = User.objects.get(staff_id=staff_id)
            
            # Save the form without committing to the database
            user = form.save(commit=False)
            user.staff_id = staff_id
            user.Document_no = doc_no
            user.Tran_No = tran_no
            
            # Save uploaded PDFs
            file_paths = save_uploaded_pdfs(request.FILES)
            user.Attachment = file_paths.get('Attachment')
            
            # Set approval statuses based on the role
            pending_roles = {
                'Technician': ['staff', 'HOD', 'GM', 'vice_principal', 'principal'],
                'Staff': ['HOD', 'GM', 'vice_principal', 'principal'],
                'HOD': ['GM', 'vice_principal', 'principal'],
                'office': ['GM', 'vice_principal', 'principal'],
                'GM': ['vice_principal', 'principal'],
                'vice_principal': ['principal'],
                'Principal': []
            }
            for pending_role in pending_roles.get(role, []):
                setattr(user, pending_role, 'Pending')

            # Save the user
            user.save()
            return redirect('create_form')  # Redirect to a success page
        else:
            # Handle form errors
            return render(request, "e-approval/error.html", {
                'form': form,
                "category": category,
                "role": role,
                "Department": department,
                "Name": name
            })
    else:
        form = EApprovalForm()
        staff_user = User.objects.get(staff_id=staff_id)
        department = staff_user.Department
        role = staff_user.role
        role_list = ['Technician', 'office', 'Staff', 'HOD', 'GM', 'vice_principal', 'Principal']
        
        # Get the index of the current role
        ia = role_list.index(role)
        
        approval_user = []
        
        for next_role in role_list[ia+1:]:
            approver = User.objects.filter(role=next_role)
            if next_role in ['Staff', 'HOD']:
                approver = approver.filter(Department=department)
            approval_user.append(approver.first())

        # Filter out None values if any role does not have a user
        approval_user = [user for user in approval_user if user is not None]
        
        return render(request, "e-approval/index.html", {
            'form': form,
            "approval_user": approval_user,
            "category": category,
            "role": role,
            "Department": department,
            "Name": name
        })


def encrypt_password(raw_password):
    # Implement your password encryption algorithm (e.g., using hashlib)
    import hashlib
    return hashlib.sha256(raw_password.encode()).hexdigest()


def signup(request):
    if request.method == 'POST':
        form = userform(request.POST)
        if form.is_valid():
            password = form.cleaned_data['Password']
            confirm_password = form.cleaned_data['confirm_Password']

            if password == confirm_password:
                encrypted_password = encrypt_password(password)

                # Save the encrypted password to your user model
                user = form.save(commit=False)  # Don't save the form yet
                user.Password = encrypted_password
                user.confirm_Password = encrypted_password

                user.save()

                # Redirect to a success page or login page
                return redirect('login')
            else:
                # Passwords don't match, return an error
                form.add_error('confirm_password', 'Passwords do not match')
                return render(request, "auth/signup.html", {'form': form})
        else:
            return render(request, "e-approval/error.html", {'form': form})
    else:
        form = userform()

    return render(request, "auth/signup.html", {'form': form})


def login(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        password = request.POST.get('password')
        print(staff_id,password)
        # Fetch the user from the database
        try:
            user = User.objects.get(staff_id=staff_id)
        except User.DoesNotExist:
            # User not found, show an error message
            error_message = 'Invalid staff_id or password.'
            return render(request, "auth/login.html", {'error_message': error_message})

        # Check if the password matches
        if user.Password == encrypt_password(password):
            name=user.Name
            # Passwords match, log in the user
            # Set session variables or use Django's login system as needed
            request.session['user_id'] = user.id
            user = get_object_or_404(User, staff_id=staff_id)
            user_dict = {
            'id': user.id,
            'staff_id': user.staff_id,
            'name': user.Name,
            'user_name': user.user_name,
            'Department' : user.Department,
            'email' : user.email,
            'role' : user.role,
            'Password' : user.Password,
            'confirm_Password' : user.confirm_Password           }
            
            request.session['user_data'] = user_dict

            return redirect('create_form')
        else:
            # Passwords don't match, show an error message
            error_message = 'Invalid username or password.'
            return render(request, "auth/login.html", {'error_message': error_message})
    else:
        return render(request, "auth/login.html")
def logout(request):
    print('logout function called')
    auth_logout(request)
    messages.success(request,'You were logged out')
    request.session.flush()  # Flush all session data
    return render(request, "auth/login.html")

# #def auth_approval(request):
# #    staff_id = e_approval.objects.filter(staff_id=567654)
# #    Document_no = request.GET.get('Document_no')
# #    print(Document_no,'89')
# #    if Document_no:
# #        Document_no = e_approval.objects.get(Document_no=Document_no)
# #        staff_id=Document_no.staff_id
# #        gm=Document_no.GM
# #        vice_prinicipal=Document_no.vice_principal
# #        prinicipal=Document_no.principal
# #        if gm=='pending':
# #            auth_staff_id = User.objects.get(staff_id=staff_id)
# #        print(Document_no)
# #        gm = User.objects.get(role='GM')
# #        vice_principal = User.objects.get(role='vice_principal')
# #        principal = User.objects.get(role='Principal')
#
# #        if Document_no:
# #            print(Document_no)
# #            return render(request, "e-approval/auth_approval.html",{"Document_no":Document_no,"gm":gm,"vice_principal":vice_principal,"principal":principal})
#
# #        return render(request, "e-approval/auth_approval.html",{"Document_no":Document_no})
# #    return render(request, "e-approval/auth_approval.html",{"staff_id":staff_id})


def auth_approval(request):

# Convert a number to words

    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    staff_id=user_data['staff_id']

    if request.method == 'POST':
        form = doc_remarks_form(request.POST)

        if form.is_valid():
            Document_no = form.cleaned_data['Document_no']

            # Get the current date and time in the desired format
            date_time = datetime.now().strftime("%d%m%y%H%M")

            # Combine the document number and date-time string
            doc_no = f"{Document_no}@{date_time}"


            # Save the form data to the database
            user = form.save(commit=False)

            # Assuming 'user_data' is a dictionary containing user information
            user.doc_approval_id = user_data.get('staff_id')  # Use 'get' to avoid KeyError
            user.Document_no = doc_no
            user.doc_clarification_status = 'Pending'

            user.save()
        else:
            return render(request, "e-approval/error.html", {'form': form})


    Document_no = request.GET.get('Document_no')

    if Document_no:
        role=staff_role
        role_list = ['Staff','HOD','GM','vice_principal','Principal']
        ia = role_list.index(role)
        approval_user = []
        date=None

        auth_list = e_approval.objects.filter(Document_no=Document_no)
        
       
        for i,j in enumerate(auth_list):
            if j.Staff!='Pending':
                approval_user.append({"date":j.Staff_date,'Approval':'Staff',
                'remarks':j.Staff})

            if j.HOD!='Pending':
                approval_user.append({"date":j.HOD_date,'Approval':'HOD',
                'remarks':j.HOD})
            if j.GM!='Pending':
                approval_user.append({"date":j.GM_date,'Approval':'GM',
                'remarks':j.GM})
            if j.vice_principal!='Pending':
                approval_user.append({"date":j.vice_principal_date,'Approval':'vice_principal',
                'remarks':j.vice_principal})
            if j.principal!='Pending':
                approval_user.append({"date":j.principal_date,'Approval':'principal',
                'remarks':j.principal})
        
        document_data = e_approval.objects.get(Document_no=Document_no)
        print(document_data,"************")
        number = document_data.Total_Value
        number_in_words = num2words(number)
        print(number_in_words)
        return render(request, "e-approval/auth_approval.html",{"Document_no":document_data,"approval_user":approval_user,"doc":Document_no,"Name":name,"role":staff_role,"department":department,"number_in_words":number_in_words,"doc_data":doc_data})


    user_data=request.session.get('user_data', {})
    
    def filtere(user_data):
        global doc_data 
        doc_data=[]
        if user_data['role'] == 'Staff':
            print('Staff-----------------------------')
            technicians = User.objects.filter(Department=user_data['Department'], role__in=['Technician'])
            for technician in technicians:
                approvals = e_approval.objects.filter(staff_id=technician.staff_id ,Staff = 'Pending',HOD = 'Pending',GM='Pending',vice_principal='Pending',principal='Pending')
                print('Staff2-----------------------------')

                if  approvals:
                    print('Staff3-----------------------------')

                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)
        elif user_data['role'] == 'HOD':
            technicians = User.objects.filter(Department=user_data['Department'], role__in=['Technician'])
            for technician in technicians:
                approvals = e_approval.objects.exclude(Staff='Pending').filter(staff_id=technician.staff_id ,HOD = 'Pending',GM='Pending',vice_principal='Pending',principal='Pending')

                if  approvals:
                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)
        elif user_data['role'] == 'GM':
            technicians = User.objects.filter(
                role__in=['Technician','HOD','office']  # Use role__in for multiple roles
            )

            for technician in technicians:
                approvals = e_approval.objects.exclude(Staff='Pending',HOD='Pending').filter(staff_id=technician.staff_id,GM='Pending',vice_principal='Pending',principal='Pending')

                if  approvals:
                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)


        elif user_data['role'] == 'vice_principal':
            technicians = User.objects.filter(
                role__in=['Technician', 'GM','HOD','office']  # Use role__in for multiple roles
            )

            for technician in technicians:
                approvals = e_approval.objects.exclude(Staff='Pending',HOD='Pending',GM='Pending').filter(staff_id=technician.staff_id,vice_principal='Pending',principal='Pending')

                if  approvals:
                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)


        elif user_data['role'] == 'Principal':
            technicians = User.objects.filter(
                role__in=['Technician', 'GM', 'vice_principal','HOD','office']  # Use role__in for multiple roles
            )
            print('principal',technicians)
            for technician in technicians:
                approvals = e_approval.objects.exclude(Staff='Pending',HOD='Pending',GM='Pending',vice_principal='Pending').filter(staff_id=technician.staff_id ,principal='Pending')
                print(approvals)
                if  approvals:
                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)
    filtere(user_data)
    if request.method == 'POST':
        form = auth_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = staff.role
    return render(request, "e-approval/auth_approval.html",{"doc_data":doc_data,"Name":name,"role":staff_role,"department":department})

doc_no = None # Declare the global variable outside the function

def clarification(request):
    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    user_name=user_data["user_name"]

    document_data_value = request.GET.get('document_data_value')
    if document_data_value:
        key, value = document_data_value.split('|')
        doc_no = value  # Update the global variable value

        document_data = e_approval.objects.get(Document_no= value)

        print("******************************************")

        remarks_document_data = doc_remarks.objects.get(Document_no=key, doc_clarification_status='Pending')
        document_data_list = doc_remarks.objects.filter(doc_applied_staff_id=user_data['staff_id'], doc_clarification_status='Pending')


        return render(request, "e-approval/clarification.html", {"document_data": document_data,"remarks_document_data":remarks_document_data,"Name":name,"user_name":user_name,"role":staff_role,"department":department})


    
    user_data = request.session.get('user_data', {})
    doc_data={}    
    document_data_list = doc_remarks.objects.filter(doc_applied_staff_id=user_data['staff_id'], doc_clarification_status='Pending') 
    print("__________________________________________")
    for doc in document_data_list:
        pattern = r"^(.*?)@"
        match = re.search(pattern, doc.Document_no)
        if match:
            document_data_value = match.group(1)
            doc_data[doc.Document_no] = document_data_value
    return render(request, "e-approval/clarification.html", {"document_data_value": doc_data,"Name":name,"role":staff_role,"user_name":user_name,"department":department,"document_data_list":document_data_list})
    
    



def approval_user_details(request):
    return render(request, "e-approval/approval_user_details.html")


def updateapproval(request):
    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    user_name=user_data["user_name"]
    print(user_name)

    if request.method == 'POST':

        Priority = request.POST.get('Priority')
        Document_no = request.POST.get('Document_no')
        remarks_Document_no = request.POST.get('remarks_document_data')

        Category = request.POST.get('Category')
        Sub_Category = request.POST.get('Sub_Category')
        fin_commit = request.POST.get('fin_commit')
        Total_Value = request.POST.get('Total_Value')
        doc_clarifictaions_reason = request.POST.get('doc_clarifictaions_reason')
        file_paths = save_uploaded_pdfs(request.FILES)
        approval_data = get_object_or_404(e_approval,Document_no=Document_no)
        doc_data = get_object_or_404(doc_remarks,Document_no=remarks_Document_no)
        approval_data.Priority = Priority
        approval_data.Category = Category
        approval_data.Sub_Category = Sub_Category
        approval_data.fin_commit = fin_commit
        approval_data.Total_Value = Total_Value
        approval_data.Attachment = file_paths.get('Attachment')

        approval_data.save()

        doc_data.doc_clarifictaions_reason = doc_clarifictaions_reason
        doc_data.doc_clarification_status = 'verified'
        doc_data.save()

        # if docremarksform.is_valid():
        #     doc_data.doc_clarifictaions_reason = doc_clarifictaions_reason
        #     doc_data.doc_clarification_status = doc_clarification_status
        #     DocRemarksUpdateForm.save()

        return redirect('clarification')
    return render(request, "e-approval/clarification.html",{"Name":name,"role":staff_role,"department":department,"user_name":user_name})




def form_approval(request):
    approval_Remarks = request.POST.get('approval_Remarks')
    Document_no = request.POST.get('Document_no')
    now = datetime.now()
    print("dsd------------------------------------------------------------")

    # Format the date and time as a string
    current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    approval_Reason = request.POST.get('approval_Reason')
    print(approval_Remarks,Document_no,approval_Reason)
    user_data=request.session.get('user_data', {})
    role=user_data["role"]
    approval_data = get_object_or_404(e_approval,Document_no=Document_no)

    if approval_Remarks and role=='Staff':
        approval_data.Staff = approval_Remarks
        approval_data.Staff_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='HOD':
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='GM':
        approval_data.GM = approval_Remarks
        approval_data.GM_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='vice_principal':
        approval_data.vice_principal = approval_Remarks
        approval_data.vice_principal_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='Principal':
        approval_data.principal = approval_Remarks
        approval_data.principal_date = current_date_time
        approval_data.save()
    
    if approval_Reason and role=='Staff':
        approval_data.Staff = approval_Reason
        approval_data.Staff_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='HOD':
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='GM':
        approval_data.GM = approval_Reason
        approval_data.GM_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='vice_principal':
        approval_data.principal = approval_Reason
        approval_data.vice_principal_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='Principal':
        approval_data.principal = approval_Reason
        approval_data.principal_date = current_date_time
        approval_data.save()

    return render(request, "e-approval/auth_approval.html")


def view_approval(request):
    Tran_No = request.GET.get('Tran_No')
    user_data=request.session.get('user_data', {})
    role=user_data['role']
    Department=user_data['Department']
    staff_id=user_data['staff_id']
    name=user_data["name"]

    approval_user = []
    date=None

    role_list = ['Staff','HOD','GM','vice_principal','Principal']
    approval_user = []
    date=None

    auth_list = e_approval.objects.filter(Document_no=Tran_No)
    for i,j in enumerate(auth_list):
        if j.Staff!='Pending':
            approval_user.append({"date":j.Staff_date,'Approval':'Staff',
            'user':User.objects.filter(Department=Department, role='Staff').first()})
        if j.HOD!='Pending':
            approval_user.append({"date":j.HOD_date,'Approval':'HOD',
            'user':User.objects.filter(Department=Department, role='HOD').first()})
        if j.GM!='Pending':
            approval_user.append({"date":j.GM_date,'Approval':'GM',
            'user':User.objects.filter( role='GM').first()})
        if j.vice_principal!='Pending':
            approval_user.append({"date":j.vice_principal_date,'Approval':'vice_principal',
            'user':User.objects.filter( role='vice_principal').first()})
        if j.principal!='Pending':
            approval_user.append({"date":j.principal_date,'Approval':'principal',
            'user':User.objects.filter( role='principal').first()})
    if Tran_No:
        Tran_No = e_approval.objects.get(Tran_No=Tran_No)
        tran_no=e_approval.objects.filter(staff_id=staff_id)
        print(tran_no,'!-------------------------!')
        return render(request, "e-approval/view_approval.html",{"Tran_No":Tran_No,"approval_user":approval_user,"Name":name,"role":role,"department":Department,"tran_no":tran_no})

    doc_data=[]
    tran_no=e_approval.objects.filter(staff_id=staff_id)
    print(tran_no,'-------------------------')
    return render(request, "e-approval/view_approval.html",{"tran_no":tran_no,"Name":name,"role":role,"department":Department})



from django.shortcuts import HttpResponse #type:ignore
from django.core.exceptions import ObjectDoesNotExist #type:ignore

import logging

logger = logging.getLogger(__name__)

def pdf_show(request,Tran_No):
    if Tran_No:
        print(Tran_No)

        pdf = get_object_or_404(e_approval,Tran_No=Tran_No)
        print(pdf)
        
        pdf_paths = pdf.Attachment
        pdf_path=str(pdf_paths)
        print(pdf_path,'--------------------------------------')

    if pdf_path:
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{pdf.Attachment.name}"'
                return response
        else:
            return HttpResponse("PDF not found.")


from django.shortcuts import HttpResponse #type:ignore
from django.core.mail import send_mail #type:ignore

def send_email(request):
    subject = 'Hello from Django'
    message = 'This is a test email sent from Django.'
    recipient_list = ['953621243053@ritrjpm.ac.in']  # Replace with the recipient's email address

    send_mail(subject, message, 'ganeshperumal256@gmail.com', recipient_list)
    return HttpResponse('Email sent successfully.')



from django.http import JsonResponse #type:ignore
from django.views.decorators.csrf import csrf_exempt #type:ignore
from django.shortcuts import render #type:ignore
import json

@csrf_exempt
def process_department(request):
    user_data=request.session.get('user_data', {})
    role=user_data['role']
    Department=user_data['Department']
    name=user_data["name"]
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_department = data.get('department')
            # print('---------------------------------', selected_department)
            # Render the new template and return the HTML content
            return render(request, "e-approval/view_approval.html",{"Name":name,"role":role,"department":Department})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def pdf(request):
    return render(request, "e-approval/pdf.html")


from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO  # Add this import statement
import os

def generate_pdf(request,Tran_No):
    print(Tran_No)
    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()
    Document_no = e_approval.objects.get(Tran_No=Tran_No)

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Draw the content on the PDF
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(175, height - 50, "Ramco Institute of Technology")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(245, height - 80, "E-approval")
    p.drawString(50, height - 330, "Approval List")

    # Labels
    p.setFont("Times-Bold", 13)
    
    p.drawString(70, height - 120, "Department :")
    p.line(140, height - 125, 550, height - 125)
    p.drawString(70, height - 150, "Trans NO ")
    p.rect(140,height - 155, 150, 20)
    p.drawString(70, height - 180, "Category ")
    p.drawString(140, height - 180, ":")
    p.line(140, height - 185, 300, height - 185)
    p.drawString(70, height - 210, "Subject ")
    p.drawString(140, height - 210, ":")
    p.line(140, height - 215, 300, height - 215)
    p.drawString(70, height - 240, "Remarks ")
    p.drawString(140, height - 240, ":")
    p.line(140, height - 245, 300, height - 245)
    p.drawString(70, height - 300, "Amount (INR) ")
    p.drawString(155, height - 300, ":")
    p.line(160, height - 305, 300, height - 305)

    p.drawString(145, height - 120, Document_no.Department)
    p.drawString(145, height - 150, Document_no.Tran_No)
    p.drawString(145, height - 180, Document_no.Category)
    p.drawString(405, height - 180, Document_no.Sub_Category)
    p.drawString(145, height - 210, Document_no.remarks_Subject)
    p.drawString(160, height - 300, Document_no.Total_Value)
    p.drawString(405, height - 120, Document_no.Document_no)
    # p.drawString(150, height - 120, Document_no.Department)
    

    
    

    p.drawString(320, height - 150, "Doc NO ")
    p.rect(400,height - 155, 150, 20)
    p.drawString(320, height - 180, "Sub-category ")
    p.drawString(400, height - 180, ":")
    p.line(400, height - 185, 550, height - 185)

    # Approval List Table
    p.setFont("Courier-Bold", 14)
    p.drawString(60, height - 360, "Name")
    p.drawString(210, height - 360, "Role")
    p.drawString(360, height - 360, "Date")
    p.drawString(60, height - 390, "Name")
    p.drawString(210, height - 390, Document_no.Document_no)
    p.drawString(360, height - 390, Document_no.Document_no)
    p.drawString(60, height - 420, "Name")
    p.drawString(210, height - 420, Document_no.Document_no)
    p.drawString(360, height - 420, Document_no.Document_no)
    p.drawString(60, height - 450, "Name")
    p.drawString(210, height - 450, Document_no.Document_no)
    p.drawString(360, height - 450, Document_no.Document_no)
    p.drawString(60, height - 360, "Name")
    p.drawString(210, height - 360, Document_no.Document_no)
    p.drawString(360, height - 360, Document_no.Document_no)

    # Draw table lines
    p.line(50, height - 340, 550, height - 340)
    p.line(50, height - 370, 550, height - 370)
    p.line(50, height - 400, 550, height - 400)
    p.line(50, height - 430, 550, height - 430)
    p.line(50, height - 460, 550, height - 460)
    p.line(50, height - 490, 550, height - 490)

    p.line(50, height - 340, 50, height - 490)
    p.line(200, height - 340, 200, height - 490)
    p.line(350, height - 340, 350, height - 490)
    p.line(550, height - 340, 550, height - 490)

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "Created by E-approval System")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="e_approval.pdf"'
    response.write(pdf)
    return response
