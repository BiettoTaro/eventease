import React from 'react'

export default function About() {
  return (
    <div className='max-w-6xl mx-auto p-3 space-y-4'>
        <h1 className='text-2xl font-medium text-orange-600'>About</h1>
        <p>We are three university students – led by our project leader Fabio Soggia, with the support of Marco De
           Rinaldis and Andrei Murug – developing EventEase, an academic project aimed at tech-oriented
            university students who want to stay updated and connected.
        </p>
        <p>Our original idea was to combine two worlds: technology news and live events.
           At first, we explored different APIs, such as Eventbrite, to source event-related content.
            However, as Eventbrite no longer provides event data through its API, we had to adapt.
             For the events, we turned to the Ticketmaster API, which offers a reliable stream of concerts,
              sports, and cultural activities in different locations. For the news, we integrated HackerNews
               and TechCrunch APIs, focusing entirely on technology – the core interest of our target audience.
        </p>
        <p>The result is a platform that merges tech news and event discovery in one place,
           creating a unique experience for students passionate about technology and social engagement.
            Built with a modern stack – Next.js + TailwindCSS (frontend), FastAPI (Python) (backend),
            PostgreSQL (database), and Docker (containerisation).
            EventEase showcases how teamwork and creativity can turn an academic project into a meaningful product.
        </p>

    </div>
  )
}
