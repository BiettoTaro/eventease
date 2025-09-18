import React from 'react'

export default function About() {
  return (
    <div className='max-w-6xl mx-auto p-3 space-y-4'>
        <h1 className='text-2xl font-medium text-orange-600'>About</h1>
        <p>We are three university students – led by our project leader Fabio Soggia, with the support of Marco De
           Rinaldis and Andrei Murug – developing EventEase, an academic project aimed at tech-oriented
            university students who want to stay updated and connected.
        </p>
        <p> From the beginning, our vision for EventEase was to create a platform dedicated to 
          technology – combining <strong>tech news</strong> with <strong>tech-related events </strong>  
           in one place. While exploring different providers, we found that many APIs, such as
           Eventbrite, no longer offered free access to event data. To stay aligned with our original 
           idea, we adopted <strong>SearchApi.io (Google Events)</strong>, which allowed us to
            prioritise <em>technology-focused events and articles</em> that truly matched the needs
             of our student audience. 
        </p>
        <p> To ensure the platform remains engaging even when local tech events are limited,
           we added the <strong>Ticketmaster API</strong> as a fallback source. These results
          (concerts, sports, theatre) are always shown last, keeping the focus on technology
          while providing extra variety when needed.
        </p>
        <p> For news, we also use <strong>SearchApi.io</strong> to pull in curated technology stories
         from trusted sources, creating a single hub for staying up to date with both innovations
          and opportunities to engage in real-world activities. 
        </p>
        <p> Built with a modern stack – <strong>Next.js + TailwindCSS</strong> (frontend), 
        <strong>FastAPI (Python)</strong> (backend), <strong>PostgreSQL</strong> (database), and
         <strong>Docker</strong> (for consistency across environments) – EventEase stays true to 
         its mission: <em>a tech-first discovery platform that blends knowledge with community</em>.
        </p>
        <p> We are currently working on adding more features to EventEase, such as user profiles,
         event planning tools, and a community forum. We are also working on adding more APIs to
          the platform to provide a more diverse range of events and news. </p>
                

    </div>
  )
}
