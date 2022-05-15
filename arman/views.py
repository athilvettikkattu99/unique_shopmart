import json
from multiprocessing import context
import os
from django.conf import settings

from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import random
from .models import *

# Create your views here.
from .models import product

# count cart ites of user


def cart_count(uid):
    cots = Cart.objects.filter(User_id=uid).count()
    return cots


# index page

def index(request):
    if request.user.is_superuser:
        return redirect('home')
    elif 'id' in request.session:
        return redirect('user_home')
    else:
        pro = automate_data()
        cat = Category.objects.all().order_by('?')
        top_product_list = product.objects.filter(
            Top_product="yes").order_by('?')
        return render(request, 'index.html', {'cat': cat, 'pro': pro, 'top_product_list': top_product_list})

# selected category view page


def public_view_selected_category(request, pk):

    sel_prod = product.objects.filter(Category=pk).order_by('?')
    if sel_prod.count() > 0:
        return render(request, 'category_select_product.html', {'sel_prod': sel_prod})
    return render(request, 'category_select_product.html')

# public search product


def public_search_product(request):

    if request.method == "POST":
        search_data = request.POST.get('search_data')
        sel_prod = product.objects.filter(
            Name__icontains=search_data).order_by('?')
        if sel_prod.exists():
            return render(request, 'public_search_product.html', {'sel_prod': sel_prod})
    return render(request, 'public_search_product.html')

# public product full details


def public_view_product_details(request, pk):
    product_det = product.objects.get(id=pk)
    product_sub_imgs = product_images.objects.filter(Product_id=pk)
    return render(request, 'public_view_product_details.html', {'product_det': product_det, 'product_sub_imgs': product_sub_imgs})


def home(request):
    if request.user.is_superuser:
        orders = My_order.objects.filter(~Q(Status="Delivered"), ~Q(
            Status="canceled")).values('User_id').distinct()
        pro_data = product.objects.all()
        users = UserDetails.objects.all()
        context = {'orders': orders, 'pro_data': pro_data, 'users': users}
        return render(request, 'home.html', context)
    else:
        return redirect('/')


def category_page(request):
    if request.user.is_superuser:
        lists = Category.objects.all().order_by('-id')
        return render(request, 'category.html', {'list': lists})
    else:
        return redirect('/')


def product_page(request):
    if request.user.is_superuser:
        product_data = product.objects.all().order_by('?')
        return render(request, 'product.html', {'p_data': product_data})
    else:
        return redirect('/')


