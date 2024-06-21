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
from application.models import e_approval,User,doc_remarks,status     #type:ignore
from django.contrib import messages #type:ignore
from django.db.models import Q  #type:ignore
import pandas as pd  
from num2words import num2words   
from django.core.mail import send_mail

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

def create_form(request):
    user_data=request.session.get('user_data', {})
    staff_id=user_data["staff_id"]
    Name=user_data["name"]
    Department=user_data["Department"]
    role=user_data["role"]
    email=user_data['email']


    excel_file_path = 'category.csv'
    excel_file_path1 = 'Book1.csv'
    try:
        head = pd.read_csv(excel_file_path1)
    except pd.errors.EmptyDataError:
        # Handle the case where the Excel file is empty
        head = pd.DataFrame(columns=['Head of account'])
    # # Read the Excel file
    try:
        df = pd.read_csv(excel_file_path)
    except pd.errors.EmptyDataError:
        # Handle the case where the Excel file is empty
        df = pd.DataFrame(columns=['Sub_category'])

    category = df['Sub_category'].tolist()
    head_account = head['Head of account'].tolist()

    print(head_account,'--------------------------------------------------')

    if request.method == 'POST':
        form = EApprovalForm(request.POST)
        if form.is_valid():
            Department = form.cleaned_data['Department']
            Category = form.cleaned_data['Category']
            dept_code={"ARTIFICIAL INTELLIGENCE AND DATA SCIENCE":"AD",
                       "CIVIL ENGINEERING":"CE",
                       "COMPUTER SCIENCE AND BUSINESS SYSTEM":"CB",
                       "COMPUTER SCIENCE AND ENGINEERING":"CSE",
                       "ELECRICAL AND ELECTRONICS ENGINEERING":"EEE",
                       "ELECTRONICS AND COMMUNICATION ENGINEERING":"ECE",
                       "INFORMATION TECHNOLOGY":"IT",
                       "MECHANICAL ENGINEERING":"MECH",}
            count = e_approval.objects.count() + 1
            print(count)
            year = datetime.now().strftime("%Y")
            count_no = f"{count:05d}"
            tran_count = e_approval.objects.filter(Department=Department).count() + 1
            tran_count_no = f"{tran_count:05d}"
            if dept_code[Department] == dept_code[Department]:
                doc_no = f'RIT/AC/{year}/{dept_code[Department]}/{Category}/{tran_count_no}'
            print(doc_no)
            tran_no = f'RIT/AC/{year}/{dept_code[Department]}/{Category}/{count_no}'
            staff = User.objects.get(staff_id=staff_id)
            user = form.save(commit=False)
            role = staff.role
            user.staff_id = staff_id
            user.Document_no = doc_no
            user.Tran_No = tran_no
            user.creator=role

            file_paths = save_uploaded_pdfs(request.FILES)

            print(".......................................................",file_paths.get('Attachment'))
            user.Attachment = file_paths.get('Attachment')
            
            # Set approval status based on role
            if role == 'Technician':
                user.Technician = None
                user.Staff = 'Pending'
                user.HOD = 'Pending'
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'

            elif role == 'Staff':
                user.Technician = None
                user.Staff = None
                user.HOD = 'Pending'
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'HOD':
                user.Technician = None
                user.Staff = None
                user.HOD = None
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'

            elif role == 'office':
                user.Technician = None
                user.Staff = None
                user.HOD = None
                user.GM = 'Pending'
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'GM':
                user.Technician = None
                user.Staff = None
                user.HOD = None
                user.GM = None
                user.vice_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'vice_principal':
                user.Technician = None
                user.Staff = None
                user.HOD = None
                user.GM = None
                user.vice_principal = None
                user.principal = 'Pending'
            
            user.save()
       
            

            send_email(request,email)
            approval_user = []
            date=None
            approval_user = []
            new_approval_user=[]
            date=None

            auth_list = e_approval.objects.filter(Document_no=tran_no)
            print(auth_list,"gfgdfgdsfgdfdfgdgf")
            for i,j in enumerate(auth_list):
                # if j.Staff!='Pending':
                new_approval_user.append({"date":j.Staff_date,'Approval':'Staff',
                'user':User.objects.filter(Department=Department, role='Staff').first()})
                # if j.HOD!='Pending':
                new_approval_user.append({"date":j.HOD_date,'Approval':'HOD',
                'user':User.objects.filter(Department=Department, role='HOD').first()})
                # if j.GM!='Pending':
                new_approval_user.append({"date":j.GM_date,'Approval':'GM',
                'user':User.objects.filter( role='GM').first()})
                # if j.vice_principal!='Pending':
                new_approval_user.append({"date":j.vice_principal_date,'Approval':'vice_principal',
                'user':User.objects.filter( role='vice_principal').first()})
                # if j.principal!='Pending':
                new_approval_user.append({"date":j.principal_date,'Approval':'principal',
                'user':User.objects.filter( role='principal').first()})
                new_approval_user.reverse()
                for i in range(0,len(new_approval_user)):
                    if new_approval_user[i]['Approval']!=j.creator:
                        if new_approval_user[i]['date'] == None:
                            new_approval_user[i]['date']="Pending"
                            approval_user.append(new_approval_user[i])
                        else:
                            approval_user.append(new_approval_user[i])
                    else:
                        break
                send_approval=approval_user[-1]['user'].email
                send_email(request, send_approval)
                print(send_approval,"------------")
            return redirect('create_form')

        else:
            return render(request, "e-approval/error.html", {'form': form,"category":category,"role":role,"Department":Department,"Name":Name,"head_account":head_account})
    else:
        form = EApprovalForm()
        staff_user = User.objects.get(staff_id=staff_id)
        department=staff_user.Department
        role=staff_user.role
        role_list = ['Technician','office','Staff','HOD','GM','vice_principal','Principal']
        ia = role_list.index(role)
        print(department,role,ia)
        approval_user = []
        for i in role_list[ia]:
            print(i)
            if i == "Staff":
                approval_user.append(User.objects.filter(Department=department, role=i).first())  # Use .first() to get the first object or None
            elif i == "HOD":
                approval_user.append(User.objects.filter(Department=department,role=i).first())  # Use .first() to get the first object or None
            elif i == "GM":
                approval_user.append(User.objects.filter(role=i).first())
            elif i == "vice_principal":
                approval_user.append(User.objects.filter(role=i).first())
            elif i == "Principal":
                approval_user.append(User.objects.filter(role=i).first())
            # return render(request, "e-approval/index.html", {'form': form, 'gm_user': gm_user, 'vice_principal_user': vice_principal_user,
            #                                                 'principal_user': principal_user, 'HOD': HOD_user
            #                                              })
        print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        return render(request, "e-approval/index.html", {'form': form, "approval_user":approval_user,"category":category,"role":role,"Department":Department,"Name":Name,"head_account":head_account,
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

    print(user_data['role'])
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

            print("fdsfdsfdsfdsfdsfdddfdfdssdfddf")
            user.save()
        else:
            return render(request, "e-approval/error.html", {'form': form})


    Document_no = request.GET.get('Document_no')


    if Document_no:
        role=staff_role
        role_list = ['Staff','HOD','GM','vice_principal','Principal']
        ia = role_list.index(role)
        print(department,role,ia)
        approval_user = []
        print(approval_user,"!!!!!!!!!!!!!")
        date=None

        auth_list = e_approval.objects.filter(Document_no=Document_no)
        for i,j in enumerate(auth_list):
            if j.Staff!='Pending':
                approval_user.append({"date":j.Staff_date,'Approval':'Staff','name':j.Staff_name,
                'remarks':j.Staff})
            if j.HOD!='Pending':
                approval_user.append({"date":j.HOD_date,'Approval':'HOD','name':j.HOD_name,
                'remarks':j.HOD})
            if j.GM!='Pending':
                approval_user.append({"date":j.GM_date,'Approval':'GM','name':j.GM_name,
                'remarks':j.GM})
            if j.vice_principal!='Pending':
                approval_user.append({"date":j.vice_principal_date,'Approval':'vice_principal','name':j.vp_name,
                'remarks':j.vice_principal})
            if j.principal!='Pending':
                approval_user.append({"date":j.principal_date,'Approval':'principal','name':j.principal_name,
                'remarks':j.principal})
            for a in approval_user:
                print(approval_user)
        document_data = e_approval.objects.get(Document_no=Document_no)
        number = document_data.Total_Value
        number_in_words = num2words(number)
        print(auth_list)
        return render(request, "e-approval/auth_approval.html",{"Document_no":document_data,"approval_user":approval_user,"doc":Document_no,"Name":name,"role":staff_role,"department":department,"number_in_words":number_in_words,'doc_data':doc_data})


    user_data=request.session.get('user_data', {})
    print(user_data['role'])
    def filler(user_data):
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
            technicians = User.objects.filter(Department=user_data['Department'], role__in=['Technician','Staff'])
            for technician in technicians:
                approvals = e_approval.objects.exclude(Staff='Pending').filter(staff_id=technician.staff_id ,HOD = 'Pending',GM='Pending',vice_principal='Pending',principal='Pending')

                if  approvals:
                    for approval in approvals:  # Iterate through the queryset
                        staff = User.objects.filter(staff_id=approval.staff_id).first()
                        approval.staff_name = staff.Name
                        doc_data.append(approval)
        elif user_data['role'] == 'GM':
            technicians = User.objects.filter(
                role__in=['Technician',"Staff",'HOD','office']  # Use role__in for multiple roles
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
                role__in=['Technician',"Staff", 'GM','HOD','office']  # Use role__in for multiple roles
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
                role__in=['Technician', 'GM',"Staff", 'vice_principal','HOD','office']  # Use role__in for multiple roles
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

    if request.method == 'POST':
        form = auth_form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = staff.role
    filler(user_data)
    print(doc_data,"#$#$#$#$#$#$#$#$#$#$")
    return render(request, "e-approval/auth_approval.html",{"doc_data":doc_data,"Name":name,"role":staff_role,"department":department,'doc_data':doc_data})

doc_no = None # Declare the global variable outside the function

def clarification(request):
    user_data=request.session.get('user_data', {})
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    user_name=user_data["user_name"]
    print(user_name)

    document_data_value = request.GET.get('document_data_value')

    if document_data_value:
        key, value = document_data_value.split('|')
        doc_no = value  # Update the global variable value
        # Now you can use key and value as needed
        print("Key:", key)
        print("Value:", value)
        document_data = e_approval.objects.get(Document_no= value)
        remarks_document_data = doc_remarks.objects.get(Document_no=key, doc_clarification_status='Pending')

        print(document_data,"+++++++++++++")
        return render(request, "e-approval/clarification.html", {"document_data": document_data,"remarks_document_data":remarks_document_data,"Name":name,"user_name":user_name,"role":staff_role,"department":department,"document_data_value": doc_data})
    user_data = request.session.get('user_data', {})
    def fillerer(user_data):
        global doc_data
        doc_data = {}
        
        document_data_list = doc_remarks.objects.filter(doc_applied_staff_id=user_data['staff_id'], doc_clarification_status='Pending')
        for doc in document_data_list:
            pattern = r"^(.*?)@"
            match = re.search(pattern, doc.Document_no)
            if match:
                document_data_value = match.group(1)
                doc_data[doc.Document_no] = document_data_value
    fillerer(user_data)

    return render(request, "e-approval/clarification.html", {"document_data_value": doc_data,"Name":name,"role":staff_role,"user_name":user_name,"department":department,"document_data_value": doc_data})



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
        # Sub_Category = request.POST.get('Sub_Category')
        fin_commit = request.POST.get('fin_commit')
        Total_Value = request.POST.get('Total_Value')
        doc_clarifictaions_reason = request.POST.get('doc_clarifictaions_reason')
        file_paths = save_uploaded_pdfs(request.FILES)
        approval_data = get_object_or_404(e_approval,Document_no=Document_no)
        doc_data = get_object_or_404(doc_remarks,Document_no=remarks_Document_no)
        approval_data.Priority = Priority
        approval_data.Category = Category
        # approval_data.Sub_Category = Sub_Category
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
    Tran_No = request.GET.get('Tran_No')
    user_data=request.session.get('user_data', {})
    approval_Remarks = request.POST.get('approval_Remarks')
    Document_no = request.POST.get('Document_no')
    default=["GM",'vice_principal','Principal']
    roles=['Technician','Staff','HOD']
    if user_data['role'] in roles :
        start_index = roles.index(user_data['role'])
        toallist = [User.objects.filter(role=i, Department=user_data['Department']).values_list('email', flat=True).first() for i in roles[start_index+1:]]+[User.objects.filter(role=i).values_list('email', flat=True).first() for i in default]
    else:
        # Handle the case where user_role is not in the roles list
        start_index = default.index(user_data['role'])
        print('***************')
        toallist = [User.objects.filter(role=i).values_list('email', flat=True).first() for i in default[start_index+1:]]
    print('$$$$$$$$$',toallist)
    now = datetime.now()
    print("dsd------------------------------------------------------------")
    staff_role=user_data['role']
    department=user_data['Department']
    name=user_data["name"]
    user_name=user_data["user_name"]
    Department=user_data['Department']
    print(user_name,"approval")
    # Format the date and time as a string
    current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    approval_Reason = request.POST.get('approval_Reason')
    print(approval_Remarks,Document_no,approval_Reason)
    user_data=request.session.get('user_data', {})
    role=user_data["role"]
    approval_data = get_object_or_404(e_approval,Document_no=Document_no)

    if approval_Remarks and role=='Staff':
        approval_data.Staff_name=user_name
        approval_data.Staff = approval_Remarks
        approval_data.Staff_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='HOD':
        approval_data.HOD_name=user_name
        approval_data.HOD = approval_Remarks
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='GM':
        approval_data.GM_name=user_name
        approval_data.GM = approval_Remarks
        approval_data.GM_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='vice_principal':
        approval_data.vp_name=user_name
        approval_data.vice_principal = approval_Remarks
        approval_data.vice_principal_date = current_date_time
        approval_data.save()

    if approval_Remarks and role=='Principal':
        approval_data.principal_name=user_name
        approval_data.principal = approval_Remarks
        approval_data.principal_date = current_date_time
        approval_data.save()
    
    if approval_Reason and role=='Staff':
        approval_data.Staff_name=user_name
        approval_data.Staff = approval_Reason
        approval_data.Staff_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='HOD':
        approval_data.HOD_name=user_name
        approval_data.HOD = approval_Reason
        approval_data.HOD_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='GM':
        approval_data.GM_name=user_name
        approval_data.GM = approval_Reason
        approval_data.GM_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='vice_principal':
        approval_data.vp_name=user_name
        approval_data.principal = approval_Reason
        approval_data.vice_principal_date = current_date_time
        approval_data.save()

    if approval_Reason and role=='Principal':
        approval_data.principal_name=user_name
        approval_data.principal = approval_Reason
        approval_data.principal_date = current_date_time
        approval_data.save()
    print('wewwwewewewewewewewewe',toallist[0])
    send_email(request,toallist[0])


    return render(request, "e-approval/auth_approval.html",{"Name":name,"role":staff_role,"department":department,"user_name":user_name,"doc_data":doc_data})


def view_approval(request):
    Tran_No = request.GET.get('Tran_No')
    user_data=request.session.get('user_data', {})
    role=user_data['role']
    Document_no=request.GET.get('Tran_No')
    Department=user_data['Department']
    staff_id=user_data['staff_id']
    name=user_data["name"]

    approval_user = []
    date=None
    approval_user = []
    new_approval_user=[]
    date=None

    auth_list = e_approval.objects.filter(Document_no=Document_no)
    print(auth_list,"gfgdfgdsfgdfdfgdgf")
    for i,j in enumerate(auth_list):
        # if j.Staff!='Pending':
        new_approval_user.append({"date":j.Staff_date,'Approval':'Staff',
        'user':User.objects.filter( role='Staff').first()})
        # if j.HOD!='Pending':
        new_approval_user.append({"date":j.HOD_date,'Approval':'HOD',
        'user':User.objects.filter( role='HOD').first()})
        # if j.GM!='Pending':
        new_approval_user.append({"date":j.GM_date,'Approval':'GM',
        'user':User.objects.filter( role='GM').first()})
        # if j.vice_principal!='Pending':
        new_approval_user.append({"date":j.vice_principal_date,'Approval':'vice_principal',
        'user':User.objects.filter( role='vice_principal').first()})
        # if j.principal!='Pending':
        new_approval_user.append({"date":j.principal_date,'Approval':'principal',
        'user':User.objects.filter( role='principal').first()})
        new_approval_user.reverse()
        print(new_approval_user)
        for i in range(0,len(new_approval_user)):
            if new_approval_user[i]['Approval']!=j.creator:
                if new_approval_user[i]['date'] == None:
                    new_approval_user[i]['date']="Pending"
                    approval_user.append(new_approval_user[i])
                else:
                    approval_user.append(new_approval_user[i])
            else:
                break
                
    print(approval_user)

    if Tran_No:
        Tran_No = e_approval.objects.get(Tran_No=Tran_No)
        if role == "GM"or role == "vice_principal" or role == "Principal":
            tran_no=e_approval.objects.filter()
        else:
            tran_no=e_approval.objects.filter(Department=Department)
        print(Tran_No,'!-------------------------!')
        return render(request, "e-approval/view_approval.html",{"Tran_No":Tran_No,"approval_user":approval_user,"Name":name,"role":role,"department":Department,"tran_no":tran_no})

    doc_data=[]
    if role == "GM"or role == "vice_principal" or role == "Principal":
            tran_no=e_approval.objects.filter()
    else:
        tran_no=e_approval.objects.filter(Department=Department)
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

def send_email(request,email):
    user_data=request.session.get('user_data', {})
    Tran_No = request.GET.get('Tran_No')

    subject_create = ''
    message_create = 'This is a test email sent from Django.'


    send_mail(
    subject_create,
    message_create,
    "ganeshperumal256@gmail.com",
    [email],
    fail_silently=False,
    )
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
from datetime import datetime
from PyPDF2 import PdfMerger
from reportlab.pdfgen import canvas

def generate_pdf(request,Tran_No):
    print(Tran_No)
    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()
    Document_no = e_approval.objects.get(Tran_No=Tran_No)

    user = User.objects.get(Department=Document_no.Department,role='Technician')
    user1 = User.objects.get(Department=Document_no.Department,role='Staff')
    user2 = User.objects.get(Department=Document_no.Department,role='HOD')
    user3 = User.objects.get(role='GM')
    user4 = User.objects.get(role='vice_principal')
    user5 = User.objects.get(role='Principal')

    staff_id = User.objects.get(staff_id=Document_no.staff_id)
    role=staff_id.role



    # def handle_uploaded_file(f):
    #     with open('{Tran_No.Attachment}', 'wb+') as destination:
    #         for chunk in f.chunks():
    #             destination.write(chunk)
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Draw the content on the PDF
    width, height = A4
    Generated_date=datetime.now()
    Generated_date_str = Generated_date.strftime('%Y-%m-%d/%H:%M')
        
    print(Generated_date)
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(175, height - 50, "Ramco Institute of Technology")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(245, height - 80, "E-approval")
    p.drawString(50, height - 330, "Approval List")
    
    # Labels
    p.setFont("Times-Bold", 13)
    
    p.drawString(70, height - 120, "Department :")
    p.drawString(210, height - 170, ":")
    p.drawString(70, height - 150, "Trans NO ")
    p.drawString(210, height - 150, ":")
    p.drawString(70, height - 190, "Category ")
    p.drawString(210, height - 190, ":")
    p.drawString(70, height - 210, "Subject ")
    p.drawString(210, height - 210, ":")
    p.drawString(70, height - 250, "Remarks ")
    p.drawString(210, height - 250, ":")
    p.drawString(70, height - 270, "Approval Date")
    p.drawString(210, height - 270, ":")
    p.drawString(70, height - 230, "Approved Request Date")
    p.drawString(210, height - 230, ":")
    p.drawString(70, height - 310, "Amount (INR) ")
    p.drawString(210, height - 310, ":")


    p.setFont("Times-Roman", 12)
    p.drawString(180, height - 120, Document_no.Department)
    p.drawString(220, height - 150, Document_no.Tran_No)
    p.drawString(220, height - 190, Document_no.Category)
    p.drawString(220, height - 290, Document_no.Head_of_account)
    p.drawString(220, height - 210, Document_no.remarks_Subject)
    p.drawString(220, height - 250, str(Document_no.remarks_Subject1))
    p.drawString(220, height - 230, str(Document_no.date))
    p.drawString(220, height - 270, str(Document_no.vice_principal_date))
    p.drawString(220, height - 310, Document_no.Total_Value)
    p.drawString(220, height - 170, Document_no.Document_no)    

    
    
    p.setFont("Times-Bold", 13)
    p.drawString(70, height - 170, "Doc NO ")
    p.drawString(70, height - 290, "Head of Account")
    p.drawString(210, height - 290, ":")


    image_path = "static/image/RIT_logo.png"
    if os.path.isfile(image_path):
        img = Image.open(image_path)
        img_reader = ImageReader(img)
        p.drawImage(img_reader, 70, height - 100, width=70, height=70)  # Adjust the coordinates and size as needed


    if role=='Technician':
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(302, height - 360, "Date(YYYY-mm-dd) & Time")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))
        p.drawString(150, height - 420, user4.Name)
        p.drawString(320, height - 420, str(Document_no.vice_principal_date))
        p.drawString(150, height - 450, user3.Name)
        p.drawString(320, height - 450, str(Document_no.GM_date))
        p.drawString(150, height - 480, user2.Name)
        p.drawString(320, height - 480, str(Document_no.HOD_date))
        p.drawString(150, height - 510, user1.Name)
        p.drawString(320, height - 510, str(Document_no.Staff_date))

        p.line(100, height - 340, 500, height - 340)
        p.line(100, height - 370, 500, height - 370)
        p.line(100, height - 400, 500, height - 400)
        p.line(100, height - 430, 500, height - 430)
        p.line(100, height - 460, 500, height - 460)
        p.line(100, height - 490, 500, height - 490)
        p.line(100, height - 520, 500, height - 520)


        p.line(100, height - 340, 100, height - 520)
        p.line(300, height - 340, 300, height - 520)
        p.line(500, height - 340, 500, height - 520)
    elif role=='Staff':
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(302, height - 360, "")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))
        p.drawString(150, height - 420, user4.Name)
        p.drawString(320, height - 420, str(Document_no.vice_principal_date))
        p.drawString(150, height - 450, user3.Name)
        p.drawString(320, height - 450, str(Document_no.GM_date))
        p.drawString(150, height - 480, user2.Name)
        p.drawString(320, height - 480, str(Document_no.HOD_date))


        p.line(100, height - 340, 500, height - 340)
        p.line(100, height - 370, 500, height - 370)
        p.line(100, height - 400, 500, height - 400)
        p.line(100, height - 430, 500, height - 430)
        p.line(100, height - 460, 500, height - 460)
        p.line(100, height - 490, 500, height - 490)


        p.line(100, height - 340, 100, height - 490)
        p.line(300, height - 340, 300, height - 490)
        p.line(500, height - 340, 500, height - 490)
    elif role=='HOD':
        p.setFont("Courier-Bold", 14)
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(350, height - 360, "Date(YYYY-mm-dd) & Time")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))
        p.drawString(150, height - 420, user4.Name)
        p.drawString(320, height - 420, str(Document_no.vice_principal_date))
        p.drawString(150, height - 450, user3.Name)
        p.drawString(320, height - 450, str(Document_no.GM_date))



        p.line(100, height - 340, 500, height - 340)
        p.line(100, height - 370, 500, height - 370)
        p.line(100, height - 400, 500, height - 400)
        p.line(100, height - 430, 500, height - 430)
        p.line(100, height - 460, 500, height - 460)


        p.line(100, height - 340, 100, height - 460)
        p.line(300, height - 340, 300, height - 460)
        p.line(500, height - 340, 500, height - 460)
    


    elif role=='office':
        p.setFont("Courier-Bold", 14)
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(350, height - 360, "Date(YYYY-mm-dd) & Time")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))
        p.drawString(150, height - 420, user4.Name)
        p.drawString(320, height - 420, str(Document_no.vice_principal_date))
        p.drawString(150, height - 450, user3.Name)
        p.drawString(320, height - 450, str(Document_no.GM_date))



        p.line(100, height - 340, 500, height - 340)
        p.line(100, height - 370, 500, height - 370)
        p.line(100, height - 400, 500, height - 400)
        p.line(100, height - 430, 500, height - 430)
        p.line(100, height - 460, 500, height - 460)


        p.line(100, height - 340, 100, height - 460)
        p.line(300, height - 340, 300, height - 460)
        p.line(500, height - 340, 500, height - 460)
    
    elif role=='GM':
        p.setFont("Courier-Bold", 14)
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(350, height - 360, "Date(YYYY-mm-dd) & Time")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))
        p.drawString(150, height - 420, user4.Name)
        p.drawString(320, height - 420, str(Document_no.vice_principal_date))




        p.line(50, height - 340, 550, height - 340)
        p.line(50, height - 370, 550, height - 370)
        p.line(50, height - 400, 550, height - 400)
        p.line(50, height - 430, 550, height - 430)



        p.line(100, height - 340, 100, height - 430)
        p.line(300, height - 340, 300, height - 430)
        p.line(500, height - 340, 500, height - 430)
    
    elif role=='vice_principal':
        p.setFont("Courier-Bold", 14)
        p.setFont("Courier-Bold", 14)
        p.drawString(200, height - 360, "Name")
        p.drawString(350, height - 360, "Date(YYYY-mm-dd) & Time")
        p.drawString(150, height - 390, user5.Name)
        p.drawString(320, height - 390, str(Document_no.principal_date))




        p.line(50, height - 340, 550, height - 340)
        p.line(50, height - 370, 550, height - 370)
        p.line(50, height - 400, 550, height - 400)



        p.line(100, height - 340, 100, height - 400)
        p.line(300, height - 340, 300, height - 400)
        p.line(500, height - 340, 500, height - 400)
    
    
    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "Created by E-approval System/")
    p.drawString(190, 50, Generated_date_str)
    p.drawString(420, 820, "DATE:")
    p.drawString(460, 820, Generated_date_str)
    # Close the PDF object cleanly.
    p.showPage()
   

    # # Add watermark text
    # watermark_text = "Ramco Institute of Technology"
    # p.setFont("Times-Roman", 36)
    # p.setFillColorRGB(0.9, 0.9, 0.9)  # Light gray color for the watermark
    # p.saveState()
    # p.translate(300, 613)
    # p.rotate(33)
    # p.drawCentredString(0, 0, watermark_text)
    # p.restoreState()

    # # Title
    # p.setFont("Times-Roman", 12)
    # p.setFillColorRGB(0, 0, 0)
    # p.drawString(190, height - 50, "Ramco Institute of Technology")
    # p.setFont("Times-Roman", 10)
    # p.drawString(230, height - 60, "Rajapalayam")
    # p.drawString(220, height - 70, "Fuel Requisition Slip")
    # p.drawString(80, height - 90, "To :")
    # p.drawString(100, height - 100, "P.A.C.R. SETHURAMAMMAL CHARITY TRUST,")
    # p.drawString(150, height - 110, "BPCL, DEALERS @ 236463,")
    # p.drawString(100, height - 120, "P.A.C. RAMASAMY RAJASALAI, RAJAPALAYAM.")
    
    # p.setFont("Times-Roman", 10)
    # p.drawString(360, height - 50, 'Recipt No :')
    # p.drawString(422, height - 30, '')

    # # Car Details
    # p.setFont("Times-Roman", 10)
    # p.drawString(100, height - 150, "Please Supply for vehicle No")
    # p.drawString(260, height - 150, ":")
    # p.drawString(270, height - 150, '')
    # p.drawString(380, height - 150, "Date&Time")
    # p.drawString(435, height - 150, ":")
    # p.drawString(440, height - 150, '')
    
    # # Items
    # p.setFont("Times-Roman", 10)
    # p.drawString(130, height - 170, "Fuel Type")
    # p.drawString(185, height - 170, ":")
    # p.drawString(276, height - 160, '')

    # p.drawString(130, height - 190, "Vehicle Type")
    # p.drawString(185, height - 190, ":")
    # p.drawString(276, height - 160, '')


    # p.drawString(130, height - 210, "Fuel Quantity")
    # p.drawString(185, height - 210, ":")
    # p.drawString(195, height - 210, "Tank Full")

    # p.drawString(130, height - 230, "Engine Oil")
    # p.drawString(185, height - 230, ":")
    # # if data.engine_oil_quantity == 'None':
    # #     p.drawString(276, height - 200, 'None')
    # # else:
    # #     p.drawString(276, height - 200, ' Liter')

    # p.drawString(130, height - 250, "Grease Type")
    # p.drawString(185, height - 250, ":")
    # p.drawString(276, height - 250, '')

    # # if data.grease_quantity != 'None':
    # #     p.drawString(180, height - 240, "Grease")
    # #     p.drawString(265, height - 240, ":")
    # #     p.drawString(276, height - 240, ' kG')

    # # if data.grease_quantity == 'None' and data.distilled_water_quantity != 'None':
    # #     p.drawString(180, height - 240, "Distilled Water")
    # #     p.drawString(265, height - 240, ":")
    # #     p.drawString(276, height - 240, data.distilled_water_quantity + ' Liter')
    # # else:
    # #     p.drawString(180, height - 260, "Distilled Water")
    # #     p.drawString(265, height - 260, ":")
    # #     p.drawString(276, height - 260,  data.distilled_water_quantity + ' Liter')

    # # Signature and Address
    # p.setFont("Times-Roman", 12)
    # p.drawString(110, height - 320, "Transport Incharge")
    # p.drawString(100, height - 330, "N.Govindaraju/Rit2500")
    # p.drawString(420, height - 320, "GM Admin")
    # p.drawString(400, height - 330, "Selva Raj/Rit2369")

    # # Rectangle for the main content
    # p.rect(50, 500, 500, 310)

    # # Seal (simulated by drawing an ellipse and text)
    # image_path = "static/images/imag1.jpg"
    # if os.path.isfile(image_path):
    #     img = Image.open(image_path)
    #     img_reader = ImageReader(img)
    #     p.drawImage(img_reader, 340, height - 310, width=70, height=70)  # Adjust the coordinates and size as needed

    # # Finalize the PDF
    # p.showPage()
    # p.save()

    # # Get the value of the buffer and close it
    # pdf = buffer.getvalue()
    # buffer.close()

    # # Create the HttpResponse object with the appropriate PDF headers
    # response = HttpResponse(pdf, content_type='application/pdf')
    # # response['Content-Disposition'] = f'attachment; filename="{}.pdf"'   # This will prompt a download

    # return response



    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="e_approval.pdf"'
    response.write(pdf)
    return response
