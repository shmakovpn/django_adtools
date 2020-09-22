Django-adtools
==============



Django-adtools is a package with a set of utilities for integrating web applications based on the django framework with
MS ActiveDirectory.

All documentation is in the "``docs/build``" directory and online at
http://django-adtools.readthedocs.org

Short example of using Active Directory authentication system

 .. code-block:: python

  # views.py
  from django_adtools.ad.ad_tools import ad_login, ad_clear_username

  def post(self, request):
      form = LoginForm(request.POST)
      if form.is_valid():
          if ad_login(  # checking, if user is able to login using Active Directory credentials
              dc=DomainController.get(),  # A hostname or an ip address of a Domain Controller
              username=form.cleaned_data['username'],
              password=form.cleaned_data['password'],
              domain=settings.ADTOOLS_DOMAIN,  # A name of domain, e.g. domain.com
              group=settings.ADTOOLS_GROUP,  # A group name of valid users
          ):
              # get full domain username like user@domain.ru
              username_without_domain = ad_clear_username(form.cleaned_data['username'])
              username = f"{username_without_domain}@{settings.ADTOOLS_DOMAIN}"
              try:
                  # looking for existing user profile (case insensitive)
                  user = User.objects.get(username__iexact=username)
              except User.DoesNotExist:
                  # create a new user profile, if it does not exist
                  user = User(username=username)
                  user.save()
              login(request=request, user=user)
              return redirect(reverse(f'{__package__}:index'))
      context = {'package': __package__, 'form': form, 'login_failed': True, }
      return render(request, f"{__package__}/login.html", context)
