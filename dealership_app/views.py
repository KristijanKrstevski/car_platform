import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Car, CarImage, CarEquipment,CarModel
from .forms import CarModelForm, CarImageForm
from django.db.models import Avg, Sum, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.contrib.auth.decorators import login_required



# ✅ DASHBOARD HOME
def admin_dashboard(request):
    # Check if user is authenticated, if not redirect to admin login
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=/dashboard/')
    total_cars = Car.objects.count()
    total_sold = Car.objects.filter(sold=True).count()

    # 1. Просечна цена на сите возила
    avg_price = Car.objects.aggregate(avg=Avg('price'))['avg'] or 0

    # 2. Просечна цена на продадените
    avg_price_sold = Car.objects.filter(sold=True).aggregate(avg=Avg('price'))['avg'] or 0

    # 3. Вредност на непродадени (инвентарио)
    inventory_value = Car.objects.filter(sold=False).aggregate(total=Sum('price'))['total'] or 0

    # 4. Просечна цена по година на производство
    current_year = timezone.now().year
    age_price_expr = ExpressionWrapper(
        F('price') / (current_year - F('year') + 1),
        output_field=FloatField()
    )
    avg_price_per_year = Car.objects.annotate(age_price=age_price_expr).aggregate(avg=Avg('age_price'))['avg'] or 0

    # 5. Распределба по тип на гориво
    fuel_data = Car.objects.values('fuel_type').annotate(count=Count('id')).order_by()
    fuel_labels = [item['fuel_type'] for item in fuel_data]
    fuel_counts = [item['count'] for item in fuel_data]

    # 6. Latest added cars
    latest_cars = Car.objects.select_related('brand', 'model_name').order_by('-created_at')[:5]
    
    # 7. Calculate available cars for the chart
    available_cars = total_cars - total_sold

    return render(request, "admin_custom/dashboard.html", {
        "total_cars": total_cars,
        "total_sold": total_sold,
        "available_cars": available_cars,
        "avg_price": round(avg_price, 2),
        "avg_price_sold": round(avg_price_sold, 2),
        "inventory_value": inventory_value,
        "avg_price_per_year": round(avg_price_per_year, 2),
        "fuel_labels": fuel_labels,
        "fuel_counts": fuel_counts,
        "latest_cars": latest_cars,
    })



# ✅ LIST CARS
def admin_car_list(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=' + request.path)
    
    # Get filter parameters
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', '-created_at')
    
    # Base queryset with related objects for optimization
    cars = Car.objects.select_related('brand', 'model_name').all()
    
    # Apply search filter
    if q:
        cars = cars.filter(
            Q(title__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(model_name__name__icontains=q)
        )
    
    # Apply status filter
    if status == 'available':
        cars = cars.filter(sold=False)
    elif status == 'sold':
        cars = cars.filter(sold=True)
    
    # Apply sorting
    if sort:
        if sort == 'brand':
            cars = cars.order_by('brand__name', 'model_name__name')
        else:
            cars = cars.order_by(sort)
    else:
        cars = cars.order_by('-created_at')
    
    # Calculate statistics
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(sold=False).count()
    sold_cars = Car.objects.filter(sold=True).count()
    avg_price = Car.objects.aggregate(avg=Avg('price'))['avg'] or 0
    
    # Pagination
    paginator = Paginator(cars, 12)  # Show 12 cars per page for better grid layout
    page = request.GET.get('page')
    cars = paginator.get_page(page)
    
    return render(request, 'admin_custom/car_list.html', {
        'cars': cars,
        'q': q,
        'status': status,
        'sort': sort,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'sold_cars': sold_cars,
        'avg_price': round(avg_price, 2),
    })

# ✅ ADD CAR
def admin_car_add(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == "POST":
        car_form = CarModelForm(request.POST, request.FILES)
        image_form = CarImageForm(request.POST, request.FILES)
        files = request.FILES.getlist("images")

        # Debug: log received files
        print("DEBUG: files sent →", files)

        # **Debug: show form validity and errors**
        is_valid = car_form.is_valid()
        print("DEBUG: car_form.is_valid() →", is_valid)
        if not is_valid:
            print("DEBUG: car_form.errors →", car_form.errors)

        if is_valid:
            car = car_form.save()
            car.equipment.set(request.POST.getlist("equipment"))

            for f in files:
                print(f"DEBUG: saving image → {f}")
                CarImage.objects.create(car=car, image=f)

            messages.success(request, "✅ Car added successfully!")
            return redirect("admin_car_list")
        else:
            messages.error(request, "❌ Please fix the errors below.")
    else:
        car_form = CarModelForm()
        image_form = CarImageForm()

    return render(request, "admin_custom/car_form.html", {
        "form": car_form,
        "image_form": image_form,
        "images": [],
        "all_equipment": CarEquipment.objects.all(),
        "selected_equipment": [],
        "initial_model": "",
    })


# ✅ EDIT CAR
def admin_car_edit(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=' + request.path)
    car = get_object_or_404(Car, pk=pk)
    images = CarImage.objects.filter(car=car)

    if request.method == "POST":
        car_form = CarModelForm(request.POST, request.FILES, instance=car)
        image_form = CarImageForm(request.POST, request.FILES)
        files = request.FILES.getlist("images")

        # Debug: log received files
        print("DEBUG: files sent →", files)

        # **Debug: show form validity and errors**
        is_valid = car_form.is_valid()
        print("DEBUG: car_form.is_valid() →", is_valid)
        if not is_valid:
            print("DEBUG: car_form.errors →", car_form.errors)

        if is_valid:
            car = car_form.save()
            car.equipment.set(request.POST.getlist("equipment"))

            for f in files:
                print(f"DEBUG: saving image → {f}")
                CarImage.objects.create(car=car, image=f)

            messages.success(request, "✅ Car updated successfully!")
            return redirect("admin_car_edit", pk=car.pk)
        else:
            messages.error(request, "❌ Please fix the errors below.")
    else:
        car_form = CarModelForm(instance=car)
        image_form = CarImageForm()

    return render(request, "admin_custom/car_form.html", {
        "form": car_form,
        "image_form": image_form,
        "car": car,
        "images": images,
        "all_equipment": CarEquipment.objects.all(),
        "selected_equipment": car.equipment.all(),
        "initial_model": car.model_name_id or "",
    })


# ✅ AJAX DELETE IMAGE (No refresh)
def ajax_delete_car_image(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=401)
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        img = get_object_or_404(CarImage, id=pk)
        car_id = img.car.id  # CarImage must have a ForeignKey to Car
        if img.image and os.path.isfile(img.image.path):
            os.remove(img.image.path)
        img.delete()
        remaining = CarImage.objects.filter(car_id=car_id).count()
        return JsonResponse({"success": True, "remaining": remaining})
    return JsonResponse({"success": False}, status=400)

# ✅ DELETE CAR
def admin_car_delete(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/?next=' + request.path)
    car = get_object_or_404(Car, pk=pk)
    extra_images = CarImage.objects.filter(car=car)
    for img in extra_images:
        if img.image and os.path.isfile(img.image.path):
            os.remove(img.image.path)
        img.delete()
    if car.main_image and os.path.isfile(car.main_image.path):
        os.remove(car.main_image.path)
    car.delete()
    messages.success(request, "🗑 Car and all its images deleted!")
    return redirect("admin_car_list")

def ajax_load_models(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "Authentication required"}, status=401)
    bid = request.GET.get('brand')
    qs = CarModel.objects.filter(brand_id=bid).values('id','name')
    return JsonResponse(list(qs), safe=False)