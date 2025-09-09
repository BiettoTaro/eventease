import Link from "next/link";
import Results from "../../../components/Results";
import { fetchEvents } from "../../../lib/api";
export const dynamic = "force-dynamic";
import { EventItem } from "../../../lib/types";


type EventPageProps = {
    searchParams: {
        offset?: string;
        limit?: string;
    }
}

export default async function EventsPage({ searchParams }: EventPageProps) {
  const offset = parseInt(searchParams?.offset || "0", 10);
  const limit = parseInt(searchParams?.limit || "10", 10);
  let events: EventItem[] = [];
  let total = 0;

  try {
    const {items, total:eventsTotal} = await fetchEvents(undefined, offset, limit);
    total = eventsTotal;
    events = items.map((item: EventItem, index: number) => ({
      id: item.id || String(index),
      title: item.title,
      description: item.description || "",
      type: item.type,
      image: item.image || null,
    }));
  } catch (err) {
    console.error("Error fetching events:", err);
    return (
      <div className="p-10 text-center text-red-500">
        Could not load events right now.
      </div>
    );
  }

  const hasPrev = offset > 0;
  const hasNext = offset + limit < total;

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-4">
      <h2 className="text-2xl font-bold mb-6">Upcoming Events</h2>
      {events.length > 0 ? (
        <>
        <Results results={events} />
        <div className="flex justify-between mt-6">
            {hasPrev ? (
              <Link
                href={`/events?offset=${Math.max(offset - limit, 0)}&limit=${limit}`}
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
                  Previous
              </Link>
            ) : (
              <span />
            )}

            {hasNext &&(
              <Link
                href={`/events?offset=${offset + limit}&limit=${limit}`}
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
                  Next
              </Link>
            )}
          </div>
        </>
      ) : (
        <p>No events available.</p>
      )}
    </div>
  );
}
