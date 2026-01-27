from django.shortcuts import render
from django.http import JsonResponse
from .models import Location

def get_sido(request):
    sido_list = Location.objects.values_list("sido", flat=True).distinct()
    return JsonResponse(list(sido_list), safe=False)


def get_sigungu(request):
    sido = request.GET.get("sido")
    sigungu_list = Location.objects.filter(sido=sido).values_list("sigungu", flat=True).distinct()
    return JsonResponse(list(sigungu_list), safe=False)


def get_eupmyeondong(request):
    sido = request.GET.get("sido")
    sigungu = request.GET.get("sigungu")

    qs = Location.objects.filter(
        sido=sido,
        sigungu=sigungu
    )

    # ✅ eupmyeondong이 없는 지역 (세종 새롬동)
    if not qs.exclude(eupmyeondong="").exists():
        loc = qs.first()
        return JsonResponse([
            {
                "id": loc.id,
                "name": sigungu   # ⭐ 2단계를 3단계처럼 노출
            }
        ], safe=False)

    # ✅ 일반 3단계 지역
    data = [
        {
            "id": loc.id,
            "name": loc.eupmyeondong
        }
        for loc in qs.exclude(eupmyeondong="").order_by("eupmyeondong")
    ]

    return JsonResponse(data, safe=False)
    
