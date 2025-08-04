import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Car, CarBrand, CarModel

def index(request):
    featured_cars = Car.objects.filter(sold=False).order_by('-created_at')[:6]
    return render(request, 'frontend/index.html', {'featured_cars': featured_cars})

def ajax_models(request):
    """Return JSON list of {id,name} for models of given brand."""
    brand_id = request.GET.get('brand')
    models = []
    if brand_id and brand_id.isdigit():
        qs = CarModel.objects.filter(brand_id=brand_id).order_by('name')
        models = [{'id': m.id, 'name': m.name} for m in qs]
    return JsonResponse(models, safe=False)

def vehicle_list(request):
    qs = Car.objects.filter(sold=False)

    # -- Filters --
    brand    = request.GET.get('brand')
    model_id = request.GET.get('model_name')
    trans    = request.GET.get('transmission')
    body     = request.GET.get('vehicle_body')
    fuel     = request.GET.get('fuel')
    color    = request.GET.get('color')
    beginners= request.GET.get('for_beginners')

    if brand:
        qs = qs.filter(brand_id=brand)
    if model_id:
        qs = qs.filter(model_name_id=model_id)
    if trans:
        qs = qs.filter(transmission=trans)
    if body:
        qs = qs.filter(body_type=body)
    if fuel:
        qs = qs.filter(fuel_type=fuel)
    if color:
        qs = qs.filter(color=color)
    if beginners:
        qs = qs.filter(kilowatts__lte=77)

    # -- Sorting in-panel --
    sort_price   = request.GET.get('sort_price')
    sort_mileage = request.GET.get('sort_mileage')
    sort_year    = request.GET.get('sort_year')

    # apply only one sort: priority price > mileage > year
    if sort_price in ['asc','desc']:
        qs = qs.order_by('price' if sort_price=='asc' else '-price')
    elif sort_mileage in ['asc','desc']:
        qs = qs.order_by('mileage' if sort_mileage=='asc' else '-mileage')
    elif sort_year in ['asc','desc']:
        qs = qs.order_by('year' if sort_year=='asc' else '-year')
    else:
        qs = qs.order_by('-created_at')

    # -- Pagination --
    paginator = Paginator(qs, 9)
    page = request.GET.get('page')
    cars = paginator.get_page(page)

    # models for the initial brand
    models_qs = CarModel.objects.filter(brand_id=brand).order_by('name') if brand else []

    return render(request, 'frontend/vehicles.html', {
        'cars': cars,
        'brands': CarBrand.objects.all(),
        'models': models_qs,
        'transmission_choices': Car.TRANSMISSION_CHOICES,
        'fuel_choices':        Car.FUEL_CHOICES,
        'vehicle_bodies':      Car.BODY_CHOICES,
        'colors':              Car.COLOR_CHOICES,
    })

def vehicle_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'frontend/vehicle_detail.html', {'car': car})
