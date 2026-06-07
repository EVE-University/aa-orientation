"""Views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.cache import cache

import requests
from django.conf import settings
from esi.models import Token

from orientation.models import NewMembers


def get_character_online_status(character_id):
    """Check if an EVE character is currently online using authenticated ESI API."""
    cache_key = f"online_status_{character_id}"
    cached_status = cache.get(cache_key)

    if cached_status is not None:
        return cached_status

    try:
        # Get a valid ESI token for this character with the required scope
        required_scope = 'esi-location.read_online.v1'

        # Try to find a valid token for this character with the required scope
        try:
            token = Token.objects.filter(
                character_id=character_id,
                scopes__name=required_scope
            ).require_valid().first()
        except Token.DoesNotExist:
            token = None

        if not token:
            # No valid token available, cache as unknown for shorter time
            cache.set(cache_key, "No Token", 60)
            return "No Token"

        # Make authenticated ESI API request
        esi_url = getattr(settings, 'ESI_API_URL', 'https://esi.evetech.net/')
        api_url = f"{esi_url}latest/characters/{character_id}/online/"

        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'User-Agent': 'Alliance Auth Orientation Module',
            'Cache-Control': 'no-cache'
        }

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            online_data = response.json()
        elif response.status_code == 401:
            # Token expired or invalid, cache as no token
            cache.set(cache_key, "Token Invalid", 60)
            return "Token Invalid"
        else:
            # Other error
            cache.set(cache_key, "Unknown", 60)
            return "Unknown"

        is_online = online_data.get('online', False)
        status = "Online" if is_online else "Offline"

        # Cache for 5 minutes to avoid excessive API calls
        cache.set(cache_key, status, 60 * 5)
        return status

    except Exception as e:
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
