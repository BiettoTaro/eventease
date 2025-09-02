"use client"
import Link from 'next/link'
import React from 'react'
import { useSearchParams } from 'next/navigation';

interface NavbarItemProps {
    title: string;
    address: string;
    param: string;
}

export default function NavbarItem({title, address, param}: NavbarItemProps) {
    const searchParams = useSearchParams();
    const type = searchParams.get("type");

  return (
    <div>
        <Link className={`hover:text-white dark:hover:text-orange-500 font-semibold
         ${type === param ? 'underline underline-offset-8 decoration-4 dark:decoration-orange-500 decoration-gray-900 rounded-lg' : 
            ''}`} 
        href={`/?type=${param}`}>{title}</Link>
    </div>
  )
}
