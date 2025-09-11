import React from "react";
import Link from "next/link";
import Image from "next/image";

type ResultItem = {
  id: string;
  title: string;
  description: string;
  url?: string;
  image?: string | null;
  map_image?: string | null;
  type?: string;
};

export default function Card({ result }: { result: ResultItem }) {
  const imgSrc = result.image || result.map_image || "/placeholder.jpg";
  return (
    <div className="group cursor-pointer p-2 border-b dark:border-orange-600 border-gray-500 shadow-sm hover:shadow-gray-500 hover:shadow-lg dark:shadow-lg dark:hover:shadow-orange-500 transition-shadow rounded-lg">
      <Link href={result.url || "#"} target="_blank" rel="noopener noreferrer">
        <Image
          src={imgSrc} 
          alt={result.title}
          width={500}
          height={300}
          className="sm:rounded-t-lg object-cover w-full h-48"
        />
        <div className="p-2">
          <h2 className="text-lg font-semibold mb-1 line-clamp-2">
            {result.title}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
            {result.description}
          </p>
          {result.type && (
            <span className="inline-block mt-2 text-xs font-medium px-2 py-1 bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-200 rounded">
              {result.type}
            </span>
          )}
        </div>
      </Link>
    </div>
  );
}
