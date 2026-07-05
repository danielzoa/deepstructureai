type Props = {
  online: boolean;
  label: string;
};

export function StatusBadge({ online, label }: Props) {
  return (
    <span className="status-badge">
      <span className={online ? "dot online" : "dot"} />
      {label}
    </span>
  );
}
