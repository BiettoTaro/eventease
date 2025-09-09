import React from 'react'
import Image from 'next/image'

export default function Spinner({size = 300}: {size?: number}) {
  return (
    <div className='flex justify-center pt-32'>
        <Image src="/spinner.svg" alt="loading..." width={size} height={size} />
    </div>
  )
}
