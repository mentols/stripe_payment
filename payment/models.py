from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import Profile


class Order(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order_name = models.CharField(max_length=25, default="basket")
    total_amount = models.IntegerField(default=0)  # cents
    currency = models.CharField(max_length=3, default='usd')

    def get_current_currency(self, items) -> bool:
        try:
            current_currency = items[0].currency
        except:
            current_currency = self.currency
        flag = bool([False for item in items if item.currency != current_currency])
        flag = True if not flag else False
        self.currency = current_currency
        self.save()
        return flag

    def get_tax(self) -> object:
        try:
            return Tax.objects.get(order=self)
        except:
            return 0

    def get_discount(self) -> object:
        try:
            return Discount.objects.get(order=self)
        except:
            return 0

    def get_display_price(self) -> str:
        return "{0:.2f}".format(self.total_amount / 100)

    def __str__(self):
        return f'{self.profile.user.username}\'s {self.order_name}'


class Item(models.Model):
    class CurrencyChoices(models.TextChoices):
        USD = 'usd', _('Dollars')
        EUR = 'eur', _('Euro')
        RUB = 'rub', _('Rubles')

    product_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    currency = models.TextField(choices=CurrencyChoices.choices, default=CurrencyChoices.USD)

    def get_display_price(self) -> str:
        return "{0:.2f}".format(self.price / 100)

    def get_discount(self) -> float:
        try:
            return Discount.objects.get(item=self).percents
        except:
            return 0

    def get_tax(self) -> float:
        try:
            return Tax.objects.get(item=self).percentage
        except:
            return 0

    def __str__(self):
        return f'{self.product_name}'


class Content(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.item.product_name} in {self.order.__str__()}'


class Discount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    percents = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_name = models.CharField(max_length=255)
    duration = models.CharField(default="forever", max_length=25)

    def __str__(self):
        return f'{self.discount_name} discount by {self.order.__str__()}'


class Tax(models.Model):
    class JurisdictionChoices(models.TextChoices):
        USA = 'US', _('United States')
        EUR = 'DE', _('Germany')
        RUB = 'RU', _('Russia')

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    inclusive = models.BooleanField(default=False)
    jurisdiction = models.CharField(max_length=2, choices=JurisdictionChoices.choices, default=JurisdictionChoices.USA)
    percentage = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'{self.display_name} tax by {self.order.__str__()}'
