"use client"

import { useEffect, useState } from 'react'
import { fetchEvents } from '../../lib/api'
import Results from '../../components/Results'
import React from 'react'

type EventItem = {
    id: string;
    title: string;
    description: string;
    type: string;
}

export default function EventsPage() {
    const [events, setEvents] = useState<EventItem[]>([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchEvents()
        .then(setEvents)
        .catch((err) => console.error("Error fetching events:", err))
        .finally(() => setLoading(false));
    }, []);

  if (loading) return <div>Loading...</div>;
    
  return (
    <div className='max-w-6xl mx-auto p-3 space-y-4'>
        <h2 className='text-2xl font-bold mb-6'>Latest Events</h2>
        <Results results={events}/>
    </div>
  )
}
