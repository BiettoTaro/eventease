import React from 'react'

type ResultItem = {
    id: string;
    title: string;
    description: string;
    type: string;
}

export default function Results({results}: {results: ResultItem[]}) {
  return (
    <div>
        {results.map((result, index) => (
            <div key={index} className='p-2 border-b dark:border-gray-600 border-gray-200 rounded'>
                <h2>{result.title}</h2>
                <p>{result.description}</p>
                <p>{result.type}</p>
            </div>
        ))}
    </div>
  )
}