def login_request(request):
    if request.user.is_superuser:
        return redirect('home')
    elif 'id' in request.session:
        return redirect('user_home')
    else:
        if request.method == 'POST':
            password = request.POST.get('password')
            name = request.POST.get('username')

            user_admin = User.objects.filter(username=name)

            if user_admin:
                try:
                    user = authenticate(username=name, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('home')
                    else:
                        msg_error = "Username and Password does not match"
                        return render(request, 'login.html', {'msg_error': msg_error})
                except ObjectDoesNotExist:
                    msg_error = "Username and Password does not match"
                    return render(request, 'login.html', {'msg_error': msg_error})
            else:
                try:

                    user_test = UserDetails.objects.get(
                        username=name, password=password)
                    if user_test is not None:
                        user_new = UserDetails.objects.get(username=name)
                        request.session['id'] = user_new.id
                        return redirect('user_home')
                    else:
                        msg_error = "Username and Password does not match"
                        return render(request, 'login.html', {'msg_error': msg_error})
                except ObjectDoesNotExist:
                    msg_error = "Username and Password does not match"
                    return render(request, 'login.html', {'msg_error': msg_error})
        else:
            return render(request, 'login.html')


def user_details(request):
    if request.user.is_superuser:
        user = User.objects.get(is_superuser=True)
        details_1 = AdminDetails.objects.get(user=user.id)
        details_2 = User.objects.get(id=user.id)
        return render(request, 'user_details.html', {'detail': details_1, 'detailData': details_2})
    else:
        return redirect('/')


def edit_profile(request):
    if request.user.is_superuser:

        user = User.objects.get(is_superuser=True)
        user_detail = AdminDetails.objects.filter(user=user.id).count()

        if user_detail > 0:
            user_details = AdminDetails.objects.get(user=user.id)

            if request.method == 'POST':

                if request.FILES.get('files') is not None:
                    if user_details.Image == "/static/images/fav_rm.png":
                        user_details.Image = request.FILES['files']
                    else:
                        os.remove(user_details.Image.path)
                        user_details.Image = request.FILES['files']

                user_details.Mobile = request.POST.get('mobile')
                user_details.Address = request.POST.get('address')
                user_details.save()

                user.name = request.POST.get('username')
                user.email = request.POST.get('email')
                user.save()
                msg_success = "Profile details saved successfully"
                return render(request, 'create_profile.html', {'msg_success': msg_success})
            else:
                return render(request, 'create_profile.html', {'user': user, 'user_detail': user_details})
        else:
            if request.method == 'POST':

                if request.FILES.get('files') is not None:
                    Image = request.FILES['files']
                else:
                    Image = "/static/images/fav_rm.png"
                Mobile = request.POST.get('mobile')
                Address = request.POST.get('address')
                AdminDetails.objects.create(
                    Mobile=Mobile, Image=Image, Address=Address, user_id=user.id)
                msg_success = "Profile details saved successfully"
                return render(request, 'create_profile.html', {'msg_success': msg_success})
            else:
                return render(request, 'create_profile.html', {'user': user, 'user_detail': user_detail})
    else:
        return redirect('/')


def reset_password(request):
    if request.user.is_superuser:
        if request.method == 'POST':

            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            user = User.objects.get(is_superuser=True)
            if password1 == password2:
                user.set_password(password1)
                user.save()
                msg_success = "Password has been changed successfully"
                return render(request, 'reset_password.html', {'msg_success': msg_success})
            else:
                msg_error = "Password does not match"
                return render(request, 'reset_password.html', {'msg_error': msg_error})
        return render(request, 'reset_password.html')
    else:
        return redirect('/')


def logout_request(request):
    if request.user.is_superuser:
        logout(request)
        return redirect('/')
    else:
        return redirect('/')


def add_new_category(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.FILES['image']
            if Category.objects.filter(name=name).exists():
                msg_error = "Category name already exists"
                messages.error(request, '')
                return render(request, 'add_category.html', {'msg_error': msg_error})
            else:
                Category.objects.create(
                    name=name, description=description, image=image)
                msg_success = "Category added succesfully"
                return render(request, 'add_category.html', {'msg_success': msg_success})
        else:
            return render(request, 'add_category.html')
    else:
        return redirect('/')


def add_product(request):
    if request.user.is_superuser:
        if request.method == "POST":

            name = request.POST.get('name')
            brand = request.POST.get('brand')
            category = request.POST.get('category')

            Category_id_find = Category.objects.get(id=category)
            if Category_id_find is not None:
                category_name = Category_id_find.name

            qty = request.POST.get('qty')
            rate = request.POST.get('rate')

            discount = request.POST.get('discount')
            if discount == "":
                discount = 0
            percentage = request.POST.get('percentage')
            if percentage == "":
                percentage = 0
            total_rate = request.POST.get('total_rate')
            top_product = request.POST.get('top_product')

            if top_product is None:
                top_product = "No"
            else:
                total_rate = request.POST.get('total_rate')

            per_unit = request.POST.get('units')
            Image = request.FILES['file']

            if not product.objects.filter(Name=name, Brand=brand, Category=category).exists():

                product.objects.create(Name=name, Brand=brand, Category=category, Qty=qty, Rate=rate, Discount=discount,
                                       per_unit=per_unit, Percentage=percentage, Total_rate=total_rate,
                                       Top_product=top_product, Image=Image, category_name=category_name)

                if len(request.FILES) != 0:
                    product_id = product.objects.latest('id')
                    images = request.FILES.getlist('files')
                    for f in images:
                        product_images.objects.create(
                            Product_id=product_id.id, Image_path=f)
                    msg = "product added successfully"
                    return render(request, 'addproduct.html', {'msg': msg})
                else:
                    msg = "product added successfully"
                    return render(request, 'addproduct.html', {'msg': msg})
            else:
                exist_msg = "Product already exist"
                return render(request, 'addproduct.html', {'exist_msg': exist_msg})
        else:
            cate = Category.objects.all()
            return render(request, 'addproduct.html', {'cate': cate})
    else:
        return redirect('/')


def delete_data(request):
    if request.user.is_superuser:
        delete_id = request.GET.get('id')
        all_data = product.objects.get(id=delete_id)
        sub_image = product_images.objects.filter(Product_id=all_data.id)
        if sub_image is not None:  # check sub images of product exist or not
            for sub in sub_image:
                os.remove(sub.Image_path.path)
                sub.delete()
        os.remove(all_data.Image.path)
        all_data.delete()
        msg = "Product deleted successfully"
        return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


def upd_product(request, pk):
    if request.user.is_superuser:
        obj = get_object_or_404(product, id=pk)
        upd_data = product.objects.get(id=pk)

        if request.method == "POST":

            if request.FILES.get('file') is not None:

                os.remove(upd_data.Image.path)
                upd_data.Image = request.FILES['file']

            elif request.FILES.getlist('files') is not None:

                images = request.FILES.getlist('files')
                for f in images:
                    product_images.objects.create(Product_id=pk, Image_path=f)
            upd_data.Qty = request.POST.get('qty')
            upd_data.Rate = request.POST.get('rate')

            upd_data.Discount = request.POST.get('discount')
            if upd_data.Discount == "":
                upd_data.Discount = 0
            upd_data.Percentage = request.POST.get('percentage')
            if upd_data.Percentage == "":
                upd_data.Percentage = 0

            upd_data.Total_rate = request.POST.get('total_rate')

            top_product = request.POST.get('top_product')
            if top_product == "yes":
                upd_data.Top_product = request.POST.get('top_product')
            else:
                upd_data.Top_product = 'no'

            upd_data.per_unit = request.POST.get('units')

            finder = [upd_data.Category == request.POST.get('category'), upd_data.Name == request.POST.get('name'),
                      upd_data.Brand == request.POST.get('brand')]
            if all(finder):

                cart_p = Cart.objects.filter(Product_id=upd_data.id)
                for cat in cart_p:
                    cat.Total_rate = cat.Qty_count * upd_data.Total_rate
                    cat.Rate = cat.Qty_count * upd_data.Rate
                    cat.Discount = cat.Qty_count * upd_data.Discount
                    cat.save()

                upd_data.Name = request.POST.get('name')
                upd_data.Brand = request.POST.get('brand')
                upd_data.Category = request.POST.get('category')
                Category_id_find = Category.objects.get(id=upd_data.Category)
                if Category_id_find is not None:
                    upd_data.category_name = Category_id_find.name
                upd_data.save()
                msg_success = "Product updated successfully"
                return render(request, 'update_product.html', {'msg_success': msg_success})
            else:
                upd_data.Category = request.POST.get('category')
                Category_id_find = Category.objects.get(id=upd_data.Category)
                if Category_id_find is not None:
                    upd_data.category_name = Category_id_find.name
                upd_data.Name = request.POST.get('name')
                upd_data.Brand = request.POST.get('brand')

                if not product.objects.filter(Name=upd_data.Name, Brand=upd_data.Brand,
                                              Category=upd_data.Category).exists():

                    cart_p = Cart.objects.filter(Product_id=upd_data.id)
                    for cat in cart_p:
                        cat.Total_rate = cat.Qty_count * upd_data.Total_rate
                        cat.Rate = cat.Qty_count * upd_data.Rate
                        cat.Discount = cat.Qty_count * upd_data.Discount
                        cat.save()
                    upd_data.save()
                    msg_success = "Product updated successfully"
                    return render(request, 'update_product.html', {'msg_success': msg_success})
                else:
                    msg_error = "Updating Data Already Exist"
                    return render(request, 'update_product.html', {'msg_error': msg_error})
        else:
            ft_data = product.objects.get(id=pk)
            selected_cat = Category.objects.get(id=upd_data.Category)
            images_data = product_images.objects.filter(Product_id=pk)
            cate = Category.objects.all()
            context = {'ft_data': ft_data, 'obj': obj, 'images_data': images_data,
                       'cate': cate, 'selected_cat': selected_cat}
            return render(request, 'update_product.html', context)
    else:
        return redirect('/')


def delete_product_img(request):
    if request.user.is_superuser:
        delete_id = request.GET.get('id')
        z = product_images.objects.get(id=delete_id)
        os.remove(z.Image_path.path)
        z.delete()
        msg = "Image deleted"
        return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


def delete_category(request):
    if request.user.is_superuser:
        delete_cat_id = request.GET.get('id')
        all_data = Category.objects.get(id=delete_cat_id)
        pid = product.objects.filter(Category=delete_cat_id)
        if pid is not None:
            for p_id in pid:
                if p_id.Category == delete_cat_id:
                    prod_image = product_images.objects.filter(
                        Product_id=p_id.id)
                    if prod_image is not None:
                        for img in prod_image:
                            os.remove(img.Image_path.path)
                            img.delete()
                        os.remove(p_id.Image.path)
                        p_id.delete()
        os.remove(all_data.image.path)
        all_data.delete()
        msg = "Category Deleted successfully"
        return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


def check_category(request):
    if request.user.is_superuser:
        delete_cat_id = request.GET.get('id')
        all_data = Category.objects.get(id=delete_cat_id)
        if product.objects.filter(Category=delete_cat_id).exists():
            msg = "Category contains products"
            return HttpResponse(json.dumps({'msg': msg}))
        else:
            os.remove(all_data.image.path)
            all_data.delete()
            msg = "Category Deleted successfully"
            return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


def upd_category(request, pk):
    if request.user.is_superuser:
        obj = get_object_or_404(Category, id=pk)
        cat_data = Category.objects.get(id=pk)
        if request.method == "POST":
            if request.FILES.get('image') is not None:
                os.remove(cat_data.image.path)
                cat_data.image = request.FILES['image']
            cat_data.name = request.POST.get('name')
            cat_data.description = request.POST.get('description')
            cat_data.save()
            msg_success = "Category Updated successfully"
            return render(request, "update_category.html", {'msg_success': msg_success})
        else:
            return render(request, 'update_category.html', {'cat_data': cat_data, 'obj': obj})
    else:
        return redirect('/')


def offers(request):
    if request.user.is_superuser:
        offr = Offers.objects.all()
        return render(request, 'offers.html', {'offr': offr})
    else:
        return redirect('/')


def add_offers(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            image = request.FILES['image']
            Offers.objects.create(image=image)
            messages.success(request, 'Offer Added successsfully')
            return render(request, 'add_offers.html')
        else:
            return render(request, 'add_offers.html')
    else:
        return redirect('/')


def view_offers(request):
    if request.user.is_superuser:
        offr = Offers.objects.all()
        return render(request, 'view_offers.html', {'offr': offr})
    else:
        return redirect('/')


def delete_offers(request):
    if request.user.is_superuser:
        delete_offer_id = request.GET.get('id')
        all_data = Offers.objects.get(id=delete_offer_id)
        all_data.delete()
        msg = "Offer Deleted successfully"
        return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


# user home

def automate_data():
    pro = product.objects.all()
    return pro


def user_home(request):
    if 'id' in request.session:
        cart_con = cart_count(request.session['id'])
        pro = automate_data()
        cat = Category.objects.all().order_by('?')
        top_product_list = product.objects.filter(
            Top_product="yes").order_by('?')
        return render(request, 'user_home.html', {'cat': cat, 'pro': pro, 'top_product_list': top_product_list, 'cart_con': cart_con})
    else:
        return redirect('/')


# view selected category products

def view_selected_products(request, pk):
    if 'id' in request.session:
        cart_con = cart_count(request.session['id'])
        sel_prod = product.objects.filter(Category=pk).order_by('?')
        if sel_prod.count() > 0:
            return render(request, 'user_product_view.html', {'sel_prod': sel_prod, 'cart_con': cart_con})
        return render(request, 'user_product_view.html', {'cart_con': cart_con})

    else:
        return redirect('/')


def user_view_product_details(request, pk):
    if 'id' in request.session:
        cart_con = cart_count(request.session['id'])
        product_det = product.objects.get(id=pk)
        product_sub_imgs = product_images.objects.filter(Product_id=pk)

        _pro_ext_cart = Cart.objects.filter(Product=pk).count()
        if _pro_ext_cart > 0:
            cart_qty = Cart.objects.get(Product=pk)
            context = {'cart_qty': cart_qty, 'product_det': product_det,
                       'product_sub_imgs': product_sub_imgs, 'cart_con': cart_con}
            return render(request, 'user_product_fulldetails.html', context)
        return render(request, 'user_product_fulldetails.html',
                      {'product_det': product_det, 'product_sub_imgs': product_sub_imgs, 'cart_con': cart_con, 'cart_qty': _pro_ext_cart})

    else:
        return redirect('/')


def autocomplete_fn(request):
    if 'term' in request.GET:
        na = product.objects.filter(Name__istartswith=request.GET.get('term'))
        titles = list()
        for prod in na:
            titles.append(prod.Name)
        return JsonResponse(titles, safe=False)
    return render(request, 'user_home.html')


# user search products

def user_search_product(request):
    if 'id' in request.session:
        cart_con = cart_count(request.session['id'])
        if request.method == "POST":
            search_data = request.POST.get('search_data')
            sel_prod = product.objects.filter(
                Name__icontains=search_data).order_by('?')
            if sel_prod.exists():
                return render(request, 'user_search_products.html', {'sel_prod': sel_prod, 'cart_con': cart_con})
        return render(request, 'user_search_products.html', {'cart_con': cart_con})
    else:
        return redirect('/')


# add to cart
def add_to_cart(request):
    if 'id' in request.session:
        uid = request.GET.get('id')
        if uid is not None:
            prod_det = product.objects.get(id=uid)
            userid = request.session['id']
            Any_ext = Cart.objects.filter(
                User_id=userid, Product_id=prod_det.id)
            if Any_ext:
                ord = Cart.objects.get(User_id=userid, Product_id=prod_det.id)
                ord.Qty_count = ord.Qty_count + 1
                ord.Rate = prod_det.Rate * ord.Qty_count
                ord.Discount = prod_det.Discount * ord.Qty_count
                ord.Total_rate = prod_det.Total_rate * ord.Qty_count
                ord.save()
                msg = "Product added to cart!"
                return HttpResponse(json.dumps({'msg': msg}))
            else:
                a = Cart.objects.create(
                    User_id=userid, Product_id=prod_det.id, Qty_count=1, Rate=prod_det.Rate,
                    Discount=prod_det.Discount, Total_rate=prod_det.Total_rate)
                if a is not None:
                    msg = "Product added to cart"
                    return HttpResponse(json.dumps({'msg': msg}))
                else:
                    msg = "Something went wrong"
                    return HttpResponse(json.dumps({'msg': msg}))
        else:
            msg = "Something went wrong"
            return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


# cart view
def cart_view(request):
    if 'id' in request.session:
        userid = request.session['id']
        cart_data = Cart.objects.filter(User_id=userid)
        pro_data = product.objects.all()
        cart_con = cart_count(request.session['id'])
        if request.method == "POST":
            address = request.POST.get('address')
            status = "ordered"
            cart_counts = Cart.objects.filter(User_id=userid)
            for order in cart_counts:
                pro_det = product.objects.get(id=order.Product_id)
                My_order.objects.create(User_id=userid, Product_id=pro_det.id, Product_name=pro_det.Name,
                                        Brand=pro_det.Brand, Category=pro_det.category_name, Qty_count=order.Qty_count,
                                        Rate=order.Rate, Discount=order.Discount, Total_rate=order.Total_rate,
                                        Status=status, Booking_address=address)
            Cart.objects.filter(User_id=userid).delete()
            order_msg = "Order confirmed"
            return render(request, 'cart.html', {'order_msg': order_msg})

        else:
            count = cart_data.count()
            total_rate = Cart.objects.filter(
                User_id=userid).aggregate(tot=Sum('Total_rate'))
            total_rate = total_rate['tot']
            rate = Cart.objects.filter(
                User_id=userid).aggregate(rate=Sum('Rate'))
            rate = rate['rate']
            discount = Cart.objects.filter(
                User_id=userid).aggregate(discount=Sum('Discount'))
            discount = discount['discount']
            user_data = UserDetails.objects.get(id=userid)
            context = {'cart_data': cart_data, 'pro_data': pro_data, 'count': count, 'total_rate': total_rate, 'rate': rate, 'discount': discount,
                       'user_data': user_data, 'cart_con': cart_con}
            return render(request, 'cart.html', context)

    else:
        return redirect('/')


# delete cart

def delete_cart(request):
    if 'id' in request.session:
        cart_id = request.GET.get('id')
        if cart_id is not None:
            del_cart = Cart.objects.get(id=cart_id)
            del_cart.delete()
            msg = "Selected product deleted from cart"
            return HttpResponse(json.dumps({'msg': msg}))
        else:
            msg = "something went wrong "
            return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


# increment qty of selected product

def increment_cart(request):
    if 'id' in request.session:
        inc_id = request.GET.get('id')
        if inc_id is not None:

            userid = request.session['id']

            cart_id = Cart.objects.get(id=inc_id)
            prod_det = product.objects.get(id=cart_id.Product_id)
            cart_id.Qty_count = cart_id.Qty_count + 1
            cart_id.Total_rate = prod_det.Total_rate * cart_id.Qty_count
            cart_id.Rate = prod_det.Rate * cart_id.Qty_count
            cart_id.Discount = prod_det.Discount * cart_id.Qty_count
            cart_id.save()

            tot = cart_id.Total_rate
            rat = cart_id.Rate
            dis = cart_id.Discount
            # find total_rate, discount and rate
            total_rate = Cart.objects.filter(
                User_id=userid).aggregate(tot=Sum('Total_rate'))
            total_rate = total_rate['tot']
            rate = Cart.objects.filter(
                User_id=userid).aggregate(rate=Sum('Rate'))
            rate = rate['rate']
            discount = Cart.objects.filter(
                User_id=userid).aggregate(discount=Sum('Discount'))
            discount = discount['discount']

            qty_count = cart_id.Qty_count
            return HttpResponse(json.dumps({'qty_count': qty_count, 'total_rate': total_rate, 'rate': rate, 'discount': discount, 'tot': tot, 'rat': rat, 'dis': dis}))
        else:
            msg = "Product added to cart"
            return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')

# decrement qty of selected product


def decrement_cart(request):
    if 'id' in request.session:
        dec_id = request.GET.get('id')
        userid = request.session['id']

        if dec_id is not None:
            cart_id = Cart.objects.get(id=dec_id)
            prod_det = product.objects.get(id=cart_id.Product_id)

            cart_id.Qty_count = cart_id.Qty_count - 1
            cart_id.Total_rate = prod_det.Total_rate * cart_id.Qty_count
            cart_id.Rate = prod_det.Rate * cart_id.Qty_count
            cart_id.Discount = prod_det.Discount * cart_id.Qty_count
            cart_id.save()

            tot = cart_id.Total_rate
            rat = cart_id.Rate
            dis = cart_id.Discount

            qty_count = cart_id.Qty_count

            # find total_rate, discount and rate
            total_rate = Cart.objects.filter(
                User_id=userid).aggregate(tot=Sum('Total_rate'))
            total_rate = total_rate['tot']
            rate = Cart.objects.filter(
                User_id=userid).aggregate(rate=Sum('Rate'))
            rate = rate['rate']
            discount = Cart.objects.filter(
                User_id=userid).aggregate(discount=Sum('Discount'))
            discount = discount['discount']
            return HttpResponse(json.dumps({'qty_count': qty_count, 'total_rate': total_rate, 'rate': rate, 'discount': discount, 'tot': tot, 'rat': rat, 'dis': dis}))
        else:
            msg = "Product added to cart"
            return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


# Aishwarya's

def user_test_details(request):
    if 'id' in request.session:
        user_data = UserDetails.objects.get(id=request.session['id'])
        return render(request, 'user_test_details.html', {'user_data': user_data})
    else:
        messages.success(request, "User not logged in")
        return redirect('/')


def edit_user_profile(request):
    if 'id' in request.session:
        user_data = UserDetails.objects.get(id=request.session['id'])

        if request.method == 'POST':

            if request.FILES.get('files') is not None:
                if not user_data.image == "/static/images/fav_rm.png":
                    os.remove(user_data.image.path)
                    user_data.image = request.FILES['files']
                else:
                    user_data.image = request.FILES['files']

            if request.POST.get('username') is not None:
                user_name = request.POST.get('username')
                if user_data.username == user_name:
                    user_data.username = user_name
                else:
                    if UserDetails.objects.filter(username=user_name).exists():
                        msg_error = "Username already Exists"
                        return render(request, 'edit_user_profile.html', {'msg_error': msg_error})
                    else:
                        user_data.username = user_name

            if request.POST.get('email') is not None:
                email_user = request.POST.get('email')
                if user_data.user_email == email_user:
                    user_data.user_email = email_user
                else:
                    if UserDetails.objects.filter(user_email=email_user).exists():
                        msg_error = "Email already exists"
                        return render(request, 'edit_user_profile.html', {'msg_error': msg_error})
                    else:
                        user_data.user_email = email_user

            user_data.full_name = request.POST.get('name')
            user_data.mobile = request.POST.get('mobile')
            user_data.address = request.POST.get('address')

            user_data.save()

            msg_success = "Profile updated successfully"
            return render(request, 'edit_user_profile.html', {'msg_success': msg_success})

        user_data1 = UserDetails.objects.filter(id=request.session['id'])
        return render(request, 'edit_user_profile.html', {'user_data': user_data1})

    else:
        messages.info(request, "User not logged in")
        return redirect('/')


def user_reset_password(request):
    if 'id' in request.session:
        user_data = UserDetails.objects.get(id=request.session['id'])
        if request.method == 'POST':
            password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')
            if password == confirm_password:
                user_data.password = password
                user_data.save()
                msg_success = "Password has been changed successfully"
                return render(request, 'user_reset_password.html', {'msg_success': msg_success})
            else:
                msg_error = "Password does not match"
                return render(request, 'user_reset_password.html', {'msg_error': msg_error})
        else:
            user_data1 = UserDetails.objects.filter(id=request.session['id'])
            return render(request, 'user_reset_password.html', {'user_data': user_data1})
    else:
        return redirect('/')


def user_delete_session(request):
    try:
        del request.session['id']
        # request.session.set_expiry(0.0001)
        request.session.flush()
        messages.info(request, "You have successfully logged out")
        return redirect('/')
    except KeyError:
        messages.info(request, "User not logged in")
        return redirect('/')


def user_signup(request):
    if request.user.is_superuser:
        return redirect('home')
    elif 'id' in request.session:
        return redirect('user_home')
    else:
        if request.method == 'POST':

            if request.FILES.get('files') is not None:
                image = request.FILES['files']
            else:
                image = "/static/images/fav_rm.png"

            if request.POST.get('username') is not None:
                user_name = request.POST.get('username')
                if UserDetails.objects.filter(username=user_name).exists():
                    msg_error = "Username already exists"
                    return render(request, 'user_signup.html', {'msg_error': msg_error})
                else:
                    user_name = request.POST.get('username')

            if request.POST.get('email') is not None:
                email_user = request.POST.get('email')
                if UserDetails.objects.filter(user_email=email_user).exists():
                    msg_error = "Email already exists"
                    return render(request, 'user_signup.html', {'msg_error': msg_error})
                else:
                    email_user = request.POST.get('email')

                    name = request.POST.get('name')
                    mobile = request.POST.get('mobile')
                    address = request.POST.get('address')
                    password = request.POST.get('password1')
                    confirm_password = request.POST.get('password2')

                    if password != confirm_password:
                        msg_error = "Password does not match"
                        return render(request, 'user_signup.html', {'msg_error': msg_error})

                    UserDetails.objects.create(full_name=name, mobile=mobile, address=address, user_email=email_user,
                                               username=user_name, image=image, password=password)
                    # messages.info(request, "Your account has been created successfully")

                    user_test = UserDetails.objects.get(
                        username=user_name, password=password)

                    request.session['id'] = user_test.id
                    # dd = request.session['name']
                    user_new = UserDetails.objects.filter(
                        id=request.session['id'])

                    return redirect('user_signup')

        else:
            return render(request, 'user_signup.html')


# Akhil raj m r

# this page show selected user orders
def admin_view_user_order(request, pk):
    if request.user.is_superuser:
        if 'cancel' in request.POST:
            booking_id = request.POST.get('bookid')
            message = request.POST.get('message')
            user_data = My_order.objects.get(id=booking_id)
            user_data.Message = message
            user_data.Status = 'canceled'
            user_data.save()
            msg = "Order canceled"
            return render(request, 'admin_orders.html', {'msg': msg})

        elif 'confirm' in request.POST:
            confid = request.POST.get('confid')
            expt_time = request.POST.get('expt_time')
            user_data = My_order.objects.get(id=confid)
            user_data.Message = expt_time
            user_data.Status = 'Packed'
            user_data.save()
            msg = "Order Confirmed"
            return render(request, 'admin_orders.html', {'msg': msg})

        elif 'delivery' in request.POST:
            d_id = request.POST.get('ord_id')
            user_data = My_order.objects.get(id=d_id)
            user_data.Status = 'Delivered'
            user_data.save()
            msg = "Delivered"
            return render(request, 'admin_orders.html', {'msg': msg})
        else:
            orders = My_order.objects.filter(
                ~Q(Status="canceled"), ~Q(Status="Delivered"), User_id=pk)
            pro_data = product.objects.all()
            user_data = UserDetails.objects.all()
            return render(request, 'admin_orders.html',
                          {'orders': orders, 'pro_data': pro_data, 'user_data': user_data})
    else:
        return redirect('/')


# user myorder view

def user_myorder(request):
    if 'id' in request.session:
        if 'cancel' in request.POST:
            booking_id = request.POST.get('bookid')
            user_data = My_order.objects.get(id=booking_id)
            user_data.Status = 'canceled'
            user_data.save()
            msg_cancel = "order canceled"
            return render(request, 'myorders.html', {'msg_cancel': msg_cancel})
        else:
            cart_con = cart_count(request.session['id'])
            orders = My_order.objects.filter(
                User_id=request.session['id']).order_by('-id')
            pro_data = product.objects.all()
            user_data = UserDetails.objects.all()
            admin_num = AdminDetails.objects.get(id=1)
            admin_number = admin_num.Mobile
            return render(request, 'myorders.html', {'orders': orders, 'pro_data': pro_data, 'admin_number': admin_number, 'cart_con': cart_con})
    else:
        return redirect('/')


# view canceled or deliverd order users
def order_history(request):
    if request.user.is_superuser:
        orders = My_order.objects.filter(Status="Delivered").order_by('-id')
        pro_data = product.objects.all()
        return render(request, 'order_history.html',
                      {'orders': orders, 'pro_data': pro_data})
    else:
        return redirect('/')


# find counter of orders

def order_counter(request):
    if request.user.is_superuser:
        orders = My_order.objects.filter(
            ~Q(Status="Delivered"), ~Q(Status="canceled")).count()
        msg = orders
        return HttpResponse(json.dumps({'msg': msg}))
    else:
        return redirect('/')


# reset password

def forgot_password(request):
    if request.method == "POST":
        email_id = request.POST.get('email')
        access_user_data = UserDetails.objects.filter(
            user_email=email_id).exists()
        if access_user_data:
            _user = UserDetails.objects.get(user_email=email_id)
            password = random.SystemRandom().randint(100000, 999999)

            _user.password = password
            subject = 'Akhil Raj django project Password Reset'
            message = 'Password Reset Successfully\n\nYour login details are below\n\nUsername : ' + str(_user.username) + '\n\nPassword : ' + str(password) + \
                '\n\nYou can login this details'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email_id, ]
            send_mail(subject, message, email_from,
                      recipient_list, fail_silently=False)

            _user.save()
            msg_success = "Password Reset successfully check your mail new password"
            return render(request, 'forgot_password.html', {'msg_success': msg_success})
        else:
            msg_error = "Email id does not Exist in the table"
            return render(request, 'forgot_password.html', {'msg_error': msg_error})
    else:
        return render(request, 'forgot_password.html')


# cart_count find

def find_cart_count(request):
    if 'id' in request.session:
        cart_con = cart_count(request.session['id'])
        context = {
            'cart_con': cart_con
        }
        return HttpResponse(json.dumps(context))
    else:
        return redirect('/')
