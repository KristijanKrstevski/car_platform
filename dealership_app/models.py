import json
from django.db import models


class CarBrand(models.Model):
    name = models.CharField("Марка", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField("Модел", max_length=100)

    class Meta:
        unique_together = ("brand", "name")
        ordering = ["brand__name", "name"]

    def __str__(self):
        return f"{self.name}"


class CarEquipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Car(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField("Наслов", max_length=200)
    year = models.PositiveSmallIntegerField("Година на производство")
    description = models.TextField("Опис", blank=True)

    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизел'),
        ('electric', 'Електричен'),
        ('ethanol', 'Етанол'),
        ('methane', 'Метан'),
        ('lpg', 'Плин/Бензин'),
        ('hybrid_petrol', 'Хибрид/Бензин'),
        ('hybrid_diesel', 'Хибрид/Дизел'),
    ]
    fuel_type = models.CharField("Тип на гориво", max_length=20, choices=FUEL_CHOICES)

    TRANSMISSION_CHOICES = [
        ('manual', 'Рачен'),
        ('automatic', 'Автоматски'),
        ('other', 'Друго'),
    ]
    transmission = models.CharField("Менувач", max_length=20, choices=TRANSMISSION_CHOICES)

    BODY_CHOICES = [
        ('compact', 'Мал автомобил'),
        ('sedan', 'Седан'),
        ('hatchback', 'Хеџбек'),
        ('wagon', 'Караван'),
        ('coupe', 'Купе'),
        ('cabriolet', 'Кабриолет'),
        ('suv', 'Теренско'),
        ('minivan', 'Миниван'),
    ]
    body_type = models.CharField("Тип на каросерија", max_length=20, choices=BODY_CHOICES)

    REGISTRATION_CHOICES = [
        ('mk', 'Македонска'),
        ('foreign', 'Странска'),
        ('none', 'Останува да се регистрира'),
        ('other', 'Друго'),
    ]
    registration_type = models.CharField("Регистрација", max_length=20, choices=REGISTRATION_CHOICES)

    engine_capacity = models.PositiveIntegerField("Кубикажа (cm³)", null=True, blank=True)

    kilowatts = models.PositiveIntegerField("Киловати")
    price = models.PositiveIntegerField("Цена (во евра)")
    sold = models.BooleanField("Продадено", default=False)

    MILEAGE_CHOICES = [
        ('5000', '5.000 km'),
        ('10000', '10.000 km'),
        ('15000', '15.000 km'),
        ('20000', '20.000 km'),
        ('25000', '25.000 km'),
        ('30000', '30.000 km'),
        ('35000', '35.000 km'),
        ('40000', '40.000 km'),
        ('45000', '45.000 km'),
        ('50000', '50.000 km'),
        ('55000', '55.000 km'),
        ('60000', '60.000 km'),
        ('65000', '65.000 km'),
        ('70000', '70.000 km'),
        ('75000', '75.000 km'),
        ('80000', '80.000 km'),
        ('85000', '85.000 km'),
        ('90000', '90.000 km'),
        ('95000', '95.000 km'),
        ('100000', '100.000 km'),
        ('110000', '110.000 km'),
        ('120000', '120.000 km'),
        ('130000', '130.000 km'),
        ('140000', '140.000 km'),
        ('150000', '150.000 km'),
        ('160000', '160.000 km'),
        ('170000', '170.000 km'),
        ('180000', '180.000 km'),
        ('190000', '190.000 km'),
        ('200000', '200.000 km'),
        ('210000', '210.000 km'),
        ('220000', '220.000 km'),
        ('230000', '230.000 km'),
        ('240000', '240.000 km'),
        ('250000', '250.000 km'),
        ('260000', '260.000 km'),
        ('270000', '270.000 km'),
        ('280000', '280.000 km'),
        ('290000', '290.000 km'),
        ('300000', '300.000 km'),
        ('310000', '310.000 km'),
        ('320000', '320.000 km'),
        ('330000', '330.000 km'),
        ('340000', '340.000 km'),
        ('350000', '350.000 km'),
        ('360000', '360.000 km'),
        ('370000', '370.000 km'),
        ('380000', '380.000 km'),
        ('390000', '390.000 km'),
        ('400000', '400.000 km'),
        ('410000', '410.000 km'),
        ('420000', '420.000 km'),
        ('430000', '430.000 km'),
        ('440000', '440.000 km'),
        ('450000', '450.000 km'),
        ('other', 'Друго'),
    ]
    mileage = models.CharField("Километража", max_length=20, choices=MILEAGE_CHOICES)

    COLOR_CHOICES = [
        ('black', 'Црна'),
        ('white', 'Бела'),
        ('gray', 'Сива'),
        ('red', 'Црвена'),
        ('green', 'Зелена'),
        ('blue', 'Сина'),
        ('yellow', 'Жолта'),
        ('orange', 'Портокалова'),
        ('brown', 'Кафеава'),
        ('gold', 'Златна'),
        ('purple', 'Виолетова'),
        ('other', 'Друго'),
    ]
    color = models.CharField("Боја", max_length=20, choices=COLOR_CHOICES)

    SEATS_CHOICES = [
        ('3', '3 седишта'),
        ('5', '5 седишта'),
        ('7', '7 седишта'),
    ]
    seats = models.CharField("Број на седишта", max_length=2, choices=SEATS_CHOICES)

    equipment = models.ManyToManyField(CarEquipment, blank=True)

    main_image = models.ImageField("Главна слика", upload_to='cars/main_images/')

    created_at = models.DateTimeField("Креирано", auto_now_add=True)


    def display_price(self):
        return "По договор" if self.price == 0 else f"{self.price} €"

    def __str__(self):
        return self.title

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='cars/extra_images/')

    def __str__(self):
        return f"Image for {self.car.title}"
