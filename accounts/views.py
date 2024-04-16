from django.shortcuts import redirect, render
import requests.utils
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse

# Verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id

import requests

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.set_password(password)
            user.save()

            # USER ACTIVATION
            # getting the current site
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            # instead of writing message here we are creating a html file and pass the disctionary to it
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                # encoding primarykey os that it will be not visible to anyone
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # generating token
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()

            # DISPLAYING MESSAGE
            # messages.success(request, 'Registration Successful!! We have sent you a verification email to your email adderss. Please verify it.')

            # Redirecting the user to a new link
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                # getting the cart
                cart = Cart.objects.get(cart_id=_cart_id(request))

                # checking is the cart item exists or not
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    # getting the cart item
                    cart_item = CartItem.objects.filter(cart=cart)

                    # getting the current product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # getting the cart items from the user to access his existing product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for prod_var in product_variation:
                        # increasing the product variation count if item already exists
                        if prod_var in ex_var_list:
                            index = ex_var_list.index(prod_var)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        # if item does not exists then add the item
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            # assigning the user to all the cart item
                            for item in cart_item:
                                item.user = user
                                item.save()
                                
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'Logged in Successfully')

            # getting the full url using the get method
            url = request.META.get('HTTP_REFERER')
            # http://127.0.0.1:8000/accounts/login/  OR, http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/

            try:
                # taking only the part that is after '?' here, 'next=/cart/checkout/'
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                
                # making the url into a dictionary so that we can use it further
                params = dict(x.split('=') for x in query.split('&'))   
                # {'next': '/cart/checkout/'}

                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)

            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully Logged Out')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        # decoding the token
        uid = urlsafe_base64_decode(uidb64).decode()
        # checking with account
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # making the user as active
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link!!")
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email):
            user = Account.objects.get(email__exact=email)

            # RESET PASSWORD LINK
            # getting the current site
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            # instead of writing message here we are creating a html file and pass the disctionary to it
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site,
                # encoding primarykey os that it will be not visible to anyone
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # generating token
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()

            messages.success(
                request, 'Password reset email has been sent to your email address. Verify it!!')
            return redirect('login')
        else:
            messages.error(request, 'Accounts does not exists!!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        # decoding the token
        uid = urlsafe_base64_decode(uidb64).decode()
        # checking with account
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # saving the user in session
        request.session['uid'] = uid
        messages.success(request, "Please reset your password!!")
        return redirect('resetPassword')
    else:
        messages.error(request, "Link has been expired!!")
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # getting id from the saved session
            uid = request.session.get('uid')
            # fetching the user
            user = Account.objects.get(pk=uid)
            # hashing the password
            user.set_password(password)
            # saving the password
            user.save()
            messages.success(request, 'Password reset successful!!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!!')
            return redirect('forgotPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
