"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Results from "../../../components/Results";
import { fetchNews } from "../../../lib/api";
import { NewsItem } from "../../../lib/types";
import { useRouter, useSearchParams } from "next/navigation";

export const dynamic = "force-dynamic";


export default function NewsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [news, setNews] = useState<NewsItem[]>([]);
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

    const loadNews = async () => {
      try {
        const { items, total: newsTotal } = await fetchNews(undefined, offset, limit);
        setNews(items);
        setTotal(newsTotal);
      } catch (err) {
        console.error("Error fetching news:", err);
      } finally {
        setLoading(false);
      }
    };

    loadNews();
  }, [offset, limit, router]);

  if (loading) return <p className="p-10">Loading news...</p>;

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
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded"
              >
                Previous
              </Link>
            ) : (
              <span />
            )}

            {hasNext && (
              <Link
                href={`/news?offset=${offset + limit}&limit=${limit}`}
                className="px-4 py-2 bg-transparent hover:text-orange-500 dark:text-white rounded"
              >
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
