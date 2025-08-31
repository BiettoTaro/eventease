import React from 'react'
import Link from 'next/link'
import { IconType } from 'react-icons'

type HeaderItemProps = {
    title: string;
    address: string;
    Icon: IconType;
}

export default function HeaderItem({title, address, Icon}: HeaderItemProps) {
  return (
    <Link href={address} className='hover:text-orange-500'>
        <Icon className="text-2xl sm:hidden"/>
        <p className="uppercase hidden sm:inline text-sm">{title}</p>
    </Link>
  )
}
