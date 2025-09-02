"use client"

import { useEffect, useState } from 'react'
import { fetchNews } from '../../lib/api'
import Results from '../../components/Results'
import React from 'react'

type NewsItem = {
    id: string;
    title: string;
    description: string;
    type: string;
} 

export default function NewsPage() {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchNews()
        .then(setNews)
        .catch((err) => console.error("Error fetching news:", err))
        .finally(() => setLoading(false));
    }, []);

  if (loading) return <div>Loading...</div>;
    
  return (
    <div className='max-w-6xl mx-auto p-3 space-y-4'>
        <h2 className='text-2xl font-bold mb-6'>Latest News</h2>
        <Results results={news}/>
    </div>
  )
}
