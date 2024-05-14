import re
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
from django.core.paginator import Paginator
from django.conf import settings
from application.form import EApprovalForm,userform,auth_form,doc_remarks_form,DocRemarksUpdateForm,ClarificationUpdateForm
from application.models import e_approval,User,doc_remarks
from django.contrib import messages
import inflect
def in_words(Total_Value):
    p = inflect.engine()
    In_words= p.number_to_words(Total_Value)
def create_form(request):
    user_data=request.session.get('user_data', {})
    name=user_data["name"]
    staff_id=user_data["staff_id"]

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

            user.save()  # Save the user with updated fields
            return redirect('create_form')  # Redirect to a success page
        else:
            return render(request, "e-approval/error.html", {'form': form})
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
        return render(request, "e-approval/index.html", {'form': form, "appruval_user":approval_user
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
            confirm_password = form.cleaned_data['conform_Password']

            if password == confirm_password:
                encrypted_password = encrypt_password(password)

                # Save the encrypted password to your user model
                user = form.save(commit=False)  # Don't save the form yet
                user.Password = encrypted_password
                user.conform_Password = encrypted_password

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
            'conform_Password' : user.conform_Password           }
            request.session['user_data'] = user_dict

            return redirect('create_form')
        else:
            # Passwords don't match, show an error message
            error_message = 'Invalid username or password.'
            return render(request, "auth/login.html", {'error_message': error_message})
    else:
        return render(request, "auth/login.html")


# def auth_approval(request):
#     staff_id = e_approval.objects.filter(staff_id=567654)
#     Document_no = request.GET.get('Document_no')
#     print(Document_no,'89')
#     if Document_no:
#         Document_no = e_approval.objects.get(Document_no=Document_no)
#         staff_id=Document_no.staff_id
#         gm=Document_no.GM
#         vice_prinicipal=Document_no.vice_principal
#         prinicipal=Document_no.principal
#         if gm=='pending':
#             auth_staff_id = User.objects.get(staff_id=staff_id)
#         print(Document_no)
#         gm = User.objects.get(role='GM')
#         vice_principal = User.objects.get(role='vice_principal')
#         principal = User.objects.get(role='Principal')

#         if Document_no:
#             print(Document_no)
#             return render(request, "e-approval/auth_approval.html",{"Document_no":Document_no,"gm":gm,"vice_principal":vice_principal,"principal":principal})

#         return render(request, "e-approval/auth_approval.html",{"Document_no":Document_no})
#     return render(request, "e-approval/auth_approval.html",{"staff_id":staff_id})

def auth_approval(request):
    user_data=request.session.get('user_data', {})
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
        document_data = e_approval.objects.get(Document_no=Document_no)
        return render(request, "e-approval/auth_approval.html",{"Document_no":document_data})

    staff_id = e_approval.objects.filter(staff_id=567654)
    print(staff_id)
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
            approvals = e_approval.objects.filter(staff_id=technician.staff_id ,HOD = 'approved',GM='Pending',vice_principal='Pending',principal='Pending')

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
            approvals = e_approval.objects.filter(staff_id=technician.staff_id ,HOD = 'approved',GM='approved',vice_principal='Pending',principal='Pending')

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
            approvals = e_approval.objects.filter(staff_id=technician.staff_id ,HOD = 'approved',GM='approved',vice_principal='approved',principal='Pending')
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




    return render(request, "e-approval/auth_approval.html",{"staff_id":staff_id,"doc_data":doc_data})

doc_no = None # Declare the global variable outside the function

def clarification(request):

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
        return render(request, "e-approval/clarification.html", {"document_data": document_data,"remarks_document_data":remarks_document_data})


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
    return render(request, "e-approval/clarification.html", {"document_data_value": doc_data})



def approval_user_details(request):
    return render(request, "e-approval/approval_user_details.html")


def updateapproval(request):
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
        print(Category)

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
    return render(request, "e-approval/clarification.html")




def form_approval(request):
    approval_Remarks = request.POST.get('approval_Remarks')
    Document_no = request.POST.get('Document_no')
    now = datetime.now()

    # Format the date and time as a string
    current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    approval_Reason = request.POST.get('approval_Reason')
    print(approval_Remarks,Document_no,approval_Reason)
    user_data=request.session.get('user_data', {})
    role=user_data["role"]
    approval_data = get_object_or_404(e_approval,Document_no=Document_no)

    if approval_Remarks and role=='HOD':
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='GM':
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='vice_principal':
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='Principal':
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='HOD':
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='GM':
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='vice_principal':
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='Principal':
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    return render(request, "e-approval/auth_approval.html")


def view_approval(request):
    Tran_No = request.GET.get('Tran_No')
    user_data=request.session.get('user_data', {})
    role=user_data['role']
    Department=user_data['Department']

    approval_user = []

    role_list = ['Technician','HOD','GM','vice_principal','Principal']
    ia = role_list.index(role)
    for i in role_list[ia+1:]:
        print(i)
        if i == "HOD":
            approvals = e_approval.objects.exclude(HOD='Pending').filter(Tran_No=Tran_No,GM='Pending', vice_principal='Pending', principal='Pending')
            date=None
            for approval in approvals:
                date=approval.HOD_date
            approval_user.append({
                'approvals': date,
                'user': User.objects.filter(Department=Department, role=i).first()
            })
        elif i == "GM":
            approval_user.append(User.objects.filter(role=i).first())
        elif i == "vice_principal":
            approval_user.append(User.objects.filter(role=i).first())
        elif i == "Principal":
            approval_user.append(User.objects.filter(role=i).first())

    # print("data-=========================",Tran_No)
    if Tran_No:
        Tran_No = e_approval.objects.get(Tran_No=Tran_No)
        print(Tran_No)
        return render(request, "e-approval/view_approval.html",{"Tran_No":Tran_No,"approval_user":approval_user})

        return render(request, "e-approval/view_approval.html")
    return render(request, "e-approval/view_approval.html")
