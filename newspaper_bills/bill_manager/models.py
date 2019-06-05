from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from datetime import datetime


class Plan(models.Model):
    sun = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    mon = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    tue = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    wed = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    thu = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    fri = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])
    sat = models.DecimalField(max_digits=5, decimal_places=2,
                              validators=[MinValueValidator(0.00)])


class User(AbstractUser):
    plan = models.ForeignKey(to=Plan, on_delete=models.PROTECT,
                             related_name='users', null=True)


class Bill(models.Model):
    month = models.IntegerField(validators=[MinValueValidator(201901),
                                            MaxValueValidator(999912)])
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(0.00)], default=0)
    absentees = models.IntegerField(validators=[MinValueValidator(0),
                                                MaxValueValidator(2147483647)],
                                    default=0)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='bills')
    paid_on = models.DateTimeField(null=True)

    def __repr__(self):
        s = str(self.month)
        return s

    @staticmethod
    def create_bill(user, month):
        bill = Bill.objects.create(user=user, month=month)
        bill.update_amount()
        return bill

    def update_amount(self):
        current_datetime = str(datetime.now())
        today = int(current_datetime[8:10])
        first_date = '01 ' + str(self.month % 100) + ' ' + str((self.month // 100) % 100)
        day_name = datetime.strptime(first_date, '%d %m %y').weekday()
        day_name = (day_name + 2) % 7

        if day_name == 0:
            day_name = 7

        # print(f'day_name = {day_name}')
        plan_id = User.objects.get(id=self.user.id).plan_id
        plan = Plan.objects.get(id=plan_id)

        cost_chart = {1: plan.sun,
                      2: plan.mon,
                      3: plan.tue,
                      4: plan.wed,
                      5: plan.thu,
                      6: plan.fri,
                      7: plan.sat
                      }
        # print(cost_chart)
        np_absentees = self.absentees
        self.amount = 0

        for day in range(1, today + 1):

            if not np_absentees % 2:
                self.amount += cost_chart[day_name]

            np_absentees //= 2
            day_name = (day_name + 1) % 7
            if day_name == 0:
                day_name = 7

        self.save()
        return self.amount




