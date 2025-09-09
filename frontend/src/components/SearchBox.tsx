"use client";
import React, { useState } from 'react'
import { useRouter } from 'next/navigation';


export default function SearchBox() {
    const [search, setSearch] = useState("");
    const router = useRouter();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        router.push(`/search/${encodeURIComponent(search).trim()}`);
    };
  return (
    <form className="flex justify-between px-5 max-w-6xl mx-auto"
    onSubmit={handleSubmit}>
        <input type="text" placeholder="Search keywords..."
        className="w-full h-14 rounded-md placeholder:text-gray-500 outline-none bg-transparent
        flex-1" 
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        />
        <button className="text-orange-600 disabled:text-gray-400" disabled={search === ""}>Search</button>
    </form>
  )
}
