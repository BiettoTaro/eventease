import Results from "../../../components/Results";
import { fetchNews, fetchEvents } from "../../../lib/api";

type SearchPageProps = {
    params: {
        query: string;
    };
};

export default async function SearchPage({ params }: SearchPageProps) {
    const resolvedParams = await params;
    const query  = decodeURIComponent(resolvedParams.query);

    let news = [];
    let events = [];
    
    try {
        [news, events] = await Promise.all([
            fetchNews(query),
            fetchEvents(query)
        ]);
    } catch (err) {
        console.error("Search fetch error:", err);
    }

    return (
        <div className="max-w-6xl mx-auto p-3 space-y-8">
            <h2 className="text-2xl font-bold">Search results for &quot;{query}&quot;</h2>

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