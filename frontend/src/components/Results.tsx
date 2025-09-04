import React from "react";
import Card from "./Card";
import NewsListItem from "./NewsListItem";

type ResultItem = {
  id: string;
  title: string;
  description: string;
  url?: string;
  topic?: string;
  image?: string | null;
  source?: string;
  type?: string; 
};

export default function Results({ results }: { results: ResultItem[] }) {
  if (!results || results.length === 0) {
    return <p className="text-center text-gray-500">No results found.</p>;
  }

  // Detect if results are news (if first item has type === "news" or source field)
  const looksLikeNews = (item: ResultItem) =>
    !!(item.topic || item.source) && !item.type; 

  const isNews = looksLikeNews(results[0]);

  if (isNews) {
    // List layout for news
    return (
      <div className="max-w-4xl mx-auto">
        {results.map((news) => (
          <NewsListItem key={news.id} news={news} />
        ))}
      </div>
    );
  }

  // Grid layout for events
  return (
    <div
      className="sm:grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5
      max-w-6xl mx-auto p-3 gap-4"
    >
      {results.map((result) => (
        <Card key={result.id} result={result} />
      ))}
    </div>
  );
}
