import Link from "next/link";
import Results from "../../components/Results";
import { fetchNews } from "../../lib/api";
export const dynamic = "force-dynamic";

type NewsItem = {
  id: string;
  title: string;
  description: string;
  image?: string | null;
  topic?: string;
  url?: string;
  source?: string;
};

type NewsPageProps = {
  searchParams: {
    offset?: string;
    limit?: string;
  }
}

export default async function NewsPage({ searchParams }: NewsPageProps) {
  const offset = parseInt(searchParams?.offset || "0", 10);
  const limit = parseInt(searchParams?.limit || "10", 10);

  let news: NewsItem[] = [];
  let total = 0;

  try {
    const {items, total:newsTotal} = await fetchNews(undefined, offset, limit);
    total = newsTotal;
    // Ensure type is always "news"
    news = items.map((item: NewsItem, index: number) => ({
      id: item.id || String(index),
      title: item.title,
      description: item.description || "",
      image: item.image || null,
      url: item.url,
      topic: item.topic,
      source: item.source,
    }));
    
  } catch (err) {
    console.error("Error fetching news:", err);
    return (
      <div className="p-10 text-center text-red-500">
        Could not load news right now.
      </div>
    );
  }

  const hasPrev = offset > 0;
  const hasNext = offset + limit < total;

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-4">
      <h2 className="text-2xl font-bold mb-6">Latest News</h2>
      {news.length > 0 ? (
        <>
          <Results results={news} />
          <div className="flex justify-between mt-6">
            {hasPrev ? (
              <Link
                href={`/news?offset=${Math.max(offset - limit, 0)}&limit=${limit}`}
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
                  Previous
                </Link>
            ) : (
              <span />
            )}

            {hasNext &&(
              <Link
                href={`/news?offset=${offset + limit}&limit=${limit}`}
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded">
                  Next
              </Link>
            )}
          </div>
        </>
      ) : (
        <p>No news available.</p>
      )}
    </div>
  );
}
