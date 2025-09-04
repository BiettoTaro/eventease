import Results from "../../components/Results";
import { fetchNews } from "../../lib/api";

type NewsItem = {
  id: string;
  title: string;
  description: string;
  image?: string | null;
  topic?: string;
  url?: string;
  source?: string;
};

export default async function NewsPage() {
  let news: NewsItem[] = [];

  try {
    const rawNews = await fetchNews();
    // Ensure type is always "news"
    news = rawNews.map((item: NewsItem, index: number) => ({
      id: item.id || String(index),
      title: item.title,
      description: item.description || "",
      image: item.image || null,
      url: item.url,
      topic: item.topic,
    }));
    
  } catch (err) {
    console.error("Error fetching news:", err);
    return (
      <div className="p-10 text-center text-red-500">
        Could not load news right now.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-3 space-y-4">
      <h2 className="text-2xl font-bold mb-6">Latest News</h2>
      {news.length > 0 ? (
        <Results results={news} />
      ) : (
        <p>No news available.</p>
      )}
    </div>
  );
}
