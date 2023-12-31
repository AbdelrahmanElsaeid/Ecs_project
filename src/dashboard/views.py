from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
@login_required
def view_dashboard(request):

    return render(request, 'dashboard/dashboard.html')
