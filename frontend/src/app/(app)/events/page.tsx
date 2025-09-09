"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Results from "../../../components/Results";
import { fetchEvents } from "../../../lib/api";
import { EventItem } from "../../../lib/types";
import { useRouter, useSearchParams } from "next/navigation";


export const dynamic = "force-dynamic";


export default function EventsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const offset = parseInt(searchParams.get("offset") || "0", 10);
  const limit = parseInt(searchParams.get("limit") || "10", 10);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const loadEvents = async () => {
      try {
        const { items, total: eventsTotal } = await fetchEvents(undefined, offset, limit);
        setEvents(items);
        setTotal(eventsTotal);
      } catch (err) {
        console.error("Error fetching events:", err);
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, [offset, limit, router]);

  if (loading) return <p className="p-10">Loading events...</p>;

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
              <Link href={`/events?offset=${Math.max(offset - limit, 0)}&limit=${limit}`} className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
                Previous
              </Link>
            ) : <span />}
            {hasNext && (
              <Link href={`/events?offset=${offset + limit}&limit=${limit}`} className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
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
