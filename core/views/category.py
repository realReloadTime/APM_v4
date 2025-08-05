import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.category import CategoryRepository, CategoryService
from core.models import Category
from core.auth import async_permission_required, async_api_method


async def get_category_service():
    return CategoryService(CategoryRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_category(request):
    service = await get_category_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            category = await service.create_category(data)
            return JsonResponse(category, status=201)
        else:
            category = await service.get_category()
            return JsonResponse(category, status=200, safe=False)

    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_category_detail(request, category_id: int):
    service = await get_category_service()

    try:
        category = await service.get_category(category_id)
        return JsonResponse(category, status=200)

    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_category(request, category_id: int):
    service = await get_category_service()
    data = json.loads(request.body)
    try:
        category = await service.update_category(category_id, data)
        return JsonResponse(category, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_category(request, category_id: int):
    service = await get_category_service()

    try:
        assert await service.delete_category(category_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
