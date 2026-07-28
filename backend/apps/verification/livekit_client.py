
from django.conf import settings
from livekit import api


def generate_room_name(transaction_id) -> str:
    return f"kyc-{transaction_id}"


def create_access_token(*, room_name: str, identity: str, name: str, is_operator: bool = False) -> str:
   
    grants = api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
        room_admin=is_operator,
        room_record=is_operator,
    )

    token = (
        api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(name)
        .with_grants(grants)
        .with_ttl(settings.LIVEKIT_TOKEN_TTL_SECONDS)
    )
    return token.to_jwt()


def get_livekit_api() -> api.LiveKitAPI:
   
    return api.LiveKitAPI(
        settings.LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://"),
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET,
    )


async def start_recording(room_name: str) -> str:

    async with get_livekit_api() as lk:
        request = api.RoomCompositeEgressRequest(
            room_name=room_name,
            file_outputs=[api.EncodedFileOutput(filepath=f"recordings/{room_name}.mp4")],
        )
        info = await lk.egress.start_room_composite_egress(request)
        return info.egress_id