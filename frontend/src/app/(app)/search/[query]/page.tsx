import Results from "../../../../components/Results";
import { fetchNews, fetchEvents } from "../../../../lib/api";
import { NewsItem, EventItem } from "../../../../lib/types";


type SearchPageProps = {
  params: {
    query: string;
  };
};

export default async function SearchPage({ params }: SearchPageProps) {
  const query = decodeURIComponent(params.query);

  let news: NewsItem[] = [];
  let events: EventItem[] = [];

  try {
    const [newsResponse, eventsResponse] = await Promise.all([
      fetchNews(query),
      fetchEvents(query),
    ]);

    news = newsResponse.items as NewsItem[];
    events = eventsResponse.items as EventItem[];
  } catch (err) {
    console.error("Search fetch error:", err);
  }

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-8">
      <h2 className="text-2xl font-bold">
        Search results for &quot;{query}&quot;
      </h2>

      <section>
        <h3 className="text-lg font-semibold mb-4">News</h3>
        {news.length > 0 ? (
          <Results results={news} />
        ) : (
          <p>No news found.</p>
        )}
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-4">Events</h3>
        {events.length > 0 ? (
          <Results results={events} />
        ) : (
          <p>No events found.</p>
        )}
      </section>
    </div>
  );
}
