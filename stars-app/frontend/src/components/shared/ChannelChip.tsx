import { CHANNEL_CLASS } from "../../styles/tokens";

export default function ChannelChip({ channel }: { channel: string }) {
  const cls = CHANNEL_CLASS[channel] ?? "ch-portal";
  return <span className={`pill ${cls} text-xs`}>{channel}</span>;
}
