type Activity = { time: string; event: string };

export function ActivityCard({ activity, onOpen }: { activity: Activity[]; onOpen: () => void }) {
  return (
    <section className="panel-card lower-card">
      <h2>Atividade recente</h2>
      <div className="activity-list">
        {activity.slice(0, 5).map((item, index) => (
          <div className="activity-row" key={`${item.event}-${index}`}>
            <span>{item.time || "--:--"}</span>
            <p>{item.event}</p>
          </div>
        ))}
      </div>
      <button className="link-button" onClick={onOpen}>Ver todas</button>
    </section>
  );
}
