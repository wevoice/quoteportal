from .models import Tooltip


def tooltips(request):
    tooltippers = Tooltip.objects.filter(url=request.path)

    return {
        'tooltips': tooltippers
    }
