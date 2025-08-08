import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Car, CarBrand, CarModel

def index(request):
    # Get more cars for a better carousel experience (8-10 cars)
    featured_cars = Car.objects.filter(sold=False).order_by('-created_at')[:10]
    # Only show brands that have available cars
    brands = CarBrand.objects.filter(car__sold=False).distinct().order_by('name')
    
    # Get only fuel choices that exist in available cars for the search form
    base_qs = Car.objects.filter(sold=False)
    available_fuels = base_qs.values_list('fuel_type', flat=True).distinct()
    fuel_choices = [(key, label) for key, label in Car.FUEL_CHOICES if key in available_fuels]
    
    return render(request, 'frontend/index.html', {
        'featured_cars': featured_cars,
        'brands': brands,
        'fuel_choices': fuel_choices,
    })

def ajax_models(request):
    """Return JSON list of {id,name} for models of given brand that have available cars."""
    brand_id = request.GET.get('brand')
    models = []
    if brand_id and brand_id.isdigit():
        # Only show models that have available cars for this brand
        qs = CarModel.objects.filter(
            brand_id=brand_id,
            car__sold=False
        ).distinct().order_by('name')
        models = [{'id': m.id, 'name': m.name} for m in qs]
    return JsonResponse(models, safe=False)

def vehicle_list(request):
    base_qs = Car.objects.filter(sold=False)
    qs = base_qs

    # -- Filters --
    brand       = request.GET.get('brand')
    model_id    = request.GET.get('model_name') or request.GET.get('model')
    trans       = request.GET.get('transmission')
    body        = request.GET.get('vehicle_body') or request.GET.get('body_type')
    fuel        = request.GET.get('fuel')
    color       = request.GET.get('color')
    beginners   = request.GET.get('for_beginners')
    price_from  = request.GET.get('price_from')
    price_to    = request.GET.get('price_to')
    year_from   = request.GET.get('year_from')
    
    # New sorting options
    sort_price   = request.GET.get('sort_price')
    sort_mileage = request.GET.get('sort_mileage')  
    sort_year    = request.GET.get('sort_year')

    # Track if any filters are applied
    filters_applied = any([brand, model_id, trans, body, fuel, color, beginners, 
                          price_from, price_to, year_from])

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
    
    # Price range filtering
    if price_from and price_from.isdigit():
        qs = qs.filter(price__gte=int(price_from))
    if price_to and price_to.isdigit():
        qs = qs.filter(price__lte=int(price_to))
    
    # Year filtering
    if year_from and year_from.isdigit():
        qs = qs.filter(year__gte=int(year_from))

    # If filters applied but no results, show all cars
    if filters_applied and not qs.exists():
        qs = base_qs
        no_results_fallback = True
    else:
        no_results_fallback = False

    # -- Sorting --
    if sort_price in ['asc','desc']:
        qs = qs.order_by('price' if sort_price=='asc' else '-price')
    elif sort_mileage in ['asc','desc']:
        qs = qs.order_by('mileage' if sort_mileage=='asc' else '-mileage')
    elif sort_year in ['asc','desc']:
        qs = qs.order_by('year' if sort_year=='asc' else '-year')
    else:
        qs = qs.order_by('-created_at')

    # -- Pagination --
    paginator = Paginator(qs, 12)  # Show 12 cars per page
    page = request.GET.get('page')
    cars = paginator.get_page(page)

    # models for the initial brand - only show models with available cars
    models_qs = CarModel.objects.filter(
        brand_id=brand,
        car__sold=False
    ).distinct().order_by('name') if brand else []

    # Get only choices that exist in available cars
    available_transmissions = base_qs.values_list('transmission', flat=True).distinct()
    transmission_choices = [(key, label) for key, label in Car.TRANSMISSION_CHOICES if key in available_transmissions]
    
    available_fuels = base_qs.values_list('fuel_type', flat=True).distinct()
    fuel_choices = [(key, label) for key, label in Car.FUEL_CHOICES if key in available_fuels]
    
    available_bodies = base_qs.values_list('body_type', flat=True).distinct()
    vehicle_bodies = [(key, label) for key, label in Car.BODY_CHOICES if key in available_bodies]

    return render(request, 'frontend/vehicles.html', {
        'cars': cars,
        # Only show brands that have available cars
        'brands': CarBrand.objects.filter(car__sold=False).distinct().order_by('name'),
        'models': models_qs,
        'transmission_choices': transmission_choices,
        'fuel_choices':        fuel_choices,
        'vehicle_bodies':      vehicle_bodies,
        'colors':              Car.COLOR_CHOICES,
        'no_results_fallback': no_results_fallback,
    })

def vehicle_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'frontend/vehicle_detail.html', {'car': car})

def about(request):
    return render(request, 'frontend/about.html')

def contact(request):
    return render(request, 'frontend/contact.html')
