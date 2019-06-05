from django.shortcuts import render, redirect
from datetime import datetime
from . import additives
from . import models, forms
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from collections import namedtuple
from django.contrib import messages


class Home(View):
    @staticmethod
    def get(request):
        if request.user.plan_id is None:
            return redirect('create_plan')

        # designing the calendar to display
        current_datetime = str(datetime.now())
        current_year = int(current_datetime[:4])
        current_month = int(current_datetime[5:7])
        current_day = int(current_datetime[8:10])

        calendar = additives.generate_calendar(current_day,
                                               current_month,
                                               current_year)
        # gathering billing information of user
        month = current_year*100 + current_month

        try:
            current_month_bill = request.user.bills.get(month=month)
        except ObjectDoesNotExist:
            current_month_bill = models.Bill.create_bill(user=request.user, month=month)

        np_absentees = []
        absentee_int = current_month_bill.absentees
        bit = 1

        while absentee_int:
            is_absent = absentee_int % 2

            if is_absent:
                np_absentees.append(bit)

            bit += 1
            absentee_int //= 2

        amount = current_month_bill.update_amount()
        calendar['amount'] = amount
        calendar['absentees'] = np_absentees

        return render(request, 'home.html', calendar)

    @staticmethod
    def post(request):
        print(request.POST)
        if 'date' in request.POST.keys():
            date = int(request.POST['date'])
            absentee = 2**(date-1)
            print(f'absentee = {absentee}')

            current_datetime = str(datetime.now())
            current_year = int(current_datetime[:4])
            current_month = int(current_datetime[5:7])
            month = current_month + current_year*100

            bill = request.user.bills.get(month=month)
            print(bill.absentees)
            bill.absentees = bill.absentees ^ absentee
            bill.save()
            print(bill.absentees)

        return redirect('home')


class Plan(View):
    @staticmethod
    def get(request):
        plan_id = request.user.plan_id
        plan = models.Plan.objects.get(id=plan_id)
        cost_chart = {'sun': plan.sun,
                      'mon': plan.mon,
                      'tue': plan.tue,
                      'wed': plan.wed,
                      'thu': plan.thu,
                      'fri': plan.fri,
                      'sat': plan.sat
                      }

        return render(request, 'plan.html', cost_chart)

    @staticmethod
    def post(request):
        # print(request.POST)
        if 'edit_plan' in request.POST.keys():
            return redirect('edit_plan')


class EditPlan(View):
    @staticmethod
    def get(request):
        plan_id = request.user.plan_id
        plan = models.Plan.objects.get(id=plan_id)
        cost_chart = {'sun': plan.sun,
                      'mon': plan.mon,
                      'tue': plan.tue,
                      'wed': plan.wed,
                      'thu': plan.thu,
                      'fri': plan.fri,
                      'sat': plan.sat
                      }
        form = forms.EditPlanForm(initial=cost_chart)
        return render(request, 'edit_plan.html', {'form': form})

    @staticmethod
    def post(request):
        form = forms.EditPlanForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            # print(form_data)
            old_plan = request.user.plan_id
            plans = models.Plan.objects.filter(**form_data)

            if len(plans) == 0:
                print('new')
                plan = form.save()
                request.user.plan_id = plan.id
            else:
                request.user.plan_id = plans[0].id

            request.user.save()
            models.Plan.objects.get(id=old_plan).delete()

            messages.success(request, 'Your plan has been successfully updated!')

        return redirect('plan')


class MyBills(View):
    @staticmethod
    def get(request):
        user = request.user
        bills = sorted(list(user.bills.all()), key=lambda x: x.month, reverse=True)
        # print(bills)
        bill = namedtuple('bill', ['month_name', 'year', 'amount', 'status', 'id'])
        bills_info = [bill(additives.month_name(bill_.month % 100),
                           bill_.month//100,
                           bill_.amount,
                           bill_.paid_on,
                           bill_.id)
                      for bill_ in bills]
        counter = additives.Counter(1)
        return render(request, 'my_bills.html', {'user_bills': bills_info,
                                                 'counter': counter})


class Bill(View):
    @staticmethod
    def get(request, pk):
        current_datetime = str(datetime.now())
        current_day = int(current_datetime[8:10])

        current_bill = models.Bill.objects.get(id=pk)
        calendar = additives.generate_calendar(current_day, current_bill.month % 100,
                                               current_bill.month//100)

        current_datetime = str(datetime.now())
        current_year = int(current_datetime[:4])
        current_month = int(current_datetime[5:7]) + current_year*100

        bill = namedtuple('bill', ['id', 'amount', 'status', 'absentees',
                                   'current'])

        np_absentees = []
        absentee_int = current_bill.absentees
        bit = 1

        while absentee_int:
            is_absent = absentee_int % 2

            if is_absent:
                np_absentees.append(bit)

            bit += 1
            absentee_int //= 2

        if current_month == current_bill.month:
            bill_ = bill(current_bill.id, current_bill.amount,
                         current_bill.paid_on, np_absentees, True)
        else:
            bill_ = bill(current_bill.id, current_bill.amount,
                         current_bill.paid_on, np_absentees, False)
        calendar['bill'] = bill_

        return render(request, 'bill.html', calendar)

    @staticmethod
    def post(pk, request):
        bill = models.Bill.objects.get(id=pk)
        bill.paid_on = datetime.now()
        bill.save()
        messages.success(request, 'Your bill has been marked as paid!')
        return redirect('bill', pk=pk)


class NewPlan(View):
    @staticmethod
    def get(request):
        form = forms.EditPlanForm()
        return render(request, 'new_plan.html', {'form': form})

    @staticmethod
    def post(request):
        form = forms.EditPlanForm(request.POST)

        if form.is_valid():
            plan = form.save()
            request.user.plan_id = plan.id
            request.user.save()

            messages.success(request, 'Plan uploaded successfully!')
            return redirect('home')

        else:
            return render(request, 'new_plan.html', {'form': form})
