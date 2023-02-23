import os
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from sender.forms import RegisterUserForm
from django.urls import reverse_lazy
from sender.models import*
from django.conf import settings
from sender.auxfunc import cut_first_symbol
from sender.auxfunc.create_cronjob import func


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'sender/registration.html'
    success_url = reverse_lazy('sender:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('sender:profile')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'sender/login.html'
    success_url = reverse_lazy('sender:profile')

def logout_user(request):
    logout(request)
    return redirect('sender:login')


class ConfigMailingListView(ListView):
    model = ConfigMailing
    fields = '__all__'
    template_name = 'sender/profile.html'
    success_url = reverse_lazy('sender:profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(username=self.request.user)


class ListAndCreateConfigMailing(CreateView):
    model = ConfigMailing
    fields = ('username', 'title', 'hour', 'minute', 'periodicity', 'mail_dump')
    template_name = 'sender/profile.html'
    success_url = reverse_lazy('sender:profile')

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user.pk
        mailing = self.object.pk
        create_cronjob = func.format(user, mailing)
        target_dir = f'sender/crons/{user}/{mailing}'

        if not os.path.isdir(f'sender/crons/{user}/{mailing}'):
            os.makedirs(f'sender/crons/{user}/{mailing}')

        if self.object.periodicity == 'Ежедневно':
            self.object.cron_period = f'{cut_first_symbol.do(self.object.minute.num)} {self.object.hour.num} * * *'
            self.object.cron_path = f'sender.crons.{user}.{mailing}.cron.send_letter'
            cronjob = (self.object.cron_period, self.object.cron_path)

            with open(f'{target_dir}/cron.py', 'w', encoding='utf-8') as f:
                f.write(f'{create_cronjob}')

            settings.CRONJOBS.append(cronjob)
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')
            print('список кронов')
            print( settings.CRONJOBS)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all().filter(username=self.request.user)
        context['hours'] = Hour.objects.all()
        context['minutes'] = Minute.objects.all()
        context['user'] = self.request.user
        return context


class ConfigMailingUpdateView(UpdateView):
    model = ConfigMailing
    fields = ('title', 'hour', 'minute', 'periodicity', 'mail_dump', 'weekday', 'monthdate')
    template_name = 'sender/update_mailing.html'
    success_url = reverse_lazy('sender:profile')

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user.pk
        mailing = self.object.pk
        create_cronjob = func.format(user, mailing)
        cronjob = (self.object.cron_period, self.object.cron_path)
        target_dir = f'sender/crons/{user}/{mailing}'

        if not os.path.isdir(f'sender/crons/{user}'):
            os.makedirs(f"sender/crons/{user}")

        if cronjob in  settings.CRONJOBS:
            print('удаление старого крона')
            settings.CRONJOBS.pop( settings.CRONJOBS.index(cronjob))
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')

        if self.object.periodicity == 'Ежедневно':
            self.object.cron_period = f'{cut_first_symbol.do(self.object.minute.num)} {self.object.hour.num} * * *'
            self.object.cron_path = f'sender.crons.{user}.{mailing}.cron.send_letter'
            cronjob = (self.object.cron_period,  self.object.cron_path)

            with open(f'{target_dir}/cron.py', 'w', encoding='utf-8') as f:
                f.write(f'{create_cronjob}')

            settings.CRONJOBS.append(cronjob)
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')
            print('список кронов')
            print(settings.CRONJOBS)

        if self.object.periodicity == 'Раз в неделю' and self.object.weekday:
            self.object.cron_period = f'{cut_first_symbol.do(self.object.minute.num)} {self.object.hour.num} * * {self.object.weekday.day_id}'
            self.object.cron_path = f'sender.crons.{user}.{mailing}.cron.send_letter'
            cronjob = (self.object.cron_period, self.object.cron_path)

            with open(f'{target_dir}/cron.py', 'w', encoding='utf-8') as f:
                f.write(f'{create_cronjob}')

            settings.CRONJOBS.append(cronjob)
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')
            print('список кронов')
            print(settings.CRONJOBS)

        if self.object.periodicity == 'Раз в месяц' and self.object.monthdate:
            self.object.cron_period = f'{cut_first_symbol.do(self.object.minute.num)} {self.object.hour.num} {self.object.monthdate.number} * *'
            self.object.cron_path = f'sender.crons.{user}.{mailing}.cron.send_letter'
            cronjob = (self.object.cron_period, self.object.cron_path)

            with open(f'{target_dir}/cron.py', 'w', encoding='utf-8') as f:
                f.write(f'{create_cronjob}')

            settings.CRONJOBS.append(cronjob)
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')
            print('список кронов')
            print(settings.CRONJOBS)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hours'] = Hour.objects.all()
        context['minutes'] = Minute.objects.all()
        context['dates'] = MonthDate.objects.all()
        context['days'] = WeekDay.objects.all()
        return context


class ConfigMailingDeleteView(DeleteView):
    model = ConfigMailing
    template_name = 'sender/delete_mailing.html'
    success_url = reverse_lazy('sender:profile')

    class LetterMailingListView(ListView):
        model = LetterMailing

    lm_list = LetterMailingListView()
    lm_list_query = lm_list.get_queryset()

    def post(self, request, *args, **kwargs):
        cronjob = (self.get_object().cron_period, self.get_object().cron_path)

        if cronjob in settings.CRONJOBS:
            print('удаление крона')
            print(cronjob)
            settings.CRONJOBS.pop(settings.CRONJOBS.index(cronjob))
            os.system('python3 manage.py crontab add')
            os.system('python3 manage.py crontab show > cronjons.txt')
            print('список кронов')
            print(settings.CRONJOBS)

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['letters'] = self.lm_list_query.filter(username=self.request.user, mailing=self.get_object().pk)
        return context

class ConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/mailing_detail.html'
    success_url = reverse_lazy('sender:mailing_detail')

    class LetterMailingCreateView(CreateView):
        model = LetterMailing
        fields = ('username', 'mailing', 'title', 'content', 'position')

        def get_success_url(self):
            return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.get_object(ConfigMailing.objects.all()).pk})

    lm_create = LetterMailingCreateView()
    lm_create_query = lm_create.get_form_class()

    class LetterMailingListView(ListView):
        model = LetterMailing
        success_url = reverse_lazy('sender:mailing_detail')
        ordering = ['position']

    lm_list = LetterMailingListView()
    lm_list_query = lm_list.get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trials'] = TryMailing.objects.all().filter(username=self.request.user)
        context['letters'] = self.lm_list_query.filter(username=self.request.user, mailing=self.get_object().pk)
        context['form'] = self.lm_create_query
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        view = self.LetterMailingCreateView.as_view()
        return view(request, *args, **kwargs)


class LetterMailingUpdateView(UpdateView):
    model = LetterMailing
    fields = ('title', 'content', 'position')
    template_name = 'sender/update_letter.html'

    def get_success_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.get_object().mailing.pk})


class LetterMailingDeleteView(DeleteView):
    model = LetterMailing
    template_name = 'sender/delete_letter.html'

    def get_success_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.get_object().mailing.pk})


class TryMailingListView(ListView):
    model = TryMailing
    template_name = 'sender/try_list.html'
    success_url = reverse_lazy('sender:trials')

    def get_queryset(self):
       return super().get_queryset().filter(username=self.request.user)



