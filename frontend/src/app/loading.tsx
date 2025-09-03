import React from 'react'
import Image from 'next/image'

export default function Spinner({size = 50}: {size?: number}) {
  return (
    <div className='flex justify-center'>
        <Image src="/spinner.svg" alt="loading..." width={size} height={size} />
    </div>
  )
}
