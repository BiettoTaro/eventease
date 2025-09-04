import React from 'react'
import Link from 'next/link'
import Image from 'next/image'

type NewsListItemProps = {
    id: string;
    title: string;
    description: string;
    url?: string;
    topic?: string;
    image?: string | null;
    source?: string;
}

export default function NewsListItem({news}: {news: NewsListItemProps}) {
  return (
    <Link href={news.url || "#"} target="_blank" rel="noopener noreferrer"
    className='flex items-start gap-4 p-3 border-b dark:border-gray-700 hover:bg-orange-50 
    dark:hover:bg-orange-900 transition'>
        <div className='flex-shrink-0'>
            <Image
            src={news.image || "/placeholder-news.jpg"}
            alt={news.title}
            width={100}
            height={100}
            className='rounded object-cover w-24 h-24'
            />
        </div>
        {/* Content */}
        <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                {news.topic ? (
                    <span className="text-xs bg-orange-600 text-white px-2 py-1 rounded">
                    {news.topic}
                    </span>
                ) : (
                    <span className="text-xs bg-gray-600 text-white px-2 py-1 rounded">
                    {news.source}
                    </span>
                )}
                </div>

                <h3 className="font-semibold text-lg mb-1">{news.title}</h3>
                <p className="text-sm text-gray-400 line-clamp-2">{news.description}</p>
            </div>
            </Link>
        );
}
