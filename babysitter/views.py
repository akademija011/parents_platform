from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib.auth.decorators import login_required
from layout.forms import NewsletterForm
from . forms import BabysitterForm, BabysitterCalendarForm
from . models import Babysitter, BabysitterCalendar
from connection . models import Connection
from family . models import Family


@login_required
def create_profil(request):
    form_babysitter = BabysitterForm()
    user = request.user
    user_id = user.id
    try:
        babysitter_obj = Babysitter.objects.get(user_id=user_id)
    except Babysitter.DoesNotExist:
        babysitter_obj = None
    if babysitter_obj:  # PROFIL EXIST
        return redirect('/babysitter/profil')
    else:  # PROFIL NOT EXIST
        if request.method == "POST":
            form_babysitter = BabysitterForm(request.POST, request.FILES)
            if form_babysitter.is_valid():
                babysitter = form_babysitter.save(commit=False)
                babysitter.is_form_submit = True
                babysitter.user_id = user.id
                babysitter.save()
                messages.success(
                    request, 'Uspesno ste kreirali profil')
                return redirect('/babysitter/edit_calendar')
            else:
                messages.error(
                    request, 'Proverite format broja telefona ili slike (jpg, png ili jpeg)')
        newsletter_form = NewsletterForm()
        context = {'form_babysitter': form_babysitter, 'form': newsletter_form}
        return render(request, 'babysitter/create_profil_babysitter.html', context)


@login_required
def edit_profil(request):
    user = request.user
    user_id = user.id
    babysitter_obj = get_object_or_404(Babysitter, user_id=user_id)

    form_babysitter = BabysitterForm(instance=babysitter_obj)
    if request.method == 'POST':
        form = BabysitterForm(
            request.POST, request.FILES,  instance=babysitter_obj)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Uspesno ste azurirali profil')
            return redirect('/babysitter/profil')
        else:
            messages.error(
                request, 'Proverite format broja telefona ili slike (jpg, png ili jpeg)')
    newsletter_form = NewsletterForm()
    context = {'form_babysitter': form_babysitter, 'form': newsletter_form}
    return render(request, 'babysitter/edit_profil_babysitter.html', context)


@login_required
def profil(request):
    user = request.user
    user_id = user.id
    profil = get_object_or_404(Babysitter, user_id=user_id)
    calendar = get_object_or_404(BabysitterCalendar, babysitter_id=profil.id)

    # LOGIC FOR FIND ALL FAMILY WHICH PROFIL SEND MATCH REQUEST (CONNECTION APP)
    all_families_match_queryset = []

    # All match for babysitter profile
    all_match_queryset = Connection.objects.filter(babysitter_id=profil.id)
    all_match_list = list(all_match_queryset)
    for one_match in all_match_list:
        id_family = one_match.family_id
        #is_matched = one_match.is_matched
        one_match_family = Family.objects.get(id=id_family)
        all_families_match_queryset.append(one_match_family)
    send_family_list = list(all_families_match_queryset)

    newsletter_form = NewsletterForm()
    context = {'profil': profil, 'calendar': calendar,
               'form': newsletter_form, 'send_family_list': send_family_list}
    # PROBA STRANICA
    # return render(request, 'babysitter/profil_babysitter_proba.html', context)
    return render(request, 'babysitter/profil_babysitter.html', context)


@login_required
def edit_calendar(request):
    user = request.user
    user_id = user.id
    babysitter_obj = get_object_or_404(
        Babysitter, user_id=user_id)
    babysitter_id = babysitter_obj.id
    babysitter_calendar = get_object_or_404(BabysitterCalendar,
                                            babysitter_id=babysitter_id)
    babysitter_calendar_form = BabysitterCalendarForm(
        instance=babysitter_calendar)
    if request.method == 'POST':
        form = BabysitterCalendarForm(
            request.POST, instance=babysitter_calendar)
        if form.is_valid():
            form_babysitter_calendar = form.save(commit=False)
            form_babysitter_calendar.babysitter_id = babysitter_id
            form_babysitter_calendar.save()
            messages.success(
                request, 'Uspesno ste azurirali Vasu dostupnost')
            return redirect('/babysitter/profil')
        else:
            messages.error(
                request, 'Proverite format broja telefona ili slike (jpg, png ili jpeg)')

    context = {'babysitter_calendar_form': babysitter_calendar_form}
    return render(request, 'babysitter/edit_calendar.html', context)
