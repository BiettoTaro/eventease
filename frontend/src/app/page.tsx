"use client"

import { useEffect, useState } from "react"
import { fetchNews, fetchEvents } from "../lib/api"

type NewsItem = {
    id: string;
    title: string;
    description: string;
}

type EventItem = {
    id: string;
    title: string;
    description: string;
}

export default function Home() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [newsData, eventsData] = await Promise.all([
          fetchNews(),
          fetchEvents()
        ]);
        setNews(newsData);
        setEvents(eventsData);
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;
  return  (
    <div className="p-8 space-y-12">
      
      <h2 className="text-xl font-semibold mb-4">News</h2>
      {news.length === 0 ? (
        <p>No news available.</p>
      ) : (
        <ul className="space-y-2">
          {news.map((news, index) => (
            <li key={index} className="p-2 border-b dark:border-gray-600 border-gray-200 rounded">
              <h3>{news.title}</h3>
              <p>{news.description}</p>
            </li>
          ))}
        </ul>
      )}
      <h2 className="text-xl font-semibold mb-4">Events</h2>
      {events.length === 0 ? (
        <p>No events available.</p>
      ) : (
        <ul className="space-y-2">
          {events.map((event, index) => (
            <li key={index} className="p-2 border-b dark:border-gray-600 border-gray-200 rounded">
              <h3>{event.title}</h3>
              <p>{event.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
          