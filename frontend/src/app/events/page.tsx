import Results from "../../components/Results";
import { fetchEvents } from "../../lib/api";

type EventItem = {
    id: string;
    title: string;
    description: string;
    type: string;
}

export default async function EventsPage() {
  let events: EventItem[] = [];

  try {
    events = await fetchEvents();
  } catch (err) {
    console.error("Error fetching events:", err);
    return (
      <div className="p-10 text-center text-red-500">
        Could not load events right now.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-4">
      <h2 className="text-2xl font-bold mb-6">Upcoming Events</h2>
      {events.length > 0 ? (
        <Results results={events} />
      ) : (
        <p>No events available.</p>
      )}
    </div>
  );
}
