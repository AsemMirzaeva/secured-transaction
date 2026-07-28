import {
  LiveKitRoom,
  VideoConference,
  ConnectionStateToast,
  useConnectionState,
} from "@livekit/components-react";
import { ConnectionState } from "livekit-client";
import { useEffect } from "react";

interface Props {
  livekitUrl: string;
  token: string;
  onLeave: () => void;
}

/**
 * Wraps LiveKit's React components for the Video-KYC call. The user (and,
 * once they join, the operator) share this room. The backend already scoped
 * the token to exactly one room with a short TTL — this component just
 * renders the call and reports back when it ends.
 */
export default function VideoCallRoom({ livekitUrl, token, onLeave }: Props) {
  return (
    <div className="video-kyc-room">
      <LiveKitRoom
        serverUrl={livekitUrl}
        token={token}
        connect
        video
        audio
        onDisconnected={onLeave}
        data-lk-theme="default"
      >
        <ConnectionStateWatcher onLeave={onLeave} />
        <VideoConference />
        <ConnectionStateToast />
      </LiveKitRoom>
    </div>
  );
}

function ConnectionStateWatcher({ onLeave }: { onLeave: () => void }) {
  const state = useConnectionState();

  useEffect(() => {
    if (state === ConnectionState.Disconnected) {
      onLeave();
    }
  }, [state, onLeave]);

  return null;
}