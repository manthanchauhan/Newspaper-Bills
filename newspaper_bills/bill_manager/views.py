from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from . import additives
from . import models, forms
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View, ListView
from collections import namedtuple
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class Home(LoginRequiredMixin, View):
    login_url = 'login'
    template = 'home.html'
    post_redirect = 'bill_manager:home'
    no_plan_redirect = 'create_plan'

    current_datetime = str(datetime.now())
    current_year = int(current_datetime[:4])
    current_month = int(current_datetime[5:7])
    current_day = int(current_datetime[8:10])

    def get(self, request):
        if self.request.user.plan_id is None:
            return redirect(self.no_plan_redirect)

        calendar = additives.generate_calendar(self.current_day,
                                               self.current_month,
                                               self.current_year)

        # gathering billing information of user
        month = self.current_year*100 + self.current_month
        try:
            current_month_bill = self.request.user.bills.get(month=month)
        except ObjectDoesNotExist:
            current_month_bill = models.Bill.create_bill(user=request.user,
                                                         month=month)
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
        dict_ = {'amount': amount,
                 'absentees': np_absentees
                 }
        return render(self.request, self.template, {**dict_, **calendar})

    def post(self, request):
        if 'date' in request.POST.keys():
            date = int(self.request.POST['date'])
            absentee = 2**(date-1)

            month = self.current_month + self.current_year*100

            bill = request.user.bills.get(month=month)
            bill.absentees = bill.absentees ^ absentee
            bill.save()

        return redirect(self.post_redirect)


class Plan(LoginRequiredMixin, View):
    login_url = 'login'
    template = 'plan.html'
    redirect_url = 'bill_manager:edit_plan'

    def get(self, request):
        plan_id = self.request.user.plan_id
        plan = get_object_or_404(models.Plan, id=plan_id)
        cost_chart = {'sun': plan.sun,
                      'mon': plan.mon,
                      'tue': plan.tue,
                      'wed': plan.wed,
                      'thu': plan.thu,
                      'fri': plan.fri,
                      'sat': plan.sat
                      }
        return render(request, self.template, cost_chart)

    def post(self, request):
        if 'edit_plan' in request.POST.keys():
            return redirect(self.redirect_url)


class EditPlan(LoginRequiredMixin, View):
    login_url = 'login'
    form_class = forms.EditPlanForm
    template = 'edit_plan.html'
    redirect_url = 'bill_manager:plan'

    def get(self, request):
        plan_id = request.user.plan_id
        plan = get_object_or_404(models.Plan, id=plan_id)
        cost_chart = {'sun': plan.sun,
                      'mon': plan.mon,
                      'tue': plan.tue,
                      'wed': plan.wed,
                      'thu': plan.thu,
                      'fri': plan.fri,
                      'sat': plan.sat
                      }
        form = self.form_class(initial=cost_chart)
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            old_plan = request.user.plan_id
            plans = models.Plan.objects.filter(**form_data)

            if len(plans) == 0:
                plan = form.save()
                request.user.plan_id = plan.id
            else:
                request.user.plan_id = plans[0].id

            request.user.save()
            models.Plan.objects.get(id=old_plan).delete()
            messages.success(request, 'Your plan has been successfully updated!')

        return redirect(self.redirect_url)


class MyBills(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
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
        return render(request, 'my_bills.html', {'user_bills': bills_info})


class Bill(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
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
        bill = get_object_or_404(models.Bill, id=pk)
        bill.paid_on = datetime.now()
        bill.save()
        messages.success(request, 'Your bill has been marked as paid!')
        return redirect('bill_manager:bill', pk=pk)


class NewPlan(LoginRequiredMixin, View):
    login_url = 'login'

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
            return redirect('bill_manager:home')

        else:
            return render(request, 'new_plan.html', {'form': form})
