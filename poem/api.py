from poem.models import Poem
from ninja import Router

router = Router()


@router.get("newest/")
def poems(request):
    poems = Poem.objects.select_related(
        "author"
    ).filter(
        editorial__status="approved"
    ).exclude(
        editorial__timing=None
    )[:25]

    return [{
        "poem_id": poem.id,
        "name": poem.name,
        "editorial_timing": poem.editorial.timing,
    } for poem in poems]
