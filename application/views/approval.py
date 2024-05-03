from django.shortcuts import render, redirect, get_object_or_404
from application.form import e_approval
from application.models import e_approval,User
from datetime import datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
from django.core.paginator import Paginator
from django.conf import settings
from application.form import EApprovalForm,userform
from application.models import e_approval



def create_form(request, name, staff_id):
    if request.method == 'POST':
        form = EApprovalForm(request.POST)
        if form.is_valid():
            staff = User.objects.get(staff_id=staff_id)
            user = form.save(commit=False)
            role = staff.role
            user.staff_id = staff_id

            # Set approval status based on role
            if role == 'Technician':
                user.Technician = None
                user.HOD = 'Pending'
                user.GM = 'Pending'
                user.vise_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'HOD':
                user.Technician = None
                user.HOD = None
                user.GM = 'Pending'
                user.vise_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'GM':
                user.Technician = None
                user.HOD = None
                user.GM = None
                user.vise_principal = 'Pending'
                user.principal = 'Pending'
            elif role == 'vice_principal':
                user.Technician = None
                user.HOD = None
                user.GM = None
                user.vise_principal = None
                user.principal = 'Pending'

            user.save()  # Save the user with updated fields
            return redirect('create_form',name,staff_id)  # Redirect to a success page
        else:
            return render(request, "e-approval/error.html", {'form': form})
    else:
        form = EApprovalForm()
        staff_user = User.objects.get(staff_id=staff_id)
        department=staff_user.Department
        staff_approval_exists = e_approval.objects.filter(staff_id=staff_id).exists()
        if staff_approval_exists:
            staff_approval = e_approval.objects.get(staff_id=staff_id)
            gm_user, vise_principal_user, principal_user = None, None, None
            if staff_approval.GM == 'Pending':
                gm_user = User.objects.get(role='GM')
            else:
                gm_user='Null'
            if staff_approval.vise_principal == 'Pending':
                vise_principal_user = User.objects.get(role='vise_principal')
            else:
                vise_principal_user='Null'
            if staff_approval.principal == 'Pending':
                principal_user = User.objects.get(role='principal')
            else:
                principal_user='Null'
            if staff_approval.HOD == 'Pending':
                HOD_user = User.objects.get(role='HOD',Department=department)
            else:
                HOD_user='Null'
            return render(request, "e-approval/index.html", {'form': form, 'gm_user': gm_user, 'vise_principal_user': vise_principal_user,
                                                            'principal_user': principal_user, 'HOD': HOD_user
                                                         })
        return render(request, "e-approval/index.html", {'form': form,
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
            # Passwords match, log in the user
            # Set session variables or use Django's login system as needed
            request.session['user_id'] = user.id
            name=user.user_name
            return redirect('create_form',name,staff_id)
        else:
            # Passwords don't match, show an error message
            error_message = 'Invalid username or password.'
            return render(request, "auth/login.html", {'error_message': error_message})
    else:
        return render(request, "auth/login.html")

# def authorize_e_approval(request,staff_id):
#     form = User.objects.filter(staff_id=staff_id).first()

#     if form is None:  # Form not found, render personal.html with Aadhaar_Number
#         return render(request, "form/personal.html", {'Aadhaar_Number': Aadhaar_Number})
#     else:
#         return render(request, "form/recheck_personal.html", {'form': form})

#     return render(request, "form/aadhar.html")
#     return render(request, "e-approval/auth_approval.html")