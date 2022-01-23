from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from layout.forms import NewsletterForm
from . models import Connection
from babysitter.models import Babysitter, BabysitterCalendar
from family.models import Family, FamilyCalendar
from family.choices import sity_list, work_list
from django.db.models import Q


@login_required
def all_babysitters(request):
    family = get_object_or_404(Family, user_id=request.user.id)
    family_city = family.sity
    babysitters = Babysitter.objects.filter(sity=family_city)

    # Babysitter with same city like family
    if babysitters.exists():
        babysitters = babysitters
    else:
        # Random Babysitter if same city is not exists. MEMBERSHIP GOLD OR A FEW FIRST
        babysitters = Babysitter.objects.all()

    if request.method == "POST":
        filter_babysitter = False
        # Filters after POST submit
        price_range_min = request.POST['price_range_min']
        price_range_max = request.POST['price_range_max']
        if price_range_min != '' or price_range_max != '':
            filter_babysitter = Babysitter.objects.filter(
                hourly_rate__gte=price_range_min).filter(hourly_rate__lte=price_range_max)
        city = request.POST['city']
        if city != '':
            filter_babysitter = Babysitter.objects.filter(sity=city)
        age_children = request.POST['age_children']
        if age_children != '':
            filter_babysitter = Babysitter.objects.filter(
                Q(age_children=age_children) | Q(age_children__contains=age_children))
        work_type = request.POST['work_type']
        if work_type != '':
            # IF 'Bebisiter i Dadilja' don't filter work
            if work_type == 'Bebisiterka i Dadilja':
                filter_babysitter = filter_babysitter
            else:
                filter_babysitter = Babysitter.objects.filter(
                    work_type=work_type)
        # If Filters match
        if filter_babysitter:
            babysitters = filter_babysitter
        # If Filters doesnt's match
        else:
            babysitters = False

    newsletter_form = NewsletterForm()
    city_list = sity_list
    work_role_list = work_list
    context = {'babysitters': babysitters,
               'city_list': city_list, 'work_role_list': work_role_list, 'form': newsletter_form}
    return render(request, 'connection/all_babysitters.html', context)


@login_required
def babysitter_profil(request, slug):
    babysitter = get_object_or_404(Babysitter, slug=slug)
    calendar = get_object_or_404(BabysitterCalendar,
                                 babysitter_id=babysitter.id)

    newsletter_form = NewsletterForm()
    context = {'babysitter': babysitter,
               'calendar': calendar,
               'form': newsletter_form}
    return render(request, 'connection/babysitter_profil.html', context)


@login_required
def send_match(request):
    if request.method == "POST":
        babysitter_slug = request.POST['babysitter_slug']
        babysiter_for_match = Babysitter.objects.get(slug=babysitter_slug)
        family_id = request.user.family.id
        babysitter_id = babysiter_for_match.id
        connection = Connection()
        connection.family_id = family_id
        connection.babysitter_id = babysitter_id
        connection.is_matched = None

        all_connection = Connection.objects.filter(
            family_id=family_id, babysitter_id=babysitter_id)
        if all_connection.exists():
            for connection in all_connection:
                if connection.is_matched == False:
                    connection.is_matched = None
                    connection.save()
                    messages.success(
                        request, (f'Ponovo ste ste rezervisali {babysiter_for_match.work_type} {babysiter_for_match.first_name} {babysiter_for_match.last_name}'))
                else:
                    messages.success(
                        request, (f'Već ste rezervisali {babysiter_for_match.work_type} {babysiter_for_match.first_name} {babysiter_for_match.last_name}'))
        else:
            connection.save()
            messages.success(
                request, (f'Uspešno ste rezervisali {babysiter_for_match.work_type} {babysiter_for_match.first_name} {babysiter_for_match.last_name}'))
    return redirect('family:profil')


@login_required
def matched_babysitter_profil(request, slug):
    babysitter = get_object_or_404(Babysitter, slug=slug)
    calendar = get_object_or_404(BabysitterCalendar,
                                 babysitter_id=babysitter.id)

    connection_queryset = Connection.objects.filter(
        family_id=request.user.family.id, babysitter_id=babysitter.id)
    # Stop URL connection if is mached is FALSE or Connection doesn't exists
    if connection_queryset.exists():
        if connection_queryset[0].is_matched == False:
            return redirect('family:profil')
        else:
            newsletter_form = NewsletterForm()
            context = {'babysitter': babysitter,
                       'calendar': calendar,
                       'form': newsletter_form}
            return render(request, 'connection/matched_babysitter_profil.html', context)
    else:
        return redirect('family:profil')


@login_required
def family_profil(request, slug):
    profil = get_object_or_404(Family, slug=slug)
    calendar = get_object_or_404(FamilyCalendar,
                                 family_id=profil.id)
    babysitter_id = request.user.babysitter.id
    # Connection for context
    connection_list = []
    all_connection_queryset = Connection.objects.filter(
        family_id=profil.id, babysitter_id=babysitter_id)

    for connection in all_connection_queryset:
        connection_list.append(connection)

    newsletter_form = NewsletterForm()
    context = {'profil': profil, 'connection_list': connection_list,
               'calendar': calendar,
               'form': newsletter_form}
    return render(request, 'connection/family_profil.html', context)


@login_required
def matched_family_profil(request, slug):
    babysitter_id = request.user.babysitter.id
    profil = get_object_or_404(Family, slug=slug)
    calendar = get_object_or_404(FamilyCalendar,
                                 family_id=profil.id)

    connection_queryset = Connection.objects.filter(
        family_id=profil.id, babysitter_id=babysitter_id)
    # Stop URL connection if is mached is FALSE or Connection doesn't exists
    if connection_queryset.exists():
        if connection_queryset[0].is_matched == False:
            return redirect('babysitter:profil')
        else:
            # Change is matched in TRUE
            for connection in connection_queryset:
                connection.is_matched = True
                connection.save()

            newsletter_form = NewsletterForm()
            context = {'profil': profil,
                       'calendar': calendar,
                       'form': newsletter_form}
            return render(request, 'connection/matched_family_profil.html', context)
    else:
        return redirect('babysitter:profil')


@login_required
def deny_connection(request):
    if request.method == "POST":
        connection_id = request.POST['connection_id']
        connection = Connection.objects.get(id=connection_id)
        connection.is_matched = False
        connection.save()
        messages.success(
            request, ('Uspešno ste odbili zahtev!'))
        context = {'connection': connection}
        return redirect('babysitter:profil')


@login_required
def delete_connection(request):
    if request.method == "POST":
        connection_id = request.POST['connection_id']
        connection = Connection.objects.get(id=connection_id)
        connection.delete()
        messages.success(
            request, ('Uspešno ste obrisali zahtev!'))
        context = {'connection': connection}
        return redirect('family:profil')
