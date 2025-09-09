"use client"

import React, { useEffect } from 'react'

type ErrorProps = {
    error: Error;
    reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
    useEffect(() => {
        console.log(error);
    }, [error]);
  return (
    <div className='text-center mt-10'>
        <h1>Something went wrong</h1>
        <button className='hover:text-orange-500' onClick={() => reset()}>Try again</button> 
    </div>
  )
}
