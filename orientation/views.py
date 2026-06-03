"""Views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.cache import cache

import requests
from django.conf import settings

from orientation.models import NewMembers


def get_character_online_status(character_id):
    """Check if an EVE character is currently online using ESI API."""
    cache_key = f"online_status_{character_id}"
    cached_status = cache.get(cache_key)

    if cached_status is not None:
        return cached_status

    try:
        # Direct ESI API call to check online status
        esi_url = getattr(settings, 'ESI_API_URL', 'https://esi.evetech.net/')
        api_url = f"{esi_url}latest/characters/{character_id}/online/"

        response = requests.get(
            api_url,
            headers={
                'User-Agent': 'Alliance Auth Orientation Module',
                'Cache-Control': 'no-cache'
            },
            timeout=10
        )

        if response.status_code == 200:
            online_data = response.json()
            is_online = online_data.get('online', False)
            status = "Online" if is_online else "Offline"
        else:
            status = "Unknown"

        # Cache for 5 minutes to avoid excessive API calls
        cache.set(cache_key, status, 60 * 5)
        return status

    except Exception:
        # If API call fails, return unknown status and cache for shorter time
        cache.set(cache_key, "Unknown", 60)
        return "Unknown"


@login_required
@permission_required("orientation.basic_access")
def index(request):
    """List all NewMembers ordered by creation date."""
    members = NewMembers.all_new_members_in_corp()

    # Add online status for each member
    for member in members:
        try:
            # Get the main character for this user
            main_character = member.member_app.user.profile.main_character
            if main_character:
                member.online_status = get_character_online_status(main_character.character_id)
            else:
                member.online_status = "No Character"
        except Exception:
            member.online_status = "Unknown"

    return render(request, "orientation/index.html", {"members": members})


@require_POST
@permission_required("orientation.basic_access")
def mark_talked(request):
    """Mark a member as 'talked to'."""
    member_id = request.POST.get("member_id")
    print(request.POST)
    try:
        member = NewMembers.objects.get(id=member_id)
        member.member_talked_state = NewMembers.MembershipStates.TALKED
        member.save()
        return JsonResponse({"success": True})
    except NewMembers.DoesNotExist:
        return JsonResponse({"success": False, "error": "Member not found"})
