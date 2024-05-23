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
def create_form(request):
    user_data=request.session.get('user_data', {})
    staff_id=user_data["staff_id"]
    Name=user_data["name"]
    Department=user_data["Department"]
    role=user_data["role"]


    excel_file_path = 'category.csv'
    # Read the Excel file
    try:
        df = pd.read_csv(excel_file_path)
    except pd.errors.EmptyDataError:
        # Handle the case where the Excel file is empty
        df = pd.DataFrame(columns=['Sub_category'])
    category = df['Sub_category'].tolist()
    if request.method == 'POST':
        form = EApprovalForm(request.POST)
        if form.is_valid():
            Department = form.cleaned_data['Department']
            Category = form.cleaned_data['Category']
            Sub_Category = form.cleaned_data['Sub_Category']
            # Calculate count and format as strings with leading zeros
            count = e_approval.objects.count() + 1
            print(count)
            count_no = f"{count:05d}"
            tran_count = e_approval.objects.filter(Department=Department).count() + 1
            tran_count_no = f"{tran_count:05d}"

            # Construct document and transaction numbers
            doc_no = f'rit/ac{Department}/{Category}/{Sub_Category}/{count_no}'
            tran_no = f'rit/ac{Department}/{Category}/{Sub_Category}/{tran_count_no}'
            staff = User.objects.get(staff_id=staff_id)
            user = form.save(commit=False)
            role = staff.role
            user.staff_id = staff_id
            user.Document_no = doc_no
            user.Tran_No = tran_no
            file_paths = save_uploaded_pdfs(request.FILES)
            print(".......................................................",file_paths.get('Attachment'))
            user.Attachment = file_paths.get('Attachment')
            # Set approval status based on role
            if role == 'Technician':
                user.Technician = None
                user.HOD = 'Pending'
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'HOD':
                user.Technician = None
                user.HOD = None
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'GM':
                user.Technician = None
                user.HOD = None
                user.GM = None
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'vice_principal':
                user.Technician = None
                user.HOD = None
                user.GM = None
                user.vice_principal = None
                user.principal = 'Pending'

            user.save()
            return redirect('create_form')  # Redirect to a success page
        else:
            return render(request, "e-approval/error.html", {'form': form,"category":category,"role":role,"Department":Department,"Name":Name})
    else:
        form = EApprovalForm()
        staff_user = User.objects.get(staff_id=staff_id)
        department=staff_user.Department
        role=staff_user.role
        role_list = ['Technician','HOD','GM','vice_principal','Principal']
        ia = role_list.index(role)
        print(department,role,ia)
        approval_user = []
        for i in role_list[ia+1:]:
            print(i)
            if i == "HOD":
                approval_user.append(User.objects.filter(Department=department, role=i).first())  # Use .first() to get the first object or None
            elif i == "GM":
                approval_user.append(User.objects.filter(role=i).first())
            elif i == "vice_principal":
                approval_user.append(User.objects.filter(role=i).first())
            elif i == "Principal":
                approval_user.append(User.objects.filter(role=i).first())
            # return render(request, "e-approval/index.html", {'form': form, 'gm_user': gm_user, 'vice_principal_user': vice_principal_user,
            #                                                 'principal_user': principal_user, 'HOD': HOD_user
            #                                              })
        return render(request, "e-approval/index.html", {'form': form, "approval_user":approval_user,"category":category,"role":role,"Department":Department,"Name":Name
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
def auth_approval_list():
    pass
def auth_approval(request):
    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]

    print('yhjgjhghj',user_data['role'])
    if request.method == 'POST':
        form = doc_remarks_form(request.POST)

        if form.is_valid():
            Document_no = form.cleaned_data['Document_no']

            # Get the current date and time in the desired format
            date_time = datetime.now().strftime("%d%m%y%H%M")

            # Combine the document number and date-time string
            doc_no = f"{Document_no}@{date_time}"
            print(doc_no)

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
        role_list = ['HOD','GM','vice_principal','Principal']
        ia = role_list.index(role)
        print(department,role,ia)
        approval_user = []
        date=None

        auth_list = e_approval.objects.filter(Document_no=Document_no)
        for i,j in enumerate(auth_list):
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
        return render(request, "e-approval/auth_approval.html",{"Document_no":document_data,"approval_user":approval_user,"doc":Document_no,"Name":name,"role":staff_role,"department":department})


    user_data=request.session.get('user_data', {})
    print('yhjgjhghj',user_data['role'])
    doc_data=[]
    if user_data['role'] == 'HOD':
        print('hojkkhjjhj')
        technicians = User.objects.filter(Department=user_data['Department'], role__in=['Technician'])
        for technician in technicians:
            approvals = e_approval.objects.filter(staff_id=technician.staff_id ,HOD = 'Pending',GM='Pending',vice_principal='Pending',principal='Pending')

            if  approvals:
                print('hojkkhjjhj')

                for approval in approvals:  # Iterate through the queryset
                    staff = User.objects.filter(staff_id=approval.staff_id).first()
                    approval.staff_name = staff.Name
                    doc_data.append(approval)
    elif user_data['role'] == 'GM':
        technicians = User.objects.filter(
            role__in=['Technician','HOD']  # Use role__in for multiple roles
         )

        for technician in technicians:
            approvals = e_approval.objects.exclude(HOD='Pending').filter(staff_id=technician.staff_id,GM='Pending',vice_principal='Pending',principal='Pending')

            if  approvals:
                for approval in approvals:  # Iterate through the queryset
                    staff = User.objects.filter(staff_id=approval.staff_id).first()
                    approval.staff_name = staff.Name
                    doc_data.append(approval)


    elif user_data['role'] == 'vice_principal':
        technicians = User.objects.filter(
            role__in=['Technician', 'GM','HOD']  # Use role__in for multiple roles
         )

        for technician in technicians:
            approvals = e_approval.objects.exclude(HOD='Pending',GM='Pending').filter(staff_id=technician.staff_id,vice_principal='Pending',principal='Pending')

            if  approvals:
                for approval in approvals:  # Iterate through the queryset
                    staff = User.objects.filter(staff_id=approval.staff_id).first()
                    approval.staff_name = staff.Name
                    doc_data.append(approval)


    elif user_data['role'] == 'Principal':
        technicians = User.objects.filter(
            role__in=['Technician', 'GM', 'vice_principal','HOD']  # Use role__in for multiple roles
         )
        print('principal',technicians)
        for technician in technicians:
            approvals = e_approval.objects.exclude(HOD='Pending',GM='Pending',vice_principal='Pending').filter(staff_id=technician.staff_id ,principal='Pending')
            print(approvals)
            if  approvals:
                for approval in approvals:  # Iterate through the queryset
                    staff = User.objects.filter(staff_id=approval.staff_id).first()
                    approval.staff_name = staff.Name
                    doc_data.append(approval)
    print('doc_data',doc_data)
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

    document_data_value = request.GET.get('document_data_value')

    if document_data_value:
        key, value = document_data_value.split('|')
        doc_no = value  # Update the global variable value
        # Now you can use key and value as needed
        print("Key:", key)
        print("Value:", value)
        document_data = e_approval.objects.get(Document_no= value)
        remarks_document_data = doc_remarks.objects.get(Document_no=key, doc_clarification_status='Pending')

        print(document_data)
        return render(request, "e-approval/clarification.html", {"document_data": document_data,"remarks_document_data":remarks_document_data,"Name":name,"role":staff_role,"department":department})


    doc_data = {}
    user_data = request.session.get('user_data', {})
    document_data_list = doc_remarks.objects.filter(doc_applied_staff_id=user_data['staff_id'], doc_clarification_status='Pending')
    for doc in document_data_list:
        pattern = r"^(.*?)@"
        match = re.search(pattern, doc.Document_no)
        if match:
            document_data_value = match.group(1)
            doc_data[doc.Document_no] = document_data_value
    print(doc_data)
    return render(request, "e-approval/clarification.html", {"document_data_value": doc_data,"Name":name,"role":staff_role,"department":department})



def approval_user_details(request):
    return render(request, "e-approval/approval_user_details.html")


def updateapproval(request):
    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    print("ghkuvhgujkhnjk-1")

    if request.method == 'POST':

        Priority = request.POST.get('Priority')
        Document_no = request.POST.get('Document_no')
        remarks_Document_no = request.POST.get('remarks_document_data')
        print(Document_no,remarks_Document_no)

        Category = request.POST.get('Category')
        Sub_Category = request.POST.get('Sub_Category')
        fin_commit = request.POST.get('fin_commit')
        Total_Value = request.POST.get('Total_Value')
        doc_clarifictaions_reason = request.POST.get('doc_clarifictaions_reason')
        print(Category,Sub_Category,fin_commit,Total_Value,doc_clarifictaions_reason)

        approval_data = get_object_or_404(e_approval,Document_no=Document_no)
        doc_data = get_object_or_404(doc_remarks,Document_no=remarks_Document_no)


        clarificationform = ClarificationUpdateForm(request.GET,instance=approval_data)
        print(clarificationform)
        print('yesgvhbhjb')
        approval_data.Priority = Priority
        approval_data.Category = Category
        approval_data.Sub_Category = Sub_Category
        approval_data.fin_commit = fin_commit
        approval_data.Total_Value = Total_Value
        approval_data.save()

        doc_data.doc_clarifictaions_reason = doc_clarifictaions_reason
        doc_data.doc_clarification_status = 'verified'
        doc_data.save()

        # if docremarksform.is_valid():
        #     doc_data.doc_clarifictaions_reason = doc_clarifictaions_reason
        #     doc_data.doc_clarification_status = doc_clarification_status
        #     DocRemarksUpdateForm.save()

        return redirect('clarification')
    return render(request, "e-approval/clarification.html",{"Name":name,"role":staff_role,"department":department})




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

    if approval_Remarks and role=='HOD':
        print("dsd------------------------------------------------------------")
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

    role_list = ['HOD','GM','vice_principal','Principal']
    approval_user = []
    date=None

    auth_list = e_approval.objects.filter(Document_no=Tran_No)
    for i,j in enumerate(auth_list):
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
        print(Tran_No,'-------------------------')
        return render(request, "e-approval/view_approval.html",{"Tran_No":Tran_No,"approval_user":approval_user,"Name":name,"role":role,"department":Department})

    doc_data=[]
    tran_no=e_approval.objects.filter(staff_id=staff_id)
    print(tran_no,'-------------------------')
    return render(request, "e-approval/view_approval.html",{"tran_no":tran_no,"Name":name,"role":role,"department":Department})



from django.shortcuts import HttpResponse #type:ignore
from django.core.exceptions import ObjectDoesNotExist #type:ignore

def pdf_show(request, Document_no):
    user_data=request.session.get('user_data', {})
    role=user_data['role']
    Department=user_data['Department']
    name=user_data["name"]
    # Retrieve the PDF object from the database
    if 0!=0:
        pdf = get_object_or_404(e_approval, Document_no=Document_no)

        # Get the file path from the attachment
        pdf_path = pdf.Attachment.path

        # Check if the file exists at the specified path
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{pdf.Attachment.name}"'
                return response
        else:
            return HttpResponse("PDF not found.")
    return render(request, "e-approval/view_approval.html",{"Name":name,"role":role,"department":Department})


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
