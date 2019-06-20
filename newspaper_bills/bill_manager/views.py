from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.views.generic import View, DetailView, ListView, CreateView
from collections import namedtuple
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models, forms
from . import additives


class Home(LoginRequiredMixin, View):
    login_url = 'login'
    template = 'home.html'
    post_redirect = 'bill_manager:home'
    no_plan_redirect = 'bill_manager:create_plan'

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


class Plan(LoginRequiredMixin, DetailView):
    login_url = 'login'
    template_name = 'plan.html'
    model = models.Plan
    redirect_url = 'bill_manager:edit_plan'

    def post(self, request, pk):
        return redirect(self.redirect_url, pk)


class EditPlan(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = forms.EditPlanForm
    template_name = 'edit_plan.html'

    def get_initial(self):
        plan = models.Plan.objects.get(id=self.kwargs['pk'])
        return {'sun': plan.sun,
                'mon': plan.mon,
                'tue': plan.tue,
                'wed': plan.wed,
                'thu': plan.thu,
                'fri': plan.fri,
                'sat': plan.sat
                }

    def form_valid(self, form):
        plans = models.Plan.objects.filter(**form.cleaned_data)

        if len(plans) == 0:
            plan = form.save()
        else:
            plan = plans[0]

        self.request.user.plan_id = plan.id
        self.request.user.save()

        try:
            models.Plan.objects.get(id=self.kwargs['pk']).delete()
        except ProtectedError:
            pass

        messages.success(self.request, 'Your plan has been successfully updated!')
        return redirect('bill_manager:plan', self.request.user.plan_id)


class MyBills(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Bill
    template_name = 'my_bills.html'
    context_object_name = 'user_bills'
    # ordering = ['-month']

    def get_queryset(self):
        return sorted(self.request.user.bills.all(), key=lambda x: x.month, reverse=True)


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


class NewPlan(LoginRequiredMixin, CreateView):
    login_url = 'login'
    template_name = 'new_plan.html'
    form_class = forms.EditPlanForm

    def form_valid(self, form):
        plans = models.Plan.objects.filter(**form.cleaned_data)

        if len(plans) == 0:
            plan = form.save()
        else:
            plan = plans[0]

        self.request.user.plan_id = plan.id
        self.request.user.save()
        messages.success(self.request, 'Plan uploaded successfully!')
        return redirect('bill_manager:home')
