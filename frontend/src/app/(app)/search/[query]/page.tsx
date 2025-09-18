"use client";

import Results from "../../../../components/Results";
import { fetchNews, fetchEvents } from "../../../../lib/api";
import { NewsItem, EventItem } from "../../../../lib/types";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function SearchPage() {
  const params = useParams<{ query: string }>();
  const query = decodeURIComponent(params.query);

  const [news, setNews] = useState<NewsItem[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [newsResponse, eventsResponse] = await Promise.all([
          fetchNews(query),
          fetchEvents(query),
        ]);
        setNews(newsResponse.items as NewsItem[]);
        setEvents(eventsResponse.items as EventItem[]);
      } catch (err) {
        console.error("Search fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [query]);

  if (loading) return <p className="p-4">Loading search results...</p>;

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-8">
      <h2 className="text-2xl font-bold">Search results for &quot;{query}&quot;</h2>

      <section>
        <h3 className="text-lg font-semibold mb-4">News</h3>
        {news.length > 0 ? <Results results={news} /> : <p>No news found.</p>}
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-4">Events</h3>
        {events.length > 0 ? <Results results={events} /> : <p>No events found.</p>}
      </section>
    </div>
  );
}
